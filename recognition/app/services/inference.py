# app/services/inference.py
import time
import uuid
import numpy as np
from typing import List
from ..api.schemas import PredictRequest, PredictResponse, Defect
from .model_manager import model_manager
from ..utils.image_utils import load_image


class InferenceService:
    """Сервис для выполнения инференса"""

    async def predict(self, request: PredictRequest) -> PredictResponse:
        """Выполнить инференс на изображении"""

        start_time = time.time()
        request_id = uuid.uuid4().hex[:16]

        # Загружаем модель
        model = await model_manager.get_model(request.model_id)
        if not model:
            raise ValueError(f"Model {request.model_id} not found")

        # Загружаем изображение
        image = await load_image(request.image)

        # Выполняем инференс
        defects = await model.predict(
            image=image,
            threshold=request.threshold,
            return_mask=request.return_mask
        )

        processing_time = (time.time() - start_time) * 1000

        return PredictResponse(
            request_id=request_id,
            model_id=request.model_id,
            defects=defects,
            processing_time_ms=processing_time,
            image_size=image.shape[:2]
        )

    async def predict_batch(
            self,
            images: List,
            model_id: str,
            threshold: float = 0.5
    ) -> List[PredictResponse]:
        """Пакетный инференс"""

        responses = []
        for image in images:
            request = PredictRequest(
                image=image,
                model_id=model_id,
                threshold=threshold
            )
            response = await self.predict(request)
            responses.append(response)

        return responses


inference_service = InferenceService()