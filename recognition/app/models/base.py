# app/models/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, Any
import numpy as np
from ..api.schemas import Defect, ModelType


class BaseModel(ABC):
    """Абстрактный базовый класс для всех ML-моделей"""

    def __init__(self, model_id: str, model_type: ModelType):
        self.model_id = model_id
        self.model_type = model_type
        self.is_loaded = False
        self._model = None

    @abstractmethod
    async def load(self) -> None:
        """Загрузка модели в память"""
        pass

    @abstractmethod
    async def unload(self) -> None:
        """Выгрузка модели из памяти"""
        pass

    @abstractmethod
    async def predict(
            self,
            image: np.ndarray,
            threshold: float = 0.5,
            return_mask: bool = False
    ) -> List[Defect]:
        """Инференс на одном изображении"""
        pass

    @abstractmethod
    async def train(
            self,
            dataset_path: str,
            config: dict
    ) -> dict:
        """Обучение модели"""
        pass

    @property
    def is_ready(self) -> bool:
        return self.is_loaded and self._model is not None