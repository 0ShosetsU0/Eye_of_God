# recognition/app/tasks.py
from celery import Task
from app.services.model_manager import model_manager
from app.services.task_queue import celery_app


class TrainingTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(f"Training failed: {exc}")

    def on_success(self, retval, task_id, args, kwargs):
        print(f"Training completed: {task_id}")


@celery_app.task(bind=True, base=TrainingTask)
def train_model(self, model_id: str, dataset_path: str, **kwargs):
    """Задача обучения модели"""
    self.update_state(state="PROGRESS", meta={"current": 0, "total": 100})

    # Здесь будет реальное обучение
    for i in range(100):
        self.update_state(
            state="PROGRESS",
            meta={"current": i + 1, "total": 100, "loss": 1.0 - (i + 1) / 100}
        )

    return {"status": "completed", "metrics": {"accuracy": 0.95}}