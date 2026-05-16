# app/config.py
import os
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Настройки ML-сервиса"""

    # Сервис
    SERVICE_NAME: str = "ml-service"
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8001
    DEBUG: bool = False

    # Режимы работы
    USE_MOCK: bool = True  # Если True, используем мок-модели
    DEV_MODE: bool = True

    # Пути
    BASE_DIR: Path = Path(__file__).parent.parent
    MODELS_DIR: Path = BASE_DIR / "models_storage"
    TEMP_DIR: Path = BASE_DIR / "temp"

    # Модели
    YOLO_MODEL_PATH: str = "yolov8n.pt"  # Базовая модель
    ANOMALIB_CONFIG: str = "patchcore"  # Патчкор или padim
    SAM_MODEL_TYPE: str = "vit_h"  # vit_h, vit_l, vit_b

    # Производительность
    MAX_BATCH_SIZE: int = 32
    INFERENCE_TIMEOUT: int = 30
    MODEL_CACHE_TTL: int = 3600

    # Хранилище
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "localhost:9000")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET: str = "models"

    class Config:
        env_file = ".env"
        env_prefix = "ML_"


settings = Settings()

# Создаем необходимые директории
settings.MODELS_DIR.mkdir(exist_ok=True)
settings.TEMP_DIR.mkdir(exist_ok=True)