import logging
from qdrant_client import AsyncQdrantClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class QdrantManager:
    def __init__(self):
        self.client: AsyncQdrantClient = None

    def init_client(self):
        """Khởi tạo Client bất đồng bộ kết nối tới Qdrant Vector DB"""
        if not self.client:
            self.client = AsyncQdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                check_compatibility=False
            )
            logger.info(f"Kênh kết nối AsyncQdrantClient được thiết lập: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")

    async def close_client(self):
        """Đóng an toàn luồng kết nối khi tắt dịch vụ"""
        if self.client:
            await self.client.close()
            logger.info("Đã đóng luồng kết nối AsyncQdrantClient an toàn.")
            self.client = None

    async def check_health(self) -> bool:
        """Kiểm tra trạng thái liên thông mạng thực tế tới cụm Qdrant cluster"""
        if not self.client:
            return False
        try:
            # Gọi lệnh kiểm tra cụm cluster (Giao thức gRPC/REST ngầm định)
            await self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Thất bại khi kết nối kiểm tra trạng thái tới Qdrant: {str(e)}")
            return False

# Khởi tạo instance toàn cục phục vụ cơ chế nhúng Dependency Injection
qdrant_manager = QdrantManager()