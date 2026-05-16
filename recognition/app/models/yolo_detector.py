# app/models/yolo_detector.py
import numpy as np
from typing import List, Optional
import cv2
from .base import BaseModel
from ..api.schemas import Defect, ModelType


class YOLODetector(BaseModel):
    """YOLOv8 детектор для обнаружения дефектов"""

    def __init__(self, model_id: str, model_path: str):
        super().__init__(model_id, ModelType.YOLO)
        self.model_path = model_path

    async def load(self) -> None:
        """Загрузка YOLO модели"""
        try:
            from ultralytics import YOLO

            self._model = YOLO(self.model_path)
            self.is_loaded = True
            print(f"YOLO model {self.model_id} loaded from {self.model_path}")
        except Exception as e:
            print(f"Failed to load YOLO model: {e}")
            raise

    async def unload(self) -> None:
        """Выгрузка модели"""
        self._model = None
        self.is_loaded = False

    async def predict(
            self,
            image: np.ndarray,
            threshold: float = 0.5,
            return_mask: bool = False
    ) -> List[Defect]:
        """Обнаружение дефектов с помощью YOLO"""

        if not self.is_ready:
            raise RuntimeError("Model not loaded")

        # Выполняем инференс
        results = self._model(image, conf=threshold, verbose=False)

        defects = []

        if results and len(results) > 0:
            result = results[0]

            # Получаем данные из результата
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Координаты
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                    # Класс и уверенность
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]
                    confidence = float(box.conf[0])

                    defect = Defect(
                        class_name=class_name,
                        confidence=confidence,
                        bbox=[float(x1), float(y1), float(x2), float(y2)],
                        area=(x2 - x1) * (y2 - y1),
                        centroid=[(x1 + x2) / 2, (y1 + y2) / 2]
                    )

                    # Получаем маску если нужно
                    if return_mask and hasattr(box, 'mask') and box.mask is not None:
                        mask = box.mask.data[0].cpu().numpy()
                        defect.mask = self._mask_to_rle(mask)

                    defects.append(defect)

        return defects

    async def train(self, dataset_path: str, config: dict) -> dict:
        """Обучение YOLO модели"""
        from ultralytics import YOLO

        # Загружаем предобученную модель
        model = YOLO("yolov8n.pt")

        # Параметры обучения
        epochs = config.get("epochs", 100)
        batch_size = config.get("batch_size", 16)
        learning_rate = config.get("learning_rate", 0.001)
        image_size = config.get("image_size", 640)

        # Запускаем обучение
        results = model.train(
            data=dataset_path,
            epochs=epochs,
            batch=batch_size,
            lr0=learning_rate,
            imgsz=image_size,
            device="cuda" if self._has_cuda() else "cpu",
            verbose=True
        )

        # Сохраняем модель
        model_path = f"/models/{self.model_id}_trained.pt"
        model.save(model_path)

        return {
            "status": "completed",
            "metrics": results.results_dict,
            "model_path": model_path
        }

    @staticmethod
    def _has_cuda() -> bool:
        """Проверка наличия CUDA"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    @staticmethod
    def _mask_to_rle(mask: np.ndarray) -> str:
        """Конвертация маски в RLE формат"""
        import base64
        import cv2

        # Простое RLE кодирование
        pixels = mask.flatten()
        rle = []
        prev = pixels[0]
        count = 1

        for p in pixels[1:]:
            if p == prev:
                count += 1
            else:
                rle.append(count)
                prev = p
                count = 1
        rle.append(count)

        # Кодируем в base64
        rle_bytes = np.array(rle, dtype=np.int32).tobytes()
        return base64.b64encode(rle_bytes).decode('utf-8')