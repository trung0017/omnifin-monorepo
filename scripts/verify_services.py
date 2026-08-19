import asyncio
import httpx
import sys

# Danh sách các cổng dịch vụ microservices thực tế trong cấu trúc Monorepo
SERVICES = {
    "Identity & eKYC Service": "http://127.0.0.1:8000/health",
    "Transaction Service": "http://127.0.0.1:8001/health",
    "AI Assistant & RAG Service": "http://127.0.0.1:8002/health",
    "MLflow MLOps Tracking Server": "http://127.0.0.1:5000/"
}

async def check_service_health(name: str, url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            # Mã 200 cho endpoint health hoặc 404 cho gốc rỗng của MLflow đều chứng minh liên thông mạng thành công
            if response.status_code in [200, 404]:
                print(f"✅ [LIÊN THÔNG] {name} đang vận hành ổn định tại địa chỉ: {url}")
                return True
            else:
                print(f"❌ [LỖI HẠ TẦNG] {name} phản hồi với mã trạng thái bất thường: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ [MẤT KẾT NỐI] {name} không phản hồi. Hãy chắc chắn dịch vụ đã được khởi chạy. Chi tiết: {str(e)}")
            return False

async def main():
    print("=== ĐANG QUÉT TRẠNG THÁI TOÀN BỘ HỆ THỐNG OMNIFIN ENTERPRISE ===\n")
    tasks = [check_service_health(name, url) for name, url in SERVICES.items()]
    results = await asyncio.gather(*tasks)
    
    print("\n========================================================")
    if all(results):
        print("🚀 TUYỆT VỜI! Toàn bộ kiến trúc Microservices & MLOps đã thông suốt hoàn toàn!")
    else:
        print("⚠️ CẢNH BÁO: Có một số cấu phần dịch vụ chưa được kích hoạt. Bạn vui lòng kiểm tra lại Terminal.")

if __name__ == "__main__":
    asyncio.run(main())