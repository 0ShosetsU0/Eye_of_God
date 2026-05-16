# backend/app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserUpdate
from app.dependencies import get_current_active_user, get_current_admin_user

router = APIRouter()  # ЭТА СТРОКА ДОЛЖНА БЫТЬ


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: User = Depends(get_current_active_user)
):
    """Получение информации о текущем пользователе"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
        request: UserUpdate,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    """Обновление информации о текущем пользователе"""

    if request.full_name is not None:
        current_user.full_name = request.full_name
    if request.avatar_url is not None:
        current_user.avatar_url = request.avatar_url

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.get("/", response_model=list[UserResponse])
async def list_users(
        skip: int = 0,
        limit: int = 100,
        admin: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Список пользователей (только для администратора)"""

    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()

    return users