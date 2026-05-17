# recognition/app/main.py
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import router
from app.services.model_manager import model_manager
from app.services.task_queue import task_queue


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Старт
    print(f"Starting ML Service v{settings.VERSION}")
    await model_manager.initialize()
    await task_queue.start()
    yield
    # Стоп
    await model_manager.shutdown()
    await task_queue.stop()


app = FastAPI(
    title="DefectVision ML Service",
    description="ML Service for defect detection with YOLOv8, Anomalib, SAM",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    # Исправлено: используем существующий атрибут
    models_loaded = len(model_manager._models) if hasattr(model_manager, '_models') else 0
    return {"status": "healthy", "models_loaded": models_loaded}


@app.get("/")
async def root():
    return {
        "service": "DefectVision ML Service",
        "version": settings.VERSION,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)