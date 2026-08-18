from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from app.core.config import settings

# Khởi tạo Engine bất đồng bộ kết nối tới Postgres
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Khởi tạo xưởng tạo Session bất đồng bộ
async_session_local = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependency cung cấp session cho các API endpoint (Chốt chặn bẫy lỗi từ đầu)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_local() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()