# ============================================================
# Dépendances d'Authentification
# Fichier : backend/deps/auth_deps.py
# Description : Dépendances FastAPI pour JWT et auth
# ============================================================

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import settings
from backend.database import get_db
from backend.models.user import User, UserStatus


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Retourne l'utilisateur courant depuis le token JWT.
    
    Args:
        credentials: Token Bearer JWT
        db: Session BD
        
    Returns:
        User: Utilisateur authentifié
        
    Raises:
        HTTPException: Si token invalide ou utilisateur inactif
    """
    from backend.services.auth_service import auth_service
    
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Type de token incorrect",
        )
    
    user_id = payload.get("sub")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte utilisateur inactif",
        )
    
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Retourne l'utilisateur courant en vérifiant qu'il est admin.
    
    Args:
        current_user: Utilisateur authentifié
        
    Returns:
        User: Utilisateur admin
        
    Raises:
        HTTPException: Si pas admin
    """
    from backend.models.user import UserRole
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs",
        )
    
    return current_user


async def get_current_ministry(
    current_user: User = Depends(get_current_user),
) -> User:
    """Retourne l'utilisateur courant en vérifiant qu'il est ministère.
    
    Args:
        current_user: Utilisateur authentifié
        
    Returns:
        User: Utilisateur ministère
        
    Raises:
        HTTPException: Si pas ministère
    """
    from backend.models.user import UserRole
    
    if current_user.role != UserRole.MINISTRY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé au Ministère",
        )
    
    return current_user