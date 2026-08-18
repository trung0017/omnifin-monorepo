import os
import cv2
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DataPrep")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CCCD_DIR = os.path.join(BASE_DIR, "data", "sample_cccd")
SELFIE_DIR = os.path.join(BASE_DIR, "data", "sample_selfie")

def create_mock_cccd():
    """Tạo một file ảnh giả lập phôi thẻ CCCD với kích thước và màu sắc tiêu chuẩn"""
    dest_path = os.path.join(CCCD_DIR, "cccd_template_1.jpg")
    if os.path.exists(dest_path):
        return

    logger.info("Đang khởi tạo phôi ảnh CCCD mẫu...")
    # Tạo khung hình nền màu xanh nhạt tiêu chuẩn của thẻ (Kích thước 640x400)
    img = np.full((400, 640, 3), (240, 220, 180), dtype=np.uint8)
    
    # Vẽ giả lập khung viền thẻ
    cv2.rectangle(img, (20, 20), (620, 380), (150, 100, 50), 3)
    
    # Chèn dòng chữ giả lập tiêu đề thẻ
    cv2.putText(img, "CAN CUOC CONG DAN", (180, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    cv2.putText(img, "SO / NO: 012345678901", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(img, "HO TEN / NAME: NGUYEN VAN A", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Vẽ một hình khối đại diện cho vùng chứa ảnh chân dung trên thẻ
    cv2.rectangle(img, (50, 220), (170, 360), (100, 100, 100), -1)
    
    cv2.imwrite(dest_path, img)
    logger.info(f"Đã lưu ảnh CCCD mẫu tại: {dest_path}")

def create_mock_selfie():
    """Tạo một file ảnh chân dung giả lập để phục vụ so khớp khuôn mặt"""
    dest_path = os.path.join(SELFIE_DIR, "selfie_sample_1.jpg")
    if os.path.exists(dest_path):
        return

    logger.info("Đang khởi tạo ảnh chân dung selfie mẫu...")
    # Tạo khung hình nền ảnh chụp (Kích thước 400x400)
    img = np.full((400, 400, 3), (220, 220, 220), dtype=np.uint8)
    
    # Vẽ một hình tròn giả lập khuôn mặt ở trung tâm
    cv2.circle(img, (200, 180), (80), (150, 200, 250), -1)
    # Vẽ đôi mắt giả lập
    cv2.circle(img, (170, 160), (10), (0, 0, 0), -1)
    cv2.circle(img, (230, 160), (10), (0, 0, 0), -1)
    # Vẽ khuôn miệng cười
    cv2.ellipse(img, (200, 210), (30, 15), 0, 0, 180, (0, 0, 255), 3)
    
    cv2.imwrite(dest_path, img)
    logger.info(f"Đã lưu ảnh chân dung mẫu tại: {dest_path}")

def main():
    logger.info("Bắt đầu quy trình khởi tạo dữ liệu mẫu eKYC offline...")
    os.makedirs(CCCD_DIR, exist_ok=True)
    os.makedirs(SELFIE_DIR, exist_ok=True)

    create_mock_cccd()
    create_mock_selfie()
    logger.info("Hoàn tất quy trình chuẩn bị dữ liệu thử nghiệm!")

if __name__ == "__main__":
    main()