# app/models/mock.py
import random
import numpy as np
from typing import List, Optional
from .base import BaseModel
from ..api.schemas import Defect, ModelType


class MockModel(BaseModel):
    """Мок-модель для тестирования и разработки"""

    def __init__(self, model_id: str):
        super().__init__(model_id, ModelType.AUTO)
        self.defect_classes = ["царапина", "скол", "вмятина", "загрязнение", "трещина"]

    async def load(self) -> None:
        """Загрузка мок-модели"""
        self.is_loaded = True
        print(f"Mock model {self.model_id} loaded")

    async def unload(self) -> None:
        """Выгрузка мок-модели"""
        self.is_loaded = False
        self._model = None
        print(f"Mock model {self.model_id} unloaded")

    async def predict(
            self,
            image: np.ndarray,
            threshold: float = 0.5,
            return_mask: bool = False
    ) -> List[Defect]:
        """Генерация случайных дефектов для тестирования"""

        h, w = image.shape[:2]
        defects = []

        # Генерируем случайное количество дефектов (0-3)
        num_defects = random.randint(0, 3)

        for _ in range(num_defects):
            # Случайные параметры дефекта
            class_name = random.choice(self.defect_classes)
            confidence = random.uniform(0.6, 0.98)

            # Случайный bounding box
            x1 = random.uniform(0, w * 0.7)
            y1 = random.uniform(0, h * 0.7)
            x2 = x1 + random.uniform(w * 0.05, w * 0.3)
            y2 = y1 + random.uniform(h * 0.05, h * 0.3)

            defect = Defect(
                class_name=class_name,
                confidence=confidence,
                bbox=[x1, y1, x2, y2],
                area=(x2 - x1) * (y2 - y1),
                centroid=[(x1 + x2) / 2, (y1 + y2) / 2]
            )

            # Генерация простой маски (квадрат)
            if return_mask:
                mask = np.zeros((h, w), dtype=np.uint8)
                mask[int(y1):int(y2), int(x1):int(x2)] = 255
                defect.mask = self._mask_to_base64(mask)

            defects.append(defect)

        return defects

    async def train(self, dataset_path: str, config: dict) -> dict:
        """Эмуляция обучения"""
        import time

        # Симулируем обучение с прогрессом
        epochs = config.get("epochs", 10)

        for epoch in range(epochs):
            # Симуляция времени на эпоху
            await self._simulate_training_step(epoch, epochs)

        return {
            "status": "completed",
            "metrics": {
                "mAP": random.uniform(0.85, 0.95),
                "precision": random.uniform(0.88, 0.96),
                "recall": random.uniform(0.82, 0.94),
                "f1": random.uniform(0.85, 0.95)
            },
            "model_path": f"/models/{self.model_id}.pt"
        }

    async def _simulate_training_step(self, epoch: int, total_epochs: int):
        """Симуляция шага обучения"""
        import asyncio
        progress = (epoch + 1) / total_epochs
        print(f"Training progress: {progress:.1%}")
        await asyncio.sleep(1)

    @staticmethod
    def _mask_to_base64(mask: np.ndarray) -> str:
        """Конвертация маски в base64"""
        import base64
        import cv2
        _, buffer = cv2.imencode('.png', mask)
        return base64.b64encode(buffer).decode('utf-8')