import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel
from app.services.rag_service import rag_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    context_used: str

@router.post("/chat", response_model=ChatResponse, tags=["AI Assistant"])
async def standard_chat(request: ChatRequest):
    """Endpoint REST truyền thống - Trả về toàn bộ câu trả lời cùng một lúc"""
    # 1. Truy xuất dữ liệu nền tảng từ Qdrant Vector DB
    context = await rag_service.retrieve_context(query=request.message)
    
    # 2. Giả lập luồng tư duy và tổng hợp câu trả lời từ mô hình LLM dựa trên ngữ cảnh
    answer = f"Dựa trên tài liệu quy định nội bộ thu thập được:\n{context}\n\nOmniFin phản hồi: Hệ thống ghi nhận yêu cầu và khuyến nghị tuân thủ đúng hạn mức giao dịch."
    
    return ChatResponse(answer=answer, context_used=context)


@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """Cổng kết nối WebSocket thời gian thực - Đẩy dữ liệu dạng Token Streaming cuốn chiếu"""
    # Chấp nhận phiên kết nối từ Client Layer (Mobile App / Web Admin)
    await websocket.accept()
    try:
        while True:
            # Tiếp nhận tin nhắn dạng text gửi lên từ client
            data = await websocket.receive_text()
            
            # 1. Khai thác dữ liệu tri thức ngầm định
            context = await rag_service.retrieve_context(query=data)
            
            # Gửi tín hiệu thông báo cho Client biết hệ thống bắt đầu sinh câu trả lời
            await websocket.send_json({"type": "status", "content": "Đang phân tích tri thức..."})
            await asyncio.sleep(0.5) # Tạo độ trễ tự nhiên cho luồng I/O
            
            # 2. Giả lập luồng dữ liệu Streaming từ Mô hình ngôn ngữ lớn (LLM Engine)
            base_reply = f"Hệ thống phản hồi dựa trên Quyết định 2345/QĐ-NHNN: Mọi giao dịch chuyển tiền trên 10 triệu đồng của bạn bắt buộc phải quét sinh trắc học khuôn mặt trùng khớp với thẻ căn cước công dân gắn chip để phòng chống gian lận. Hệ thống đang bảo vệ tài khoản của bạn."
            
            # Cắt nhỏ câu trả lời thành từng cụm từ (Tokens) để đẩy cuốn chiếu về giao diện
            tokens = base_reply.split(" ")
            for token in tokens:
                await websocket.send_json({
                    "type": "token",
                    "content": token + " "
                })
                await asyncio.sleep(0.08) # Ép tốc độ đẩy token mượt mà (~12 tokens/giây)
                
            # Gửi tín hiệu báo hiệu kết thúc luồng truyền dữ liệu (EOS - End of Stream)
            await websocket.send_json({"type": "end", "content": ""})
            
    except WebSocketDisconnect:
        # Xử lý dọn dẹp bộ nhớ hoặc ghi nhận khi client ngắt kết nối đột ngột (tắt app, mất mạng)
        pass