# backend/app/routers/training.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from app.database import get_db
from app.models import Project, TrainingTask, Model, User
from app.schemas import TrainRequest, TrainResponse, TrainingStatusResponse, TrainingConfig
from app.dependencies import get_current_active_user, get_project_permission
from app.services.ml_client import ml_client

router = APIRouter()


@router.post("/start", response_model=TrainResponse)
async def start_training(
        request: TrainRequest,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """Запуск обучения модели"""

    # Проверяем существование проекта
    result = await db.execute(select(Project).where(Project.id == request.project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Создаем задачу обучения
    task = TrainingTask(
        id=str(uuid.uuid4()),
        project_id=request.project_id,
        user_id=current_user.id,
        config=request.config.model_dump(),
        status="queued"
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Обновляем статус проекта
    project.status = "training"
    await db.commit()

    # Запускаем обучение в фоне
    background_tasks.add_task(
        run_training,
        task_id=task.id,
        project_id=request.project_id,
        config=request.config
    )

    return TrainResponse(
        task_id=task.id,
        project_id=request.project_id,
        status=task.status,
        status_url=f"/api/v1/training/status/{task.id}",
        created_at=task.created_at
    )


@router.get("/status/{task_id}", response_model=TrainingStatusResponse)
async def get_training_status(
        task_id: str,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """Получение статуса обучения"""

    result = await db.execute(select(TrainingTask).where(TrainingTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TrainingStatusResponse(
        task_id=task.id,
        project_id=task.project_id,
        status=task.status,
        progress=task.progress,
        metrics=task.metrics,
        error_message=task.error_message,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at
    )


@router.post("/cancel/{task_id}")
async def cancel_training(
        task_id: str,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """Отмена обучения"""

    result = await db.execute(select(TrainingTask).where(TrainingTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "cancelled"
    await db.commit()

    return {"message": "Training cancelled"}


async def run_training(task_id: str, project_id: str, config: TrainingConfig):
    """Фоновая задача обучения"""
    # Здесь будет логика отправки запроса к ML-сервису
    # и обновления статуса в базе данных
    pass