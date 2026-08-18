from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.api import ekyc  # Import module ekyc mới tạo

app = FastAPI(
    title="OmniFin Enterprise - Identity & eKYC Service",
    version="1.0.0",
    description="Dịch vụ định danh lõi và xử lý sinh trắc học cấp độ Doanh nghiệp"
)

# Đăng ký các tuyến đường API eKYC Đông cơ AI
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