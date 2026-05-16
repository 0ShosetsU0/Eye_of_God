# backend/app/routers/datasets.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid
import os
from datetime import datetime

from app.database import get_db
from app.models import Project, Dataset, DatasetImage, User
from app.schemas import DatasetResponse
from app.dependencies import get_current_active_user, get_project_permission

router = APIRouter()


@router.get("/{project_id}/datasets", response_model=DatasetResponse)
async def get_dataset(
        project=Depends(get_project_permission),
        db: AsyncSession = Depends(get_db)
):
    """Получение информации о датасете проекта"""
    result = await db.execute(
        select(Dataset).where(Dataset.project_id == project.id)
    )
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return dataset


@router.post("/{project_id}/datasets/upload")
async def upload_images(
        project_id: str,
        files: list[UploadFile] = File(...),
        is_defect: bool = Form(False),
        defect_class: str = Form(None),
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """Загрузка изображений в датасет"""

    # Получаем или создаем датасет
    result = await db.execute(
        select(Dataset).where(Dataset.project_id == project_id)
    )
    dataset = result.scalar_one_or_none()

    if not dataset:
        dataset = Dataset(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name=f"Dataset_{datetime.now().strftime('%Y%m%d')}"
        )
        db.add(dataset)
        await db.flush()

    uploaded = []
    for file in files:
        # Сохраняем информацию об изображении
        image = DatasetImage(
            id=str(uuid.uuid4()),
            dataset_id=dataset.id,
            filename=file.filename,
            file_url=f"/temp/{file.filename}",  # Временный URL
            is_defect=is_defect,
            defect_class=defect_class if is_defect else None,
            file_size=file.size or 0
        )
        db.add(image)
        uploaded.append(image.filename)

    # Обновляем статистику датасета
    if is_defect:
        dataset.defect_samples += len(files)
    else:
        dataset.good_samples += len(files)
    dataset.total_images = dataset.good_samples + dataset.defect_samples

    if defect_class and defect_class not in dataset.defect_classes:
        dataset.defect_classes.append(defect_class)

    await db.commit()

    return {"uploaded": uploaded, "dataset_id": dataset.id}


@router.delete("/{project_id}/datasets/{image_id}")
async def delete_image(
        project_id: str,
        image_id: str,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """Удаление изображения из датасета"""

    result = await db.execute(
        select(DatasetImage).where(DatasetImage.id == image_id)
    )
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    await db.delete(image)
    await db.commit()

    return {"message": "Image deleted"}