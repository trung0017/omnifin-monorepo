import os
import logging
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KafkaManager")

# Địa chỉ Kafka Broker lấy từ mạng nội bộ Docker hoặc localhost khi chạy thử nghiệm
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TRANSACTION_TOPIC = "financial_transactions"

class KafkaManager:
    def __init__(self):
        self.producer: AIOKafkaProducer = None
        self.consumer: AIOKafkaConsumer = None

    async def start_producer(self):
        """Khởi tạo và cấu hình bẫy lỗi cho Kafka Producer"""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
            )
            await self.producer.start()
            logger.info(f"Kafka Producer khởi chạy thành công kết nối tới {KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            logger.error(f"Lỗi khởi chạy Kafka Producer (Kafka chưa sẵn sàng): {str(e)}")
            self.producer = None

    async def stop_producer(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka Producer đã dừng kết nối.")

    async def send_transaction_event(self, key: str, value: bytes):
        """Gửi sự kiện giao dịch lên Kafka Topic"""
        if not self.producer:
            raise RuntimeError("Producer chưa được khởi tạo thành công.")
        try:
            await self.producer.send_and_wait(TRANSACTION_TOPIC, key=key.encode(), value=value)
            logger.info(f"Đã đẩy sự kiện giao dịch lên Topic [{TRANSACTION_TOPIC}] - Key: {key}")
        except Exception as e:
            logger.error(f"Thất bại khi gửi sự kiện lên Kafka: {str(e)}")

# Khởi tạo một instance dùng chung cho toàn bộ ứng dụng
kafka_manager = KafkaManager()