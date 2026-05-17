# recognition/app/services/task_queue.py
from celery import Celery
from typing import Dict, Any, Optional
import asyncio
from app.config import settings

celery_app = Celery(
    "defectvision",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
)


class TaskQueue:
    def __init__(self):
        self.active_tasks: Dict[str, dict] = {}

    async def start(self):
        """Запуск очереди задач"""
        pass

    async def stop(self):
        """Остановка очереди"""
        pass

    def submit_training(self, model_id: str, dataset_path: str, config: dict) -> str:
        """Отправка задачи на обучение"""
        task = celery_app.send_task(
            "train_model",
            args=[model_id, dataset_path],
            kwargs=config,
            task_id=f"train_{model_id}"
        )
        return task.id

    def get_task_status(self, task_id: str) -> Optional[dict]:
        """Получение статуса задачи"""
        task = celery_app.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None,
            "info": task.info if task.info else {}
        }


task_queue = TaskQueue()