import asyncio
import json
import random
import uuid
import logging
from datetime import datetime
from aiokafka import AIOKafkaProducer
from faker import Faker

# Cấu hình log giám sát hiệu năng
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MockDataGenerator")

# Cấu hình kết nối hạ tầng
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TRANSACTION_TOPIC = "financial_transactions"

# Khởi tạo công cụ tạo dữ liệu giả lập tiếng Anh/Việt
fake = Faker()

def generate_random_transaction() -> dict:
    """Tạo cấu trúc một bản ghi sự kiện giao dịch tài chính ngẫu nhiên chuẩn doanh nghiệp"""
    return {
        "transaction_id": str(uuid.uuid4()),
        "account_number": fake.bban(),  # Sinh số tài khoản ngân hàng ngẫu nhiên
        "sender_name": fake.name(),
        "amount": round(random.uniform(50000, 50000000), 2),  # Giao dịch từ 50k đến 50 triệu
        "currency": "VND",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "location": random.choice(["Hanoi", "Ho Chi Minh City", "Da Nang", "Unknown"]),
        "device_ip": fake.ipv4()
    }

async def run_generator():
    """Vòng lặp bất đồng bộ sinh dữ liệu thông lượng cao pushing vào Kafka"""
    logger.info(f"Đang thiết lập kết nối tới Kafka Broker: {KAFKA_BOOTSTRAP_SERVERS}...")
    
    # Khởi tạo Producer với cấu hình tối ưu hóa thông lượng (Batching)
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        acks=1,  # Đảm bảo broker nhận được gói tin để tối ưu tốc độ
        compression_type="gzip"  # Nén dữ liệu truyền tải trên mạng nội bộ
    )
    
    try:
        await producer.start()
        logger.info(f"Kết nối thành công! Bắt đầu đẩy luồng dữ liệu giả lập vào Topic [{TRANSACTION_TOPIC}]...")
        
        count = 0
        while True:
            # Sinh 1 giao dịch ngẫu nhiên
            tx_data = generate_random_transaction()
            
            # Đóng gói dữ liệu sang Bytes JSON
            payload = json.dumps(tx_data).encode('utf-8')
            
            # Gửi bất đồng bộ (không block vòng lặp tiếp theo)
            await producer.send(
                topic=TRANSACTION_TOPIC,
                key=tx_data["transaction_id"].encode('utf-8'),
                value=payload
            )
            
            count += 1
            if count % 100 == 0:
                logger.info(f"Hệ thống vận hành ổn định: Đã đẩy thành công {count} sự kiện giao dịch vào hàng đợi.")
            
            # Giờ nghỉ cực ngắn giữa các gói tin để điều tiết thông lượng (ví dụ: 0.01s ~ 100 TPS)
            # Muốn nâng lên tốc độ tối đa có thể giảm thời gian sleep xuống hoặc bỏ hẳn
            await asyncio.sleep(0.01)
            
    except asyncio.CancelledError:
        logger.warning("Vòng lặp sinh dữ liệu bị dừng theo yêu cầu của lập trình viên.")
    except Exception as e:
        logger.error(f"Lỗi hệ thống trong quá trình đẩy luồng dữ liệu: {str(e)}")
    finally:
        await producer.stop()
        logger.info("Đã ngắt kết nối an toàn với Kafka Broker.")

if __name__ == "__main__":
    try:
        asyncio.run(run_generator())
    except KeyboardInterrupt:
        logger.info("Đã tắt script kiểm thử chủ động qua phím tắt Terminal.")