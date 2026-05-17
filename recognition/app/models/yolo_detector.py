# recognition/app/models/yolo_detector.py
import numpy as np
from typing import List, Optional, Callable
from ultralytics import YOLO
import asyncio
from .base import BaseModel


class YOLODetector(BaseModel):
    def __init__(self, model_id: str, config: dict):
        super().__init__(model_id, "yolo")
        self.config = config
        self.model_path = config.get("model_path", "yolov8n.pt")
        self._model = None

    async def load(self):
        """Загрузка модели в отдельном потоке"""
        await asyncio.to_thread(self._load_sync)
        self.is_loaded = True

    def _load_sync(self):
        self._model = YOLO(self.model_path)

    async def unload(self):
        self._model = None
        self.is_loaded = False

    async def predict(
            self,
            image: np.ndarray,
            threshold: float = 0.5,
            return_mask: bool = False
    ) -> List[dict]:
        """Инференс на изображении"""
        if not self.is_loaded:
            await self.load()

        def predict_sync():
            results = self._model(image, conf=threshold, verbose=False)
            return self._process_results(results, return_mask)

        return await asyncio.to_thread(predict_sync)

    def _process_results(self, results, return_mask):
        defects = []
        if results and len(results) > 0:
            result = results[0]
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]
                    confidence = float(box.conf[0])

                    defect = {
                        "class_name": class_name,
                        "confidence": confidence,
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "area": (x2 - x1) * (y2 - y1),
                        "centroid": [(x1 + x2) / 2, (y1 + y2) / 2]
                    }

                    if return_mask and hasattr(box, 'mask') and box.mask is not None:
                        mask = box.mask.data[0].cpu().numpy()
                        defect["mask"] = self._mask_to_rle(mask)

                    defects.append(defect)
        return defects

    async def train(self, dataset_path: str, callback: Optional[Callable] = None):
        """Обучение модели"""

        def train_sync():
            model = YOLO(self.model_path)
            results = model.train(
                data=dataset_path,
                epochs=self.config.get("epochs", 100),
                batch=self.config.get("batch_size", 16),
                lr0=self.config.get("learning_rate", 0.001),
                imgsz=self.config.get("image_size", 640),
                device="cuda" if self._has_cuda() else "cpu",
                verbose=True
            )
            return results.results_dict

        return await asyncio.to_thread(train_sync)

    @staticmethod
    def _has_cuda():
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    @staticmethod
    def _mask_to_rle(mask: np.ndarray) -> str:
        import base64
        import cv2
        _, buffer = cv2.imencode('.png', mask.astype(np.uint8) * 255)
        return base64.b64encode(buffer).decode('utf-8')