from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Jewellery ERP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    PAKKA_DATABASE_URL: str
    KACHA_DATABASE_URL: str
    SHARED_DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379"

    UPLOAD_DIR: str = "./uploads"
    MAX_IMAGE_SIZE_KB: int = 500

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    GST_RATE: float = 0.03

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-south-1"
    AWS_S3_BUCKET: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
