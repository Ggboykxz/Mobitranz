# ============================================================
# Routeur d'Authentification MobiTranz
# Fichier : backend/routers/auth.py
# Description : Routes /auth/* (login, register, refresh, biometric)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from backend.database import get_db
from backend.schemas.auth import (
    UserLogin,
    UserRegister,
    TokenResponse,
    RefreshTokenRequest,
    TOTPEnable,
    TOTPDisable,
)
from backend.services.auth_service import auth_service
from backend.models.user import User, UserRole, UserStatus


logger = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Inscrit un nouvel utilisateur.
    
    Crée un nouveau compte utilisateur avec téléphone et mot de passe.
    """
    logger.info("Inscription utilisateur", phone=data.phone)
    
    user = User(
        phone=data.phone,
        email=data.email,
        password_hash=auth_service.hash_password(data.password),
        role=UserRole.CLIENT,
        status=UserStatus.ACTIVE,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    access_token = auth_service.create_access_token(
        user.id,
        user.role.value
    )
    refresh_token = auth_service.create_refresh_token(user.id)
    
    logger.info("Utilisateur inscrit", user_id=user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authentifie un utilisateur.
    
    Valide les identifiants et retourne les tokens JWT.
    """
    logger.info("Connexion utilisateur", phone=data.phone)
    
    user = await auth_service.authenticate_user(
        db,
        data.phone,
        data.password
    )
    
    if not user:
        logger.warning("Échec connexion", phone=data.phone)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides"
        )
    
    if await auth_service.check_account_locked(db, user):
        logger.warning("Compte verrouillé", phone=data.phone)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Compte temporairement verrouillé"
        )
    
    await auth_service.reset_failed_attempts(db, user)
    
    access_token = auth_service.create_access_token(
        user.id,
        user.role.value
    )
    refresh_token = auth_service.create_refresh_token(user.id)
    
    logger.info("Connexion réussie", user_id=user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Rafraîchit les tokens JWT.
    
    Utilise le token de rafraîchissement pour obtenir
    une nouvelle paire de tokens.
    """
    payload = auth_service.verify_token(data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de rafraîchissement invalide"
        )
    
    user_id = payload.get("sub")
    
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur inactif"
        )
    
    access_token = auth_service.create_access_token(
        user.id,
        user.role.value
    )
    refresh_token = auth_service.create_refresh_token(user.id)
    
    logger.info("Tokens rafraîchis", user_id=user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/totp/enable")
async def enable_totp(
    data: TOTPEnable,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """Active le 2FA TOTP pour un utilisateur."""
    logger.info("Activation TOTP", user_id=current_user.id)
    
    if not auth_service.verify_totp(data.secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code TOTP invalide"
        )
    
    current_user.totp_secret = data.secret
    await db.commit()
    
    return {"message": "TOTP activé"}


@router.post("/totp/disable")
async def disable_totp(
    data: TOTPDisable,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lambda: None)
):
    """Désactive le 2FA TOTP pour un utilisateur."""
    logger.info("Désactivation TOTP", user_id=current_user.id)
    
    if not auth_service.verify_totp(current_user.totp_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code TOTP invalide"
        )
    
    current_user.totp_secret = None
    await db.commit()
    
    return {"message": "TOTP désactivé"}


@router.get("/totp/setup")
async def setup_totp(
    current_user: User = Depends(lambda: None)
):
    """Génère la configuration TOTP."""
    secret = auth_service.generate_totp_secret()
    uri = auth_service.get_totp_uri(secret, current_user.phone)
    
    return {"secret": secret, "uri": uri}