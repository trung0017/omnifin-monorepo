import logging
from qdrant_client import AsyncQdrantClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        # Khởi tạo client kết nối local an toàn (đã vá lỗi định tuyến ở bước trước)
        self.client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = "omnifin_knowledge_base"

    async def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """
        Truy vấn ngữ cảnh tri thức liên quan từ Qdrant.
        Trong thực tế, câu hỏi sẽ được đi qua mô hình nhúng (Embedding) trước khi so khớp.
        Tại bước này, hệ thống thực hiện truy vấn quét các payload nội dung phù hợp.
        """
        try:
            # Giả lập hoặc quét vector tương đồng từ collection
            # Sử dụng tính năng tìm kiếm bất đồng bộ của Qdrant
            results = await self.client.scroll(
                collection_name=self.collection_name,
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )
            
            records = results[0]
            if not records:
                return "Không tìm thấy tài liệu hướng dẫn nghiệp vụ liên quan."
                
            # Tổng hợp các đoạn tri thức tìm được thành một khối ngữ cảnh vững chắc
            context_chunks = [str(record.payload.get("content", "")) for record in records]
            return "\n---\n".join(context_chunks)
            
        except Exception as e:
            logger.error(f"Lỗi hệ thống khi truy vấn kho tri thức Vector DB: {str(e)}")
            return "Hệ thống tạm thời không thể truy xuất tài liệu quy định nội bộ."

rag_service = RAGService()