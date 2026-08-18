
# OmniFin Enterprise - Nền tảng Ngân hàng Số & Trợ lý Đầu tư AI Phân tán

OmniFin Enterprise là một hệ thống "Siêu ứng dụng" tài chính cấp độ doanh nghiệp (Enterprise-level Proof of Concept) kết hợp quy trình định danh khách hàng điện tử (eKYC) bảo mật cao, hệ thống phân tích luồng dữ liệu giao dịch thời gian thực nhằm phát hiện gian lận và Trợ lý ảo thông minh ứng dụng kiến trúc RAG.

Hệ thống được thiết kế theo mô hình **Microservices** kết hợp **Kiến trúc hướng sự kiện (Event-Driven Architecture)** nhằm chứng minh năng lực tối ưu hiệu năng I/O, xử lý dữ liệu lớn và tích hợp các mô hình trí tuệ nhân tạo thế hệ mới vào môi trường tài chính nghiêm ngặt.

---

## 1. Tầm Nhìn Kỹ Thuật & Bài Toán Thực Tế
Dự án tập trung giải quyết triệt để 3 bài toán cốt lõi của ngành Fintech hiện nay:
* **Tuân thủ Pháp lý (Quyết định 2345/QĐ-NHNN):** Bắt buộc xác thực sinh trắc học khuôn mặt và kiểm tra thực thể sống (Liveness Detection) đối với các giao dịch chuyển tiền giá trị cao nhằm triệt tiêu rủi ro tài khoản ảo.
* **Tự động hóa Dịch vụ Tài chính:** Giảm tải cho hệ thống tổng đài bằng Trợ lý ảo AI đa mô thức (Text & Image) sử dụng cấu trúc RAG để đọc hiểu, phản hồi chính xác các chính sách ngân hàng và nhận diện biên lai lỗi.
* **Phát hiện Gian lận Thời gian thực (Real-time Fraud Detection):** Xử lý luồng giao dịch với thông lượng cao lên tới 1000 TPS, phân tích hành vi bất thường ngay khi sự kiện được sinh ra để ngăn chặn dòng tiền bất hợp pháp.

---

## 2. Kiến Trúc Tổng Thể Hệ Thống (System Architecture) 

Hệ thống chia làm 4 lớp chức năng độc lập, giao tiếp thông qua mạng nội bộ Docker cô lập:

1. **Client Layer (Lớp Tương Tác):**
   * `mobile-app` (React Native): Ứng dụng di động dành cho người dùng cuối (Mở tài khoản, quét eKYC, trò chuyện với trợ lý AI qua giao thức WebSockets).
   * `web-admin` (ReactJS): Bảng điều khiển dành cho kiểm toán viên, hiển thị biểu đồ giao dịch trực quan từ luồng xử lý Spark/Kafka.
2. **API Gateway & Event Broker:**
   * Gateway quản lý tập trung và định tuyến luồng yêu cầu. Mọi hành động nhạy cảm đều sinh sự kiện đẩy vào luồng dữ liệu trung tâm **Apache Kafka**.
3. **Microservices Core (Lớp Dịch vụ Lõi - FastAPI):**
   * `identity-service`: Trích xuất thông tin văn bản từ CCCD (YOLOv8 + OCR), đối chiếu khuôn mặt (ArcFace) và kiểm tra ảnh thật/giả (Anti-spoofing).
   * `ai-service`: Xử lý hội thoại thông minh nhờ LangChain và Local LLM, kết nối trực tiếp cơ sở dữ liệu vector.
   * `transaction-service`: Xử lý giao dịch chuyển tiền và đóng gói các sự kiện giao dịch.
4. **Big Data & Storage Layer (Lớp Dữ liệu ĐaPersistence):**
   * Cơ sở dữ liệu phân tách theo nghiệp vụ: PostgreSQL (Giao dịch), MongoDB (Hội thoại), Milvus/Qdrant (Vector tri thức) và Redis (Cơ chế đệm dữ liệu - Cache).

---

## 3. Cấu Trúc Mã Nguồn Monorepo

Dự án được tổ chức dưới dạng Monorepo giúp quản lý tập trung toàn bộ cấu phần hạ tầng, dịch vụ và giao diện:

```text
omnifin-monorepo/
├── README.md                    # Tài liệu tổng thể dự án (Tài liệu này)
├── .cursorrules                 # Bộ quy tắc định hình tư duy phát triển cho AI
├── docker-compose.yml           # Khởi chạy toàn bộ hạ tầng (Postgres, Kafka, Redis, Milvus)
├── apps/                        # Nơi chứa mã nguồn các ứng dụng giao diện (Frontend)
│   ├── mobile-app/              # Ứng dụng di động React Native (eKYC & Khung Chat)
│   └── web-admin/               # Trực quan hóa Dashboard quản trị ReactJS
├── services/                    # Nơi chứa các dịch vụ xử lý backend (Microservices)
│   ├── identity-service/        # Lõi xử lý Định danh & Thị giác máy tính (FastAPI)
│   │   ├── app/
│   │   │   ├── main.py          # Điểm khởi chạy ứng dụng API
│   │   │   ├── api/             # Nơi quản lý các endpoints trích xuất và so khớp ảnh
│   │   │   ├── core/            # Cấu hình hệ thống, thiết lập bảo mật
│   │   │   └── models/          # Thư mục lưu trữ tệp trọng số AI (Pre-trained weights)
│   │   └── requirements.txt     # Danh sách thư viện Python (FastAPI, DeepFace, EasyOCR)
│   ├── ai-service/              # Trợ lý ảo NLP & Luồng dữ liệu RAG (FastAPI)
│   │   ├── app/
│   │   │   ├── main.py          # Điểm khởi chạy API & kết nối WebSocket
│   │   │   ├── api/             # Quản lý giao thức kết nối thời gian thực
│   │   │   └── services/        # Tích hợp cấu phần LangChain và kết nối VectorDB
│   │   └── requirements.txt     # Danh sách thư viện Python (LangChain, Milvus-Client)
│   └── transaction-service/     # Quản lý nghiệp vụ giao dịch tài chính (FastAPI)
│       ├── app/
│       │   ├── main.py          # Điểm khởi chạy cổng xử lý giao dịch
│       │   └── kafka/           # Cấu hình thiết lập kết nối Kafka Producer/Consumer
│       └── requirements.txt     # Thư viện xử lý API và thư viện kết nối Aiokafka
└── scripts/                     # Công cụ bổ trợ phát triển
    └── mock_data.py             # Script Python giả lập sinh luồng giao dịch tần suất cao
