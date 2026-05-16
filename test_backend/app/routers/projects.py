# backend/app/routers/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.database import get_db
from app.models import Project, User, Dataset
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.dependencies import get_current_active_user, get_project_permission

router = APIRouter()


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """Список проектов пользователя"""

    query = select(Project).where(Project.owner_id == current_user.id)
    result = await db.execute(query.offset(skip).limit(limit))
    projects = result.scalars().all()

    # Добавляем статистику датасетов
    for project in projects:
        dataset_result = await db.execute(
            select(func.count(Dataset.id)).where(Dataset.project_id == project.id)
        )
        project.dataset_stats = {"total_images": dataset_result.scalar() or 0}

    return projects


@router.post("/", response_model=ProjectResponse)
async def create_project(
        request: ProjectCreate,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """Создание нового проекта"""

    project = Project(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        owner_id=current_user.id
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
        project=Depends(get_project_permission)
):
    """Получение информации о проекте"""
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
        request: ProjectUpdate,
        project=Depends(get_project_permission),
        db: AsyncSession = Depends(get_db)
):
    """Обновление проекта"""

    if request.name is not None:
        project.name = request.name
    if request.description is not None:
        project.description = request.description
    if request.status is not None:
        project.status = request.status

    await db.commit()
    await db.refresh(project)

    return project


@router.delete("/{project_id}")
async def delete_project(
        project=Depends(get_project_permission),
        db: AsyncSession = Depends(get_db)
):
    """Удаление проекта"""

    await db.delete(project)
    await db.commit()

    return {"message": "Project deleted successfully"}