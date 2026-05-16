# app/services/model_manager.py
import asyncio
import uuid
from typing import Dict, Optional
from datetime import datetime
from ..models.base import BaseModel
from ..models.mock import MockModel
from ..models.yolo_detector import YOLODetector
from ..models.anomalib_detector import AnomalibDetector
from ..api.schemas import ModelType, ModelInfo
from ..config import settings


class ModelManager:
    """Менеджер моделей для загрузки, выгрузки и кэширования"""

    def __init__(self):
        self._models: Dict[str, BaseModel] = {}
        self._model_info: Dict[str, ModelInfo] = {}
        self._lock = asyncio.Lock()

    async def get_model(self, model_id: str) -> Optional[BaseModel]:
        """Получить модель по ID"""
        if model_id not in self._models:
            return None

        model = self._models[model_id]

        # Если модель не загружена, загружаем
        if not model.is_loaded:
            await model.load()

        return model

    async def create_model(
            self,
            model_type: ModelType,
            project_id: str,
            model_path: Optional[str] = None
    ) -> ModelInfo:
        """Создать новую модель"""

        model_id = f"{project_id}_{uuid.uuid4().hex[:8]}"

        # Создаем модель в зависимости от типа
        if settings.USE_MOCK:
            model = MockModel(model_id)
        else:
            if model_type == ModelType.YOLO:
                model = YOLODetector(model_id, model_path or settings.YOLO_MODEL_PATH)
            elif model_type == ModelType.ANOMALIB:
                model = AnomalibDetector(model_id, settings.ANOMALIB_CONFIG)
            else:
                model = MockModel(model_id)

        info = ModelInfo(
            model_id=model_id,
            model_type=model_type,
            project_id=project_id,
            version=1,
            created_at=datetime.now(),
            metrics={},
            is_active=False
        )

        async with self._lock:
            self._models[model_id] = model
            self._model_info[model_id] = info

        return info

    async def activate_model(self, model_id: str) -> bool:
        """Активировать модель"""

        if model_id not in self._model_info:
            return False

        # Деактивируем все другие модели для этого проекта
        project_id = self._model_info[model_id].project_id
        for info in self._model_info.values():
            if info.project_id == project_id and info.is_active:
                info.is_active = False

        self._model_info[model_id].is_active = True
        return True

    async def delete_model(self, model_id: str) -> bool:
        """Удалить модель"""

        if model_id not in self._models:
            return False

        async with self._lock:
            model = self._models[model_id]
            await model.unload()
            del self._models[model_id]
            del self._model_info[model_id]

        return True

    async def get_active_model(self, project_id: str) -> Optional[BaseModel]:
        """Получить активную модель для проекта"""

        for model_id, info in self._model_info.items():
            if info.project_id == project_id and info.is_active:
                return await self.get_model(model_id)

        return None

    def list_models(self, project_id: Optional[str] = None) -> list[ModelInfo]:
        """Список моделей"""

        if project_id:
            return [info for info in self._model_info.values() if info.project_id == project_id]
        return list(self._model_info.values())

    async def unload_unused_models(self) -> None:
        """Выгрузка неиспользуемых моделей"""

        for model_id, model in self._models.items():
            info = self._model_info.get(model_id)
            # Выгружаем неактивные модели
            if info and not info.is_active and model.is_loaded:
                await model.unload()


# Глобальный экземпляр
model_manager = ModelManager()