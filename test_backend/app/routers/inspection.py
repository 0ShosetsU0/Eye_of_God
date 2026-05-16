# backend/app/routers/inspection.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import base64
from datetime import datetime

from app.database import get_db
from app.models import Project, Inspection, Feedback, User
from app.schemas import InspectRequest, InspectResponse, Defect, FeedbackRequest
from app.dependencies import get_current_active_user, get_project_permission
from app.services.ml_client import ml_client

router = APIRouter()


@router.post("/single", response_model=InspectResponse)
async def inspect_image(
        request: InspectRequest,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """Инспекция одного изображения"""

    # Проверяем проект
    result = await db.execute(select(Project).where(Project.id == request.project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Получаем активную модель
    if not project.active_model_id:
        raise HTTPException(status_code=400, detail="No active model found")

    # Отправляем запрос к ML-сервису
    ml_result = await ml_client.predict(
        model_id=project.active_model_id,
        image=request.image,
        threshold=request.threshold
    )

    # Сохраняем результат
    inspection = Inspection(
        id=str(uuid.uuid4()),
        project_id=request.project_id,
        user_id=current_user.id,
        image_url=request.image if request.image.startswith("http") else "uploaded",
        defects=ml_result.get("defects", []),
        processing_time_ms=ml_result.get("processing_time_ms", 0)
    )
    db.add(inspection)
    await db.commit()
    await db.refresh(inspection)

    defects = [Defect(**d) for d in ml_result.get("defects", [])]

    return InspectResponse(
        id=inspection.id,
        project_id=inspection.project_id,
        defects=defects,
        processing_time_ms=inspection.processing_time_ms,
        image_url=inspection.image_url,
        result_url=inspection.result_url or "",
        created_at=inspection.created_at
    )


@router.post("/upload")
async def inspect_upload(
        project_id: str = Form(...),
        image: UploadFile = File(...),
        threshold: float = Form(0.5),
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """Инспекция загруженного изображения"""

    # Читаем изображение в base64
    content = await image.read()
    image_base64 = base64.b64encode(content).decode('utf-8')

    # Создаем запрос
    request = InspectRequest(
        project_id=project_id,
        image=f"data:image/{image.content_type.split('/')[-1]};base64,{image_base64}",
        threshold=threshold
    )

    return await inspect_image(request, current_user, db)


@router.post("/feedback", response_model=dict)
async def send_feedback(
        request: FeedbackRequest,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """Отправка обратной связи о результате"""

    # Проверяем существование инспекции
    result = await db.execute(
        select(Inspection).where(Inspection.id == request.inspection_id)
    )
    inspection = result.scalar_one_or_none()

    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    # Создаем запись обратной связи
    feedback = Feedback(
        id=str(uuid.uuid4()),
        inspection_id=request.inspection_id,
        user_id=current_user.id,
        is_correct=request.is_correct,
        corrected_defects=[d.model_dump() for d in request.corrected_defects] if request.corrected_defects else None,
        comment=request.comment
    )
    db.add(feedback)
    await db.commit()

    return {"message": "Feedback saved"}