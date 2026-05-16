# backend/app/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    TRAINING = "training"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    PREPARING = "preparing"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelType(str, Enum):
    YOLO = "yolo"
    ANOMALIB = "anomalib"
    SAM = "sam"
    AUTO = "auto"


# User schemas
class UserBase(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Project schemas
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: ProjectStatus
    owner_id: str
    active_model_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    dataset_stats: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


# Dataset schemas
class DatasetImageUpload(BaseModel):
    filename: str
    is_defect: bool = False
    defect_class: Optional[str] = None


class DatasetResponse(BaseModel):
    id: str
    project_id: str
    name: str
    total_images: int
    good_samples: int
    defect_samples: int
    defect_classes: List[str]
    created_at: datetime


# Defect schemas
class Defect(BaseModel):
    class_name: str
    confidence: float
    bbox: Optional[List[float]] = None
    mask: Optional[str] = None
    area: Optional[float] = None
    centroid: Optional[List[float]] = None


# Training schemas
class TrainingConfig(BaseModel):
    model_type: ModelType = ModelType.AUTO
    epochs: int = Field(100, ge=1, le=500)
    batch_size: int = Field(16, ge=1, le=128)
    learning_rate: float = Field(0.001, ge=1e-6, le=0.1)
    image_size: int = Field(640, ge=224, le=1280)


class TrainRequest(BaseModel):
    project_id: str
    config: TrainingConfig = Field(default_factory=TrainingConfig)


class TrainResponse(BaseModel):
    task_id: str
    project_id: str
    status: TaskStatus
    status_url: str
    created_at: datetime


class TrainingStatusResponse(BaseModel):
    task_id: str
    project_id: str
    status: TaskStatus
    progress: int
    current_epoch: Optional[int] = None
    total_epochs: Optional[int] = None
    current_loss: Optional[float] = None
    metrics: Optional[Dict[str, float]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# Inspection schemas
class InspectRequest(BaseModel):
    project_id: str
    image: str  # base64 or URL
    threshold: float = Field(0.5, ge=0, le=1)


class InspectResponse(BaseModel):
    id: str
    project_id: str
    defects: List[Defect]
    processing_time_ms: float
    image_url: str
    result_url: str
    created_at: datetime


class BatchInspectRequest(BaseModel):
    project_id: str
    images: List[str]  # list of base64 or URLs
    threshold: float = Field(0.5, ge=0, le=1)


class BatchInspectResponse(BaseModel):
    task_id: str
    project_id: str
    total_images: int
    status_url: str


# Feedback schemas
class FeedbackRequest(BaseModel):
    inspection_id: str
    is_correct: bool
    corrected_defects: Optional[List[Defect]] = None
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    inspection_id: str
    is_correct: bool
    corrected_defects: Optional[List[Defect]]
    created_at: datetime


# Auth schemas
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None