# ============================================================
# Service d'Authentification MobiTranz
# Fichier : backend/services/auth_service.py
# Description : JWT, OTP, biométrie, 2FA TOTP
# ============================================================

from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib
import jwt
from passlib.context import CryptContext
import pyotp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import settings
from backend.models.user import User, UserStatus


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class AuthService:
    """Service d'authentification MobiTranz.
    
    Gère la création et validation des tokens JWT,
    l'authentification par mot de passe, OTP et biométrie.
    """
    
    def hash_password(self, password: str) -> str:
        """Hache un mot de passe avec bcrypt.
        
        Args:
            password: Mot de passe en clair
            
        Returns:
            str: Hash bcrypt du mot de passe
        """
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe contre son hash.
        
        Args:
            plain_password: Mot de passe en clair
            hashed_password: Hash à vérifier
            
        Returns:
            bool: True si le mot de passe est correct
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self,
        user_id: str,
        role: str,
        ip_address: Optional[str] = None
    ) -> str:
        """Crée un token d'accès JWT.
        
        Args:
            user_id: Identifiant de l'utilisateur
            role: Rôle de l'utilisateur
            ip_address: Adresse IP optionnelle pour le binding
            
        Returns:
            str: Token JWT encodé
        """
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        
        payload = {
            "sub": user_id,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }
        
        if ip_address:
            payload["ip"] = ip_address
        
        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.jwt_algorithm
        )
    
    def create_refresh_token(self, user_id: str) -> str:
        """Crée un token de rafraîchissement JWT.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            str: Token JWT de rafraîchissement
        """
        expire = datetime.utcnow() + timedelta(
            days=settings.refresh_token_expire_days
        )
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "nonce": secrets.token_hex(16),
        }
        
        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.jwt_algorithm
        )
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Vérifie et décode un token JWT.
        
        Args:
            token: Token JWT à vérifier
            
        Returns:
            dict: Payload du token ou None si invalide
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    async def authenticate_user(
        self,
        db: AsyncSession,
        phone: str,
        password: str
    ) -> Optional[User]:
        """Authentifie un utilisateur par téléphone et mot de passe.
        
        Args:
            db: Session de base de données
            phone: Numéro de téléphone
            password: Mot de passe
            
        Returns:
            User: Utilisateur authentifié ou None
        """
        result = await db.execute(
            select(User).where(User.phone == phone)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        if user.status != UserStatus.ACTIVE:
            return None
        
        return user
    
    def generate_totp_secret(self) -> str:
        """Génère un secret TOTP pour 2FA.
        
        Returns:
            str: Secret TOTP (base32)
        """
        return pyotp.random_base32()
    
    def get_totp_uri(self, secret: str, username: str) -> str:
        """Génère l'URI TOTP pour configuration Google Authenticator.
        
        Args:
            secret: Secret TOTP
            username: Nom d'utilisateur
            
        Returns:
            str: URI otpauth://
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name="MobiTranz")
    
    def verify_totp(self, secret: str, code: str) -> bool:
        """Vérifie un code TOTP.
        
        Args:
            secret: Secret TOTP de l'utilisateur
            code: Code à 6 chiffres
            
        Returns:
            bool: True si le code est valide
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
    
    def hash_biometric(self, biometric_data: str) -> str:
        """Hache des données biométriques.
        
        Args:
            biometric_data: Données biométriques brutes
            
        Returns:
            str: Hash des données biométriques
        """
        return hashlib.sha256(biometric_data.encode()).hexdigest()
    
    def verify_biometric(
        self,
        biometric_data: str,
        stored_hash: str
    ) -> bool:
        """Vérifie des données biométriques contre un hash.
        
        Args:
            biometric_data: Données biométriques à vérifier
            stored_hash: Hash stocké
            
        Returns:
            bool: True si les données correspondent
        """
        return self.hash_biometric(biometric_data) == stored_hash
    
    async def check_account_locked(
        self,
        db: AsyncSession,
        user: User
    ) -> bool:
        """Vérifie si un compte est verrouillé.
        
        Args:
            db: Session de base de données
            user: Utilisateur à vérifier
            
        Returns:
            bool: True si le compte est verrouillé
        """
        if user.locked_until and user.locked_until > datetime.utcnow():
            return True
        return False
    
    async def increment_failed_attempts(
        self,
        db: AsyncSession,
        user: User
    ):
        """Incrémente le nombre de tentatives échouées.
        
        Args:
            db: Session de base de données
            user: Utilisateur
        """
        user.failed_login_attempts += 1
        
        if user.failed_login_attempts >= 3:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        await db.commit()
    
    async def reset_failed_attempts(
        self,
        db: AsyncSession,
        user: User
    ):
        """Réinitialise les tentatives échouées après succès.
        
        Args:
            db: Session de base de données
            user: Utilisateur
        """
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        await db.commit()


auth_service = AuthService()