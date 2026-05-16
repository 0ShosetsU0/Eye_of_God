# app/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import uvicorn
import uuid
import asyncio
import random
from datetime import datetime

# Отключаем предупреждения protected_namespace
BaseModel.model_config = ConfigDict(protected_namespaces=())


# ============ Схемы данных ============
class Defect(BaseModel):
    class_name: str
    confidence: float
    bbox: Optional[List[float]] = None
    mask: Optional[str] = None
    area: Optional[float] = None
    centroid: Optional[List[float]] = None


class PredictRequest(BaseModel):
    image: str
    model_id: str
    threshold: float = 0.5
    return_mask: bool = False


class PredictResponse(BaseModel):
    request_id: str
    model_id: str
    defects: List[Defect]
    processing_time_ms: float
    image_size: List[int]


class TrainRequest(BaseModel):
    project_id: str
    dataset_url: str
    model_type: str = "auto"
    epochs: int = 100
    batch_size: int = 16
    learning_rate: float = 0.001
    image_size: int = 640


class TrainResponse(BaseModel):
    task_id: str
    project_id: str
    status: str
    status_url: str
    created_at: datetime


# ============ Конфигурация ============
class Settings:
    SERVICE_NAME = "ml-service"
    SERVICE_HOST = "0.0.0.0"
    SERVICE_PORT = 8001
    DEBUG = True
    USE_MOCK = True
    DEV_MODE = True


settings = Settings()


# ============ Мок-модель ============
class MockModel:
    def __init__(self, model_id: str, model_type: str = "mock"):
        self.model_id = model_id
        self.model_type = model_type
        self.is_loaded = True
        self.defect_classes = ["царапина", "скол", "вмятина", "загрязнение", "трещина"]

    async def predict(self, image, threshold, return_mask):
        defects = []
        num_defects = random.randint(0, 3)

        for _ in range(num_defects):
            x1 = random.uniform(0, 400)
            y1 = random.uniform(0, 400)
            x2 = x1 + random.uniform(50, 200)
            y2 = y1 + random.uniform(50, 200)

            defect = Defect(
                class_name=random.choice(self.defect_classes),
                confidence=random.uniform(0.6, 0.98),
                bbox=[x1, y1, x2, y2],
                area=(x2 - x1) * (y2 - y1),
                centroid=[(x1 + x2) / 2, (y1 + y2) / 2]
            )
            defects.append(defect)

        return defects

    async def train(self, dataset_path, config):
        await asyncio.sleep(2)
        return {
            "status": "completed",
            "metrics": {
                "mAP": random.uniform(0.85, 0.95),
                "precision": random.uniform(0.88, 0.96),
                "recall": random.uniform(0.82, 0.94),
                "f1": random.uniform(0.85, 0.95)
            }
        }


# ============ Менеджер моделей ============
class ModelManager:
    def __init__(self):
        self._models = {}
        self._model_info = {}

    async def get_model(self, model_id: str):
        if model_id not in self._models:
            return None
        return self._models[model_id]

    async def create_model(self, model_type: str, project_id: str):
        model_id = f"{project_id}_{uuid.uuid4().hex[:8]}"
        model = MockModel(model_id, model_type)
        self._models[model_id] = model
        self._model_info[model_id] = {
            "model_id": model_id,
            "project_id": project_id,
            "model_type": model_type,
            "version": 1,
            "created_at": datetime.now(),
            "metrics": {},
            "is_active": False
        }
        return model

    async def activate_model(self, model_id: str):
        if model_id in self._model_info:
            project_id = self._model_info[model_id]["project_id"]
            for mid, info in self._model_info.items():
                if info["project_id"] == project_id:
                    info["is_active"] = False
            self._model_info[model_id]["is_active"] = True
            return True
        return False


model_manager = ModelManager()


# ============ Сервис инференса ============
class InferenceService:
    async def predict(self, request: PredictRequest) -> PredictResponse:
        import time
        start_time = time.time()

        model = await model_manager.get_model(request.model_id)
        if not model:
            raise ValueError(f"Model {request.model_id} not found")

        defects = await model.predict(None, request.threshold, request.return_mask)

        processing_time = (time.time() - start_time) * 1000

        return PredictResponse(
            request_id=uuid.uuid4().hex[:16],
            model_id=request.model_id,
            defects=defects,
            processing_time_ms=processing_time,
            image_size=[640, 480]
        )


inference_service = InferenceService()


# ============ Сервис обучения ============
class TrainingService:
    def __init__(self):
        self._tasks = {}

    async def start_training(self, request: TrainRequest, background_tasks):
        task_id = uuid.uuid4().hex[:16]

        self._tasks[task_id] = {
            "task_id": task_id,
            "project_id": request.project_id,
            "status": "queued",
            "created_at": datetime.now(),
            "progress": 0
        }

        background_tasks.add_task(self._run_training, task_id, request)

        return TrainResponse(
            task_id=task_id,
            project_id=request.project_id,
            status="queued",
            status_url=f"/api/v1/train/{task_id}/status",
            created_at=datetime.now()
        )

    async def _run_training(self, task_id: str, request: TrainRequest):
        try:
            self._tasks[task_id]["status"] = "preparing"
            self._tasks[task_id]["progress"] = 10
            await asyncio.sleep(0.5)

            model = await model_manager.create_model(request.model_type, request.project_id)

            self._tasks[task_id]["status"] = "training"
            self._tasks[task_id]["progress"] = 20
            self._tasks[task_id]["model_id"] = model.model_id

            for epoch in range(min(request.epochs, 10)):
                await asyncio.sleep(0.3)
                progress = 20 + (epoch + 1) * 7
                self._tasks[task_id]["progress"] = min(progress, 95)

            result = await model.train(request.dataset_url, {
                "epochs": request.epochs,
                "batch_size": request.batch_size,
                "learning_rate": request.learning_rate
            })

            await model_manager.activate_model(model.model_id)

            self._tasks[task_id]["status"] = "completed"
            self._tasks[task_id]["progress"] = 100
            self._tasks[task_id]["metrics"] = result.get("metrics", {})

        except Exception as e:
            self._tasks[task_id]["status"] = "failed"
            self._tasks[task_id]["error"] = str(e)

    async def get_status(self, task_id: str):
        return self._tasks.get(task_id)


training_service = TrainingService()

# ============ FastAPI приложение ============
app = FastAPI(
    title="DefectVision ML Service",
    description="ML сервис для обнаружения дефектов (Mock Mode)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "mock_mode": settings.USE_MOCK,
        "status": "running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "models_count": len(model_manager._models),
        "mock_mode": settings.USE_MOCK
    }


@app.post("/api/v1/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    try:
        return await inference_service.predict(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/train", response_model=TrainResponse)
async def train(request: TrainRequest, background_tasks: BackgroundTasks):
    try:
        return await training_service.start_training(request, background_tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/train/{task_id}/status")
async def get_training_status(task_id: str):
    status = await training_service.get_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status


@app.get("/api/v1/models")
async def list_models(project_id: Optional[str] = None):
    models = model_manager.list_models(project_id) if hasattr(model_manager, 'list_models') else []
    return {"models": models}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG
    )