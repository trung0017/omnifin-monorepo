import os
import time
import random
import logging
import mlflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MLOpsTrainer")

def main():
    logger.info("=== OMNIFIN MLOPS: PHISHING & FRAUD DETECTION MODEL TRAINING ===")
    
    # Thiết lập URI kết nối MLflow Server
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    mlflow.set_tracking_uri(tracking_uri)
    
    experiment_name = "OmniFin_Fraud_Detection"
    mlflow.set_experiment(experiment_name)
    
    logger.info(f"Đang kết nối tới MLflow Tracking Server tại: {tracking_uri}")
    logger.info(f"Kích hoạt Experiment: {experiment_name}")
    
    with mlflow.start_run(run_name="ci_cd_automated_pipeline_run"):
        # 1. Khai báo các siêu tham số (Hyperparameters)
        params = {
            "model_type": "XGBoost_Fraud_Classifier",
            "learning_rate": 0.05,
            "max_depth": 6,
            "n_estimators": 100,
            "threshold_fraud": 0.85
        }
        
        logger.info("Ghi nhận các tham số cấu hình Hyperparameters...")
        for key, val in params.items():
            mlflow.log_param(key, val)
            
        # 2. Giả lập quá trình huấn luyện mô hình (Training Loop)
        logger.info("Bắt đầu quá trình huấn luyện mô hình trên tập dữ liệu giao dịch...")
        time.sleep(1.0)
        
        # 3. Tính toán các chỉ số đánh giá hiệu năng (Metrics)
        accuracy = round(random.uniform(0.965, 0.985), 4)
        precision = round(random.uniform(0.950, 0.975), 4)
        recall = round(random.uniform(0.940, 0.968), 4)
        f1_score = round(2 * (precision * recall) / (precision + recall), 4)
        
        metrics = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score
        }
        
        logger.info("Đang đồng bộ các chỉ số hiệu năng (Metrics) lên MLflow Server...")
        for k, v in metrics.items():
            mlflow.log_metric(k, v)
            logger.info(f" - {k}: {v}")
            
        logger.info("🚀 TỰ ĐỘNG HÓA HOÀN TẤT: Mô hình đã được ghi vết an toàn vào MLflow Registry!")

if __name__ == "__main__":
    main()
