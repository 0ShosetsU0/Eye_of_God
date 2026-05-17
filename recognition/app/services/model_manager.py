# recognition/app/services/model_manager.py
import asyncio
from typing import Dict, Optional
from datetime import datetime
import uuid

from app.models.yolo_detector import YOLODetector
from app.models.anomalib_detector import AnomalibDetector
from app.models.sam_segmentor import SAMSegmentor
from app.models.base import BaseModel
from app.config import settings


class ModelManager:
    def __init__(self):
        self._models: Dict[str, BaseModel] = {}
        self._model_info: Dict[str, dict] = {}
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Инициализация менеджера"""
        # Предзагрузка базовых моделей
        pass

    async def create_model(
            self,
            model_type: str,
            project_id: str,
            config: dict = None
    ) -> str:
        """Создание новой модели"""
        model_id = f"{project_id}_{uuid.uuid4().hex[:8]}"

        if model_type == "yolo":
            model = YOLODetector(model_id, config or {})
        elif model_type == "anomalib":
            model = AnomalibDetector(model_id, config or {})
        elif model_type == "sam":
            model = SAMSegmentor(model_id, config or {})
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        async with self._lock:
            self._models[model_id] = model
            self._model_info[model_id] = {
                "model_id": model_id,
                "project_id": project_id,
                "model_type": model_type,
                "created_at": datetime.now().isoformat(),
                "status": "created"
            }

        return model_id

    async def get_model(self, model_id: str) -> Optional[BaseModel]:
        """Получение модели"""
        model = self._models.get(model_id)
        if model and not model.is_loaded:
            await model.load()
        return model

    async def delete_model(self, model_id: str):
        """Удаление модели"""
        async with self._lock:
            if model_id in self._models:
                await self._models[model_id].unload()
                del self._models[model_id]
                del self._model_info[model_id]

    async def train_model(
            self,
            model_id: str,
            dataset_path: str,
            callback: Optional[callable] = None
    ):
        """Обучение модели"""
        model = await self.get_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")

        result = await model.train(dataset_path, callback)
        return result


model_manager = ModelManager()