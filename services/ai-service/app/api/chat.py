import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.rag_service import rag_service
from app.services.vision_service import vision_service

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Các mô hình dữ liệu (Pydantic Models) ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    context_used: str

# --- 1. Endpoint REST Chat truyền thống ---
@router.post("/chat", response_model=ChatResponse, tags=["AI Assistant"])
async def standard_chat(request: ChatRequest):
    """Endpoint REST truyền thống - Trả về toàn bộ câu trả lời cùng một lúc dựa trên kho tri thức"""
    # Truy xuất dữ liệu nền từ Qdrant Vector DB
    context = await rag_service.retrieve_context(query=request.message)
    
    # Tổng hợp câu trả lời
    answer = f"Dựa trên tài liệu quy định nội bộ thu thập được:\n{context}\n\nOmniFin phản hồi: Hệ thống ghi nhận yêu cầu và khuyến nghị tuân thủ đúng hạn mức giao dịch."
    
    return ChatResponse(answer=answer, context_used=context)

# --- 2. Cổng WebSocket Chat thời gian thực (Streaming) ---
@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """Cổng kết nối WebSocket thời gian thực - Đẩy câu trả lời động dựa trên kho tri thức"""
    await websocket.accept()
    try:
        while True:
            # 1. Tiếp nhận tin nhắn thực tế gửi lên từ khung chat ứng dụng di động
            user_query = await websocket.receive_text()
            
            # Gửi trạng thái thông báo cho Client Layer biết hệ thống bắt đầu quét dữ liệu
            await websocket.send_json({"type": "status", "content": "Đang truy xuất kho tri thức Qdrant..."})
            
            # 2. Truy xuất dữ liệu văn bản nền tảng thực tế từ Qdrant Vector DB dựa trên câu hỏi
            context = await rag_service.retrieve_context(query=user_query)
            await asyncio.sleep(0.2)
            
            # 3. Tổng hợp câu trả lời động (Thay thế cho chuỗi text cố định trước đây)
            # Trong thực tế mốc tuần 11, khối văn bản 'context' này sẽ được đẩy vào mô hình LLM.
            if "2345" in user_query or "hạn mức" in user_query.lower() or "sinh trắc" in user_query.lower():
                dynamic_reply = f" Trợ lý AI OmniFin phản hồi dựa trên tài liệu nội bộ: {context} \n\nKhuyến nghị: Tài khoản của bạn cần hoàn tất quét phôi thẻ CCCD gắn chip để không bị gián đoạn giao dịch."
            else:
                dynamic_reply = f"Hệ thống đã nhận được câu hỏi: '{user_query}'. Dựa trên tài liệu quy định nội bộ thu thập được:\n{context}\n\nOmniFin Assistant luôn sẵn sàng hỗ trợ bạn tối ưu hóa nghiệp vụ tài chính."

            await websocket.send_json({"type": "status", "content": "Trợ lý AI đang trả lời..."})
            
            # 4. Cắt nhỏ câu trả lời động thành từng cụm từ để đẩy cuốn chiếu (Streaming) về Mobile App
            tokens = dynamic_reply.split(" ")
            for token in tokens:
                await websocket.send_json({
                    "type": "token",
                    "content": token + " "
                })
                await asyncio.sleep(0.06) # Tốc độ đẩy token mượt mà
                
            # Gửi tín hiệu báo hiệu kết thúc luồng truyền dữ liệu (End of Stream)
            await websocket.send_json({"type": "end", "content": ""})
            
    except WebSocketDisconnect:
        logger.info("Client di động đã ngắt kết nối WebSocket.")
    except Exception as e:
        logger.error(f"Lỗi hệ thống trong phiên WebSocket: {str(e)}")
        await websocket.close()
        
# --- 3. Endpoint Đa mô thức Vision AI ---
@router.post("/ai/vision-analyze", tags=["AI Assistant"])
async def vision_analyze_endpoint(file: UploadFile = File(...)):
    """
    Endpoint tiếp nhận dữ liệu ảnh Form đa phần (Multipart Form)
    để nhận diện biên lai lỗi hoặc lỗi hệ thống.
    """
    try:
        # Đọc luồng dữ liệu nhị phân trực tiếp từ Client
        image_bytes = await file.read()
        
        # Đẩy vào lõi xử lý thị giác máy tính bất đồng bộ trên RAM
        analysis_result = await vision_service.analyze_image_stream(image_bytes)
        
        if analysis_result["status"] == "error":
            return JSONResponse(status_code=400, content=analysis_result)
            
        extracted_data = analysis_result["extracted_content"]
        ai_interpretation = f"Trợ lý ảo OmniFin đã nhận diện ảnh thuộc nhóm [{analysis_result['classification']}]. Hệ thống phân tích nội dung: {extracted_data}"
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "metadata": analysis_result["image_metadata"],
            "classification": analysis_result["classification"],
            "ai_response": ai_interpretation
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Lỗi xử lý tệp tin: {str(e)}"}
        )