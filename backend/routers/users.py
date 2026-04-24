# ============================================================
# Routes Utilisateurs Admin MobiTranz
# Fichier : backend/routers/users.py
# Description : Routes /users/* (CRUD Admin)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import structlog

from backend.database import get_db
from backend.models.user import User, UserStatus
from backend.services.auth_service import auth_service


logger = structlog.get_logger()
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list)
async def list_users(
    db: AsyncSession = Depends(get_db),
    role: str = None,
    status: str = None,
    limit: int = 50,
    offset: int = 0
):
    """Liste les utilisateurs avec filtres."""
    query = select(User)
    
    if role:
        try:
            from backend.models.user import UserRole
            u_role = UserRole(role)
            query = query.where(User.role == u_role)
        except ValueError:
            pass
    
    if status:
        try:
            u_status = UserStatus(status)
            query = query.where(User.status == u_status)
        except ValueError:
            pass
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Récupère un utilisateur."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    phone: str,
    email: str = None,
    password: str,
    role: str = "client",
    first_name: str = None,
    last_name: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Crée un utilisateur (admin only)."""
    # Check existing
    result = await db.execute(
        select(User).where(User.phone == phone)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Téléphone déjà utilisé"
        )
    
    from backend.models.user import UserRole
    
    user = User(
        phone=phone,
        email=email,
        password_hash=auth_service.hash_password(password),
        role=UserRole(role),
        status=UserStatus.ACTIVE,
        first_name=first_name,
        last_name=last_name,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    logger.info("Utilisateur créé (admin)", user_id=user.id, role=role)
    
    return user


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    email: str = None,
    first_name: str = None,
    last_name: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Met à jour un utilisateur."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    if email:
        user.email = email
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    logger.info("Utilisateur mis à jour", user_id=user_id)
    
    return user


@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Suspend un utilisateur."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    user.status = UserStatus.SUSPENDED
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    logger.warning("Utilisateur suspendu", user_id=user_id)
    
    return {"status": "suspended"}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Active/réactive un utilisateur."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    user.status = UserStatus.ACTIVE
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    logger.info("Utilisateur activé", user_id=user_id)
    
    return {"status": "active"}


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Soft-delete un utilisateur."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    user.status = UserStatus.DELETED
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    logger.info("Utilisateur supprimé", user_id=user_id)
    
    return {"status": "deleted"}