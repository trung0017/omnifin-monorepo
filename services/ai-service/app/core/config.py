from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "OmniFin AI Assistant Service"
    API_V1_STR: str = "/v1"
    
    # Mặc định kết nối tới container 'qdrant' cổng 6333 trong mạng Docker.
    # Nếu chạy local ngoài Docker trên Mac, hãy đổi thành "localhost" thông qua tệp .env
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str | None = None
    QDRANT_URL: str | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()