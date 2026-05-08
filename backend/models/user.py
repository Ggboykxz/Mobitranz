# ============================================================
# Modèle Utilisateur MobiTranz
# Fichier : backend/models/user.py
# Description : Table des utilisateurs (tous rôles)
# ============================================================

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from backend.database import Base


class UserRole(enum.Enum):
    """Rôles possibles pour les utilisateurs MobiTranz."""

    CLIENT = "client"
    DRIVER = "driver"
    ADMIN = "admin"
    MINISTRY = "ministry"


class UserStatus(enum.Enum):
    """Statuts possibles pour les utilisateurs."""

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class User(Base):
    """Modèle des utilisateurs MobiTranz.

    Gère les clients, conducteurs, administrateurs et utilisateurs ministry.
    Chaque utilisateur a un profil unique avec authentication.
    """

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)

    # Informations personnelles
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    kyc_verified = Column(Boolean, default=False)
    kyc_documents = Column(String(500), nullable=True)

    # Biométrie
    biometric_hash = Column(String(255), nullable=True)

    # Authentification
    totp_secret = Column(String(32), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

    # Métadonnées
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
    last_login = Column(DateTime, nullable=True)

    # Relations
    trips_as_client = relationship(
        "Trip", foreign_keys="Trip.client_ids", back_populates="clients"
    )
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        """Représentation textuelle de l'utilisateur."""
        return f"<User {self.phone} ({self.role.value})>"
