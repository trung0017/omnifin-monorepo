from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db

app = FastAPI(
    title="OmniFin Enterprise - Identity & eKYC Service",
    version="1.0.0",
    description="Dịch vụ định danh lõi và xử lý sinh trắc học cấp độ Doanh nghiệp"
)

@app.get("/health", tags=["Health Check"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Endpoint kiểm tra trạng thái hoạt động của Service và kết nối Database trực tiếp
    """
    try:
        # Kiểm tra nhanh kết nối bằng một câu lệnh thuần độc lập
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