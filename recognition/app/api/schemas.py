# app/api/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any
from enum import Enum
from datetime import datetime


class ModelType(str, Enum):
    YOLO = "yolo"
    ANOMALIB = "anomalib"
    SAM = "sam"
    AUTO = "auto"


class Defect(BaseModel):
    """Модель дефекта"""
    class_name: str = Field(..., description="Название класса дефекта")
    confidence: float = Field(..., ge=0, le=1, description="Уверенность")
    bbox: Optional[List[float]] = Field(None, description="Bounding box [x1, y1, x2, y2]")
    mask: Optional[str] = Field(None, description="Маска дефекта (base64 или RLE)")
    area: Optional[float] = Field(None, description="Площадь дефекта в пикселях")
    centroid: Optional[List[float]] = Field(None, description="Центр масс [x, y]")


class PredictRequest(BaseModel):
    """Запрос на инференс"""
    image: Union[str, bytes] = Field(..., description="Изображение (base64 или URL)")
    model_id: str = Field(..., description="Идентификатор модели")
    threshold: float = Field(0.5, ge=0, le=1, description="Порог уверенности")
    return_mask: bool = Field(False, description="Возвращать ли маску")


class PredictResponse(BaseModel):
    """Ответ инференса"""
    request_id: str
    model_id: str
    defects: List[Defect]
    processing_time_ms: float
    image_size: tuple[int, int]


class TrainRequest(BaseModel):
    """Запрос на обучение"""
    project_id: str
    dataset_url: str
    model_type: ModelType = ModelType.AUTO
    config: Optional[dict] = Field(default_factory=dict, description="Параметры обучения")
    epochs: int = Field(100, ge=1, le=500)
    batch_size: int = Field(16, ge=1, le=128)
    learning_rate: float = Field(0.001, ge=1e-6, le=0.1)
    image_size: int = Field(640, ge=224, le=1280)


class TrainResponse(BaseModel):
    """Ответ на запрос обучения"""
    task_id: str
    project_id: str
    status: str = "queued"
    status_url: str
    created_at: datetime


class ModelInfo(BaseModel):
    """Информация о модели"""
    model_id: str
    model_type: ModelType
    project_id: str
    version: int
    created_at: datetime
    metrics: dict
    is_active: bool