import asyncio
import logging
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qdrant_models
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tên Collection lưu trữ tài liệu quy định ngân hàng & eKYC của OmniFin
COLLECTION_NAME = "omnifin_knowledge_base"
VECTOR_SIZE = 384  # Khớp với kích thước đầu ra của mô hình all-MiniLM-L6-v2

async def create_collection_if_not_exists(client: AsyncQdrantClient):
    """Khởi tạo cấu trúc bảng lưu trữ Vector trong Qdrant nếu chưa có"""
    try:
        collections_response = await client.get_collections()
        existing_collections = [c.name for c in collections_response.collections]
        
        if COLLECTION_NAME not in existing_collections:
            logger.info(f"Đang khởi tạo cấu trúc Collection mới: {COLLECTION_NAME}")
            await client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qdrant_models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=qdrant_models.Distance.COSINE # Sử dụng khoảng cách Cosine để tối ưu so khớp ngữ nghĩa
                )
            )
            logger.info(f"Khởi tạo thành công Collection: {COLLECTION_NAME}")
        else:
            logger.info(f"Collection '{COLLECTION_NAME}' đã tồn tại sẵn trên hệ thống.")
    except Exception as e:
        logger.error(f"Lỗi khi cấu hình hệ thống lưu trữ Qdrant: {str(e)}")
        raise

async def mock_embedding_engine(texts: list[str]) -> list[list[float]]:
    """
    Giả lập động cơ nhúng ma trận Vector mật độ cao (Dense Vector) 384 chiều.
    Trong thực tế tuần 11, hàm này sẽ được thay thế bằng HuggingFaceEmbeddings 
    hoặc OllamaEmbeddings chạy cục bộ nạp qua CPU/GPU Mac.
    """
    import random
    # Sinh vector ngẫu nhiên chuẩn hóa để kiểm thử luồng ghi I/O bất đồng bộ
    return [[random.uniform(-1.0, 1.0) for _ in range(VECTOR_SIZE)] for _ in texts]

async def ingest_document_pipeline(file_path: str, raw_text: str):
    """Quy trình băm nhỏ, nhúng vector và đẩy tri thức vào kho dữ liệu"""
    # 1. Khởi tạo kết nối Client cục bộ
    client = AsyncQdrantClient(host="127.0.0.1", port=6333)
    
    try:
        # 2. Đảm bảo bảng lưu trữ đã sẵn sàng
        await create_collection_if_not_exists(client)
        
        # 3. Sử dụng LangChain băm nhỏ văn bản lớn thành từng đoạn (Chunks) bảo toàn ngữ cảnh
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,       # Mỗi đoạn gồm tối đa 600 ký tự
            chunk_overlap=120,     # Gối đầu 120 ký tự giữa các đoạn liền kề để tránh mất ngữ cảnh đường biên
            length_function=len
        )
        
        chunks = text_splitter.split_text(raw_text)
        logger.info(f"Tệp tin [{file_path}] đã được băm nhỏ thành {len(chunks)} phân đoạn tri thức.")
        
        if not chunks:
            logger.warning("Không có dữ liệu văn bản hợp lệ để nạp.")
            return

        # 4. Chuyển đổi các phân đoạn văn bản thành Vector nhúng ngữ nghĩa
        embeddings = await mock_embedding_engine(chunks)
        
        # 5. Đóng gói dữ liệu cấu trúc chuẩn Qdrant Payload
        points = []
        for idx, (chunk_text, vector) in enumerate(zip(chunks, embeddings)):
            points.append(
                qdrant_models.PointStruct(
                    id=idx + 1000, # Định danh số nguyên cho điểm dữ liệu
                    vector=vector,
                    payload={
                        "source_file": file_path,
                        "content": chunk_text,
                        "metadata": {"type": "financial_policy", "ingested_at": "Aug 19, 2026"}
                    }
                )
            )
            
        # 6. Đẩy dữ liệu hàng loạt không chặn (Batch Upload) vào Vector DB
        await client.upsert(
            collection_name=COLLECTION_NAME,
            wait=True,
            points=points
        )
        logger.info(f"Đã đồng bộ an toàn {len(points)} điểm dữ liệu tri thức vào Qdrant.")
        
    finally:
        await client.close()

# Đoạn mã thực thi kiểm thử độc lập nhanh luồng Ingestion
if __name__ == "__main__":
    # Giả lập nội dung văn bản quy định chính sách bảo mật giao dịch eKYC (Quyết định 2345/QĐ-NHNN)
    sample_policy_text = """
    QUYẾT ĐỊNH 2345/QĐ-NHNN CỦA NGÂN HÀNG NHÀ NƯỚC:
    Nhằm đảm bảo an toàn, bảo mật cho các giao dịch thanh toán trực tuyến và thanh toán thẻ ngân hàng,
    tất cả các giao dịch chuyển tiền trực tuyến có giá trị trên 10 triệu đồng hoặc tổng giá trị giao dịch 
    trong ngày vượt quá 20 triệu đồng bắt buộc phải tuân thủ xác thực sinh trắc học khuôn mặt.
    Quy trình xác thực yêu cầu đối chiếu khuôn mặt của người thực hiện giao dịch trùng khớp chính xác 
    với dữ liệu sinh trắc học được lưu trữ trong chip của thẻ Căn cước công dân gắn chip (CCCD).
    Đồng thời hệ thống của các tổ chức tín dụng phải tích hợp công nghệ chống giả mạo thực thể sống (Liveness Detection)
    để ngăn chặn các hành vi gian lận bằng ảnh chụp 2D hoặc video phát lại từ thiết bị ngoại vi.
    """
    
    asyncio.run(ingest_document_pipeline(
        file_path="policies/qd_2345_nhnn.txt", 
        raw_text=sample_policy_text
    ))