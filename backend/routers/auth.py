# ============================================================
# Routeur d'Authentification MobiTranz
# Fichier : backend/routers/auth.py
# Description : Routes /auth/* (login, register, refresh, biometric)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import structlog

from backend.config import settings
from backend.database import get_db
from backend.deps.auth_deps import get_current_user
from backend.schemas.auth import (
    UserLogin,
    UserRegister,
    TokenResponse,
    RefreshTokenRequest,
    TOTPEnable,
    TOTPDisable,
)
from backend.services.auth_service import auth_service
from backend.services.sms_service import sms_service
from backend.models.user import User, UserRole, UserStatus

logger = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
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

    access_token = auth_service.create_access_token(user.id, user.role.value)
    refresh_token = auth_service.create_refresh_token(user.id)

    logger.info("Utilisateur inscrit", user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authentifie un utilisateur.

    Valide les identifiants et retourne les tokens JWT.
    """
    logger.info("Connexion utilisateur", phone=data.phone)

    user = await auth_service.authenticate_user(db, data.phone, data.password)

    if not user:
        logger.warning("Échec connexion", phone=data.phone)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides"
        )

    if await auth_service.check_account_locked(db, user):
        logger.warning("Compte verrouillé", phone=data.phone)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Compte temporairement verrouillé",
        )

    await auth_service.reset_failed_attempts(db, user)

    access_token = auth_service.create_access_token(user.id, user.role.value)
    refresh_token = auth_service.create_refresh_token(user.id)

    logger.info("Connexion réussie", user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Rafraîchit les tokens JWT.

    Utilise le token de rafraîchissement pour obtenir
    une nouvelle paire de tokens.
    """
    payload = auth_service.verify_token(data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de rafraîchissement invalide",
        )

    user_id = payload.get("sub")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur inactif"
        )

    access_token = auth_service.create_access_token(user.id, user.role.value)
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
    current_user: User = Depends(get_current_user),
):
    """Active le 2FA TOTP pour un utilisateur."""
    logger.info("Activation TOTP", user_id=current_user.id)

    if not auth_service.verify_totp(data.secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Code TOTP invalide"
        )

    current_user.totp_secret = data.secret
    await db.commit()

    return {"message": "TOTP activé"}


@router.post("/totp/disable")
async def disable_totp(
    data: TOTPDisable,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Désactive le 2FA TOTP pour un utilisateur."""
    logger.info("Désactivation TOTP", user_id=current_user.id)

    if not auth_service.verify_totp(current_user.totp_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Code TOTP invalide"
        )

    current_user.totp_secret = None
    await db.commit()

    return {"message": "TOTP désactivé"}


@router.get("/totp/setup")
async def setup_totp(current_user: User = Depends(get_current_user)):
    """Génère la configuration TOTP."""
    secret = auth_service.generate_totp_secret()
    uri = auth_service.get_totp_uri(secret, current_user.phone)

    return {"secret": secret, "uri": uri}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    from backend.redis_client import redis_client
    from backend.config import settings

    token = credentials.credentials
    if redis_client.redis:
        import time
        ttl = settings.access_token_expire_minutes * 60
        await redis_client.redis.setex(f"token_blacklist:{token}", ttl, "1")

    logger.info("Déconnexion réussie", user_id=current_user.id)
    return {"message": "Déconnexion réussie"}


@router.post("/password-reset/request")
async def request_password_reset(phone: str, db: AsyncSession = Depends(get_db)):
    """Demande de réinitialisation du mot de passe.

    Envoie un code SMS à l'utilisateur.
    """
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()

    if user:
        code = auth_service.generate_reset_code()
        user.reset_code = code
        user.reset_code_expires = datetime.now(timezone.utc) + timedelta(minutes=10)
        await db.commit()
        await sms_service.send_sms(phone, f"Votre code de réinitialisation MobiTranz : {code}")
        logger.info("Code reset envoyé", user_id=user.id, phone=phone)

    return {"message": "Si le numéro existe, un code sera envoyé par SMS"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    phone: str, code: str, new_password: str, db: AsyncSession = Depends(get_db)
):
    """Confirme la réinitialisation du mot de passe."""
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé"
        )

    if not user.reset_code or user.reset_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Code invalide"
        )

    if not user.reset_code_expires or user.reset_code_expires < datetime.now(
        timezone.utc
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Code expiré"
        )

    user.password_hash = auth_service.hash_password(new_password)
    user.reset_code = None
    user.reset_code_expires = None
    await db.commit()

    logger.info("Mot de passe réinitialisé", user_id=user.id)

    return {"message": "Mot de passe mis à jour"}
