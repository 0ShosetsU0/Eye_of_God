# app/services/training.py
import asyncio
import uuid
from typing import Dict, Optional
from datetime import datetime
from ..api.schemas import TrainRequest, TrainResponse
from ..services.model_manager import model_manager
from ..config import settings


class TrainingService:
    """Сервис для управления обучением моделей"""

    def __init__(self):
        self._tasks: Dict[str, dict] = {}

    async def start_training(
            self,
            request: TrainRequest,
            background_tasks
    ) -> TrainResponse:
        """Запуск обучения в фоне"""

        task_id = uuid.uuid4().hex[:16]

        # Создаем задачу
        self._tasks[task_id] = {
            "task_id": task_id,
            "project_id": request.project_id,
            "status": "queued",
            "created_at": datetime.now(),
            "progress": 0,
            "metrics": None,
            "error": None
        }

        # Запускаем в фоне
        background_tasks.add_task(
            self._run_training,
            task_id,
            request
        )

        return TrainResponse(
            task_id=task_id,
            project_id=request.project_id,
            status="queued",
            status_url=f"/api/v1/train/{task_id}/status",
            created_at=datetime.now()
        )

    async def _run_training(self, task_id: str, request: TrainRequest):
        """Выполнение обучения"""

        try:
            # Обновляем статус
            self._update_task(task_id, status="preparing", progress=10)

            # Создаем новую модель
            model_info = await model_manager.create_model(
                model_type=request.model_type,
                project_id=request.project_id
            )

            self._update_task(task_id, status="training", progress=20)

            # Получаем модель
            model = await model_manager.get_model(model_info.model_id)

            # Выполняем обучение
            result = await model.train(
                dataset_path=request.dataset_url,
                config={
                    "epochs": request.epochs,
                    "batch_size": request.batch_size,
                    "learning_rate": request.learning_rate,
                    "image_size": request.image_size,
                    **request.config
                }
            )

            # Обновляем информацию о модели
            model_info.metrics = result.get("metrics", {})

            # Активируем модель
            await model_manager.activate_model(model_info.model_id)

            self._update_task(
                task_id,
                status="completed",
                progress=100,
                metrics=result.get("metrics"),
                model_id=model_info.model_id
            )

        except Exception as e:
            self._update_task(
                task_id,
                status="failed",
                error=str(e)
            )

    def _update_task(self, task_id: str, **kwargs):
        """Обновление информации о задаче"""
        if task_id in self._tasks:
            self._tasks[task_id].update(kwargs)

    async def get_status(self, task_id: str) -> Optional[dict]:
        """Получение статуса задачи"""
        return self._tasks.get(task_id)


training_service = TrainingService()