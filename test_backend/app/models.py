# backend/app/models.py
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    TRAINING = "training"


class TaskStatus(str, enum.Enum):
    QUEUED = "queued"
    PREPARING = "preparing"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role = Column(String(20), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("TrainingTask", back_populates="user")
    inspections = relationship("Inspection", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default=ProjectStatus.ACTIVE)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    active_model_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="projects")
    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")
    models = relationship("Model", back_populates="project", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="project", cascade="all, delete-orphan")
    training_tasks = relationship("TrainingTask", back_populates="project")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    total_images = Column(Integer, default=0)
    good_samples = Column(Integer, default=0)
    defect_samples = Column(Integer, default=0)
    defect_classes = Column(JSONB, default=list)
    total_size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="datasets")
    images = relationship("DatasetImage", back_populates="dataset", cascade="all, delete-orphan")


class DatasetImage(Base):
    __tablename__ = "dataset_images"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    is_defect = Column(Boolean, default=False)
    defect_class = Column(String(100), nullable=True)
    image_metadata = Column(JSONB, default=dict)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dataset = relationship("Dataset", back_populates="images")
    annotations = relationship("Annotation", back_populates="image", cascade="all, delete-orphan")


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    image_id = Column(String(36), ForeignKey("dataset_images.id"), nullable=False)
    defect_class = Column(String(100), nullable=False)
    bbox = Column(JSONB, nullable=True)
    mask = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    image = relationship("DatasetImage", back_populates="annotations")


class Model(Base):
    __tablename__ = "models"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False)
    version = Column(Integer, default=1)
    file_url = Column(String(500), nullable=False)
    metrics = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="models")


class TrainingTask(Base):
    __tablename__ = "training_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    model_id = Column(String(36), nullable=True)
    status = Column(String(20), default=TaskStatus.QUEUED)
    progress = Column(Integer, default=0)
    config = Column(JSONB, default=dict)
    metrics = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="training_tasks")
    user = relationship("User", back_populates="tasks")


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    result_url = Column(String(500), nullable=True)
    defects = Column(JSONB, default=list)
    processing_time_ms = Column(Float, nullable=True)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="inspections")
    user = relationship("User", back_populates="inspections")
    feedback = relationship("Feedback", back_populates="inspection", uselist=False, cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(36), ForeignKey("inspections.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    corrected_defects = Column(JSONB, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    inspection = relationship("Inspection", back_populates="feedback")
    user = relationship("User", back_populates="feedbacks")