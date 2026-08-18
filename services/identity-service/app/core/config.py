import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Cấu hình lấy từ biến môi trường hoặc dùng giá trị mặc định của Docker hạ tầng
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://omnifin_user:omnifin_secure_password@localhost:5432/omnifin_db"
    )

settings = Settings()