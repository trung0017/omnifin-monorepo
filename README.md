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

## 2. Kiến Trúc Tổng Thể & Hạ Tầng (System Architecture)

Hệ thống được phân chia thành các lớp chức năng độc lập, giao tiếp thông qua mạng nội bộ Docker cô lập:

### 2.1. Lớp Hạ Tầng Container (`docker-compose.yml`)
* **PostgreSQL 15 (`postgres`):** Cơ sở dữ liệu quan hệ lưu trữ dữ liệu tài chính & giao dịch cốt lõi.
* **Redis 7 (`redis`):** Caching Layer phục vụ quản lý session phiên làm việc & mã xác thực OTP eKYC.
* **Apache Kafka & Zookeeper (`kafka`, `zookeeper`):** Message Broker điều phối luồng dữ liệu sự kiện giao dịch thời gian thực (Topic: `financial_transactions`).
* **Qdrant v1.3.0 (`qdrant`):** Vector Database lưu trữ vector embedding tri thức cho Trợ lý ảo RAG.

### 2.2. Lớp Dịch vụ Backend (Microservices Core - FastAPI)
* **`identity-service`:** Dịch vụ Định danh & Thị giác Máy tính (eKYC Engine). Tối ưu nạp trước mô hình vào RAM (Warm-up Engine) giúp đảm bảo phản hồi nhanh.
* **`transaction-service`:** Dịch vụ tiếp nhận & đóng gói sự kiện giao dịch tài chính đẩy vào Kafka Message Broker.
* **`ai-service`:** Khung cấu trúc dịch vụ Trợ lý ảo AI & RAG Engine kết nối Vector DB.

### 2.3. Lớp Giao Diện (Apps Layer) & Scripts Bổ Trợ
* **`apps/mobile-app` & `apps/web-admin`:** Định hướng khung ứng dụng React Native & Dashboard ReactJS.
* **`scripts/mock_data.py`:** Công cụ giả lập luồng giao dịch tần suất cao pushing trực tiếp vào Apache Kafka.

---

## 3. Cấu Trúc Mã Nguồn Monorepo

Cấu trúc cây thư mục chi tiết khớp chính xác với toàn bộ các tệp tin hiện có trong dự án:

```text
omnifin-monorepo/
├── README.md                    # Tài liệu hướng dẫn & tổng quan dự án (Tài liệu này)
├── .cursorrules                 # Bộ quy tắc định hình tư duy phát triển cho AI
├── .gitignore                   # Cấu hình bỏ qua các tệp tạm, môi trường ảo & trọng số mô hình
├── docker-compose.yml           # Khởi chạy hạ tầng container (Postgres, Redis, Kafka, Zookeeper, Qdrant)
├── apps/                        # Nơi chứa mã nguồn các ứng dụng giao diện (Frontend)
│   ├── mobile-app/              # Khung ứng dụng di động React Native (eKYC & Chatbot)
│   └── web-admin/               # Khung ứng dụng Bảng điều khiển quản trị ReactJS
├── services/                    # Nơi chứa các dịch vụ xử lý backend (Microservices)
│   ├── identity-service/        # Dịch vụ Định danh eKYC & Thị giác máy tính (FastAPI)
│   │   ├── app/
│   │   │   ├── api/             # Động cơ API Endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   └── ekyc.py      # API Trích xuất OCR, So khớp ArcFace & Liveness Detection
│   │   │   ├── core/            # Cấu hình hệ thống & Cơ sở dữ liệu bất đồng bộ
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py    # Thiết lập biến môi trường & Database URL (Pydantic Settings)
│   │   │   │   └── database.py  # Khởi tạo Async Engine & Session Pool SQLAlchemy
│   │   │   ├── data/            # Thư mục lưu trữ dữ liệu ảnh mẫu eKYC
│   │   │   │   ├── sample_cccd/ # Ảnh phôi CCCD mẫu thử nghiệm
│   │   │   │   └── sample_selfie/ # Ảnh chân dung mẫu thử nghiệm
│   │   │   ├── models/          # Thư mục lưu trữ các file trọng số AI
│   │   │   ├── download_samples.py # Script tự động sinh ảnh mẫu thử nghiệm eKYC offline
│   │   │   └── main.py          # Khởi chạy FastAPI & Warm-up nạp trước mô hình AI vào RAM
│   │   ├── requirements.txt     # Thư viện Python (FastAPI, EasyOCR, DeepFace, Ultralytics, SQLAlchemy, asyncpg)
│   │   └── yolov8n.pt           # Trọng số mô hình YOLOv8-Nano
│   ├── transaction-service/     # Dịch vụ Tiếp nhận & Đóng gói Giao dịch (FastAPI)
│   │   ├── app/
│   │   │   ├── kafka/           # Quản lý kết nối & Producer Apache Kafka
│   │   │   │   ├── __init__.py
│   │   │   │   └── connection.py # Lớp KafkaManager kết nối AIOKafkaProducer bất đồng bộ
│   │   │   └── main.py          # Khởi chạy FastAPI & Endpoint tiếp nhận giao dịch
│   │   └── requirements.txt     # Thư viện Python (FastAPI, aiokafka, pydantic, uvicorn)
│   └── ai-service/              # Dịch vụ Trợ lý ảo NLP & Luồng tri thức RAG (FastAPI)
│       ├── app/
│       │   ├── api/             # Quản lý giao thức API
│       │   ├── services/        # Tích hợp mô hình LangChain & kết nối Qdrant VectorDB
│       │   └── main.py          # Entrypoint ứng dụng API Trợ lý ảo
│       └── requirements.txt     # Thư viện phụ thuộc AI Service
└── scripts/                     # Công cụ thử nghiệm & Giả lập dữ liệu
    ├── mock_data.py             # Script Python giả lập luồng giao dịch tần suất cao đẩy vào Kafka
    └── requirements.txt         # Thư viện phụ thuộc cho scripts (aiokafka, Faker)
```

---

## 4. Chi Tiết API Endpoints & Tính Năng Đã Triển Khai

### 4.1. Identity & eKYC Service (`services/identity-service`)
* **`POST /v1/ekyc/ocr`**: Trích xuất thông tin văn bản từ thẻ CCCD bằng EasyOCR kết hợp khung định vị YOLOv8-Nano.
* **`POST /v1/ekyc/face-match`**: So khớp sinh trắc học khuôn mặt giữa ảnh Selfie và ảnh trên CCCD qua thuật toán ArcFace và bộ định vị MTCNN.
* **`POST /v1/ekyc/liveness`**: Kiểm tra thực thể sống chống gian lận ảnh chụp lại từ màn hình/2D thông qua thuật toán phân tích kết cấu tần số biến đổi Laplacian (`Laplacian Texture Frequency Analysis`).
* **`GET /health`**: Kiểm tra trạng thái hoạt động của dịch vụ và kết nối PostgreSQL.

### 4.2. Transaction Service (`services/transaction-service`)
* **`POST /v1/transactions`**: Tiếp nhận gói tin giao dịch tài chính (`transaction_id`, `account_number`, `amount`, `currency`), mã hóa và đẩy trực tiếp thành sự kiện phân tán vào Kafka Topic `financial_transactions`.

### 4.3. High-Throughput Mock Generator (`scripts/mock_data.py`)
* Sinh dữ liệu giao dịch ngẫu nhiên chuẩn doanh nghiệp bằng `Faker`, nén dữ liệu `gzip` và phát liên tục vào Kafka Broker với tốc độ cao (~100 TPS).

---

## 5. Hướng Dẫn Khởi Chạy & Kiểm Thử Hệ Thống

### 5.1. Khởi chạy Hạ tầng Container
Sử dụng Docker Compose để dựng toàn bộ bộ cơ sở dữ liệu và message broker:
```bash
docker compose up -d
```
Kiểm tra trạng thái các container đang chạy:
```bash
docker compose ps
```

### 5.2. Chạy Identity & eKYC Service
```bash
cd services/identity-service

# Tạo và kích hoạt môi trường ảo Python
python3 -m venv .venv
source .venv/bin/activate

# Cài đặt danh sách thư viện phụ thuộc
pip install -r requirements.txt

# (Tùy chọn) Sinh dữ liệu ảnh mẫu CCCD & Selfie thử nghiệm
python app/download_samples.py

# Khởi chạy dịch vụ API
uvicorn app.main:app --reload --port 8000
```
* Swagger UI documentation: `http://localhost:8000/docs`

### 5.3. Chạy Transaction Service
```bash
cd services/transaction-service

# Tạo và kích hoạt môi trường ảo Python
python3 -m venv .venv
source .venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt

# Khởi chạy dịch vụ API
uvicorn app.main:app --reload --port 8001
```
* Swagger UI documentation: `http://localhost:8001/docs`

### 5.4. Khởi chạy Script Giả Lập Luồng Giao Dịch Kafka
```bash
cd scripts

# Tạo và kích hoạt môi trường ảo Python
python3 -m venv .venv
source .venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt

# Chạy script đẩy sự kiện vào Kafka
python mock_data.py
```

---

## 6. Định Hướng Phát Triển Tiếp Theo (Roadmap)

- [ ] Hoàn thiện `ai-service` với luồng RAG kết nối Qdrant Vector DB & LangChain.
- [ ] Xây dựng giao diện ứng dụng di động `apps/mobile-app` bằng React Native (Quét eKYC & Chatbot UI).
- [ ] Phát triển Dashboard quản trị `apps/web-admin` trực quan hóa biểu đồ giao dịch & phát hiện gian lận thời gian thực.
- [ ] Triển khai Apache Spark Structured Streaming để phân tích gian lận nâng cao trên luồng Kafka.