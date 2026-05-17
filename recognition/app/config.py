# recognition/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Модели
    YOLO_MODEL_PATH: str = "models/yolov8n.pt"
    ANOMALIB_CONFIG: str = "patchcore"
    SAM_MODEL_TYPE: str = "vit_b"

    # Производительность
    MAX_BATCH_SIZE: int = 32
    INFERENCE_TIMEOUT: int = 30
    MODEL_CACHE_TTL: int = 3600

    # Очередь задач
    REDIS_URL: str = "redis://localhost:6379/0"
    MAX_CONCURRENT_TRAINING: int = 3

    # Хранилище
    MODELS_DIR: str = "/app/models_storage"
    TEMP_DIR: str = "/app/temp"

    class Config:
        env_file = ".env"
        env_prefix = "ML_"


settings = Settings()