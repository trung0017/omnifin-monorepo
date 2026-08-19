from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from app.kafka.connection import kafka_manager

# Quản lý vòng đời kết nối hạ tầng (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi chạy Producer khi khởi động server
    await kafka_manager.start_producer()
    yield
    # Dừng kết nối khi tắt server
    await kafka_manager.stop_producer()

app = FastAPI(
    title="OmniFin Enterprise - Transaction Service",
    version="1.0.0",
    description="Dịch vụ xử lý giao dịch tài chính và đóng gói sự kiện phân tán",
    lifespan=lifespan
)

@app.get("/health", tags=["Health Check"])
async def health_check():
    """Endpoint kiểm tra trạng thái liên thông của Transaction Service"""
    return {
        "status": "healthy",
        "service": "transaction-service"
    }

# Khai báo cấu trúc dữ liệu giao dịch đầu vào (Chốt chặn bẫy lỗi dữ liệu)
class TransactionSchema(BaseModel):
    transaction_id: str
    account_number: str
    amount: float
    currency: str = "VND"

@app.post("/v1/transactions", tags=["Transactions"])
async def create_transaction(payload: TransactionSchema):
    """
    Endpoint tiếp nhận giao dịch và tạo sự kiện (Event) đẩy vào Apache Kafka
    """
    try:
        # Chuyển đổi dữ liệu sang định dạng chuỗi JSON mã hóa dạng bytes để truyền qua mạng
        event_data = json.dumps(payload.model_dump()).encode('utf-8')
        
        # Đẩy sự kiện phân tán lên Kafka Broker thông qua Manager
        await kafka_manager.send_transaction_event(
            key=payload.transaction_id, 
            value=event_data
        )
        
        return {
            "status": "success",
            "message": "Sự kiện giao dịch đã được tiếp nhận và phân phối vào luồng sự kiện phân tán.",
            "data": payload
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Hệ thống điều phối sự kiện gặp lỗi: {str(e)}"
        )