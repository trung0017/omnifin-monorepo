import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import easyocr
from ultralytics import YOLO
from deepface import DeepFace

from app.core.database import get_db
from app.api import ekyc

# Cấu hình log giám sát hiệu năng hệ thống
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IdentityOptimization")

# Khởi tạo các biến global giữ thực thể mô hình trong bộ nhớ
models_pool = {
    "ocr": None,
    "yolo": None
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Cơ chế tối ưu hóa doanh nghiệp: Nạp trước trọng số mô hình (Model Warm-up)
    ngay khi khởi động dịch vụ để ép thời gian phản hồi Request xuống < 2 giây.
    """
    logger.info("[WARM-UP] Bắt đầu nạp hệ thống mô hình trí tuệ nhân tạo vào RAM...")
    
    try:
        # 1. Khởi tạo và nạp trước EasyOCR Engine
        models_pool["ocr"] = easyocr.Reader(['vi', 'en'], gpu=False)
        logger.info("[WARM-UP] Đã cấu hình và nạp thành công bộ thư viện EasyOCR.")

        # 2. Khởi tạo và nạp trước YOLOv8-Nano
        models_pool["yolo"] = YOLO("yolov8n.pt")
        logger.info("[WARM-UP] Đã cấu hình và nạp thành công bộ thư viện YOLOv8.")

        # 3. Kích hoạt kích nổ (Warm-up) DeepFace ArcFace
        # Gọi một lệnh xác thực giả lập cực nhẹ để ép thư viện dựng sẵn cấu trúc mạng trong Keras
        logger.info("[WARM-UP] Đang kích nổ ma trận mạng sinh trắc học ArcFace...")
        DeepFace.build_model("ArcFace")
        logger.info("[WARM-UP] Đã cấu hình và định hình thành công bộ thư viện ArcFace.")
        
        logger.info("[WARM-UP] Toàn bộ hệ thống mô hình AI đã sẵn sàng hoạt động với hiệu năng tối ưu!")
    except Exception as e:
        logger.error(f"[WARM-UP] Thất bại trong quá trình tối ưu hóa khởi động: {str(e)}")
    
    yield
    
    # Giải phóng tài nguyên nếu cần thiết khi tắt server
    models_pool.clear()
    logger.info("Đã giải phóng an toàn vùng tài nguyên hệ thống mô hình.")

app = FastAPI(
    title="OmniFin Enterprise - Identity & eKYC Service",
    version="1.0.0",
    description="Dịch vụ định danh lõi, xử lý sinh trắc học & Tối ưu hóa hiệu năng",
    lifespan=lifespan
)

# Đăng ký các tuyến đường API eKYC Động cơ AI
app.include_router(ekyc.router)

@app.get("/health", tags=["Health Check"])
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "service": "identity-service"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }