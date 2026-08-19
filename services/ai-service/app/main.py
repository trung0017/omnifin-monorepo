from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from app.services.qdrant_manager import qdrant_manager

from app.core.config import settings
from app.services.qdrant_manager import qdrant_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # [Warm-up Phase] Thiết lập kết nối cơ sở dữ liệu Vector ngay khi bật máy chủ
    qdrant_manager.init_client()
    yield
    # [Shutdown Phase] Giải phóng tài nguyên hệ thống an toàn
    await qdrant_manager.close_client()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", tags=["Infrastructure"])
async def health_check():
    """Endpoint kiểm tra liên thông hạ tầng toàn diện phục vụ DevOps/Docker Healthcheck"""
    start_time = time.time()
    is_qdrant_healthy = await qdrant_manager.check_health()
    latency_ms = (time.time() - start_time) * 1000

    status_code = status.HTTP_200_OK if is_qdrant_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if is_qdrant_healthy else "unhealthy",
            "service": settings.PROJECT_NAME,
            "timestamp": "Aug 19, 2026, 8:04 AM",
            "dependencies": {
                "qdrant_vector_db": "connected" if is_qdrant_healthy else "disconnected"
            },
            "performance": {
                "latency": f"{latency_ms:.2f}ms"
            }
        }
    )

@app.get("/v1/ai/knowledge-status", tags=["Knowledge Base"])
async def get_knowledge_status():
    """Kiểm tra số lượng phân đoạn tri thức đã được nạp vào hệ thống"""
    if not qdrant_manager.client:
        return JSONResponse(status_code=500, content={"status": "error", "message": "Qdrant Client chưa được khởi tạo."})
        
    try:
        collection_info = await qdrant_manager.client.get_collection(collection_name="omnifin_knowledge_base")
        return {
            "collection_name": "omnifin_knowledge_base",
            "status": collection_info.status.value,
            "vectors_count": collection_info.vectors_count,
            "points_count": collection_info.points_count,
            "indexed_vectors_count": collection_info.indexed_vectors_count
        }
    except Exception as e:
        return JSONResponse(
            status_code=404,
            content={"status": "not_found", "message": f"Bộ cơ sở tri thức chưa được khởi tạo hoặc trống: {str(e)}"}
        )