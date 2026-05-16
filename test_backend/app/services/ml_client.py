# backend/app/services/ml_client.py
import httpx
from typing import List, Dict, Any, Optional
from app.config import settings


class MLClient:
    """Клиент для взаимодействия с ML-сервисом"""

    def __init__(self):
        self.base_url = settings.ML_SERVICE_URL
        self.timeout = settings.ML_SERVICE_TIMEOUT

    async def predict(self, model_id: str, image: str, threshold: float = 0.5) -> Dict[str, Any]:
        """Отправка запроса на инференс"""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/predict",
                json={
                    "model_id": model_id,
                    "image": image,
                    "threshold": threshold,
                    "return_mask": True
                }
            )
            response.raise_for_status()
            return response.json()

    async def train(self, project_id: str, dataset_url: str, model_type: str, config: dict) -> Dict[str, Any]:
        """Запуск обучения на ML-сервисе"""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/train",
                json={
                    "project_id": project_id,
                    "dataset_url": dataset_url,
                    "model_type": model_type,
                    **config
                }
            )
            response.raise_for_status()
            return response.json()

    async def get_training_status(self, task_id: str) -> Dict[str, Any]:
        """Получение статуса обучения"""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/train/{task_id}/status"
            )
            response.raise_for_status()
            return response.json()

    async def get_models(self, project_id: Optional[str] = None) -> List[Dict]:
        """Список моделей"""

        params = {}
        if project_id:
            params["project_id"] = project_id

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/models",
                params=params
            )
            response.raise_for_status()
            return response.json().get("models", [])

    async def get_model(self, model_id: str) -> Dict:
        """Информация о модели"""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/models/{model_id}"
            )
            response.raise_for_status()
            return response.json()

    async def delete_model(self, model_id: str) -> bool:
        """Удаление модели"""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                f"{self.base_url}/api/v1/models/{model_id}"
            )
            return response.status_code == 200


ml_client = MLClient()