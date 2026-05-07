# ============================================================
# Service Portefeuille MobiTranz
# Fichier : backend/services/wallet_service.py
# Description : Gestion des wallets et transactions financières
# ============================================================

import enum
import uuid
from typing import Optional
from datetime import datetime, timezone, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, func, select, and_

from backend.database import Base
from backend.models.payment import PaymentStatus


logger = structlog.get_logger()


class WalletStatus(enum.Enum):
    """Statuts possibles d'un wallet."""
    ACTIVE = "active"
    FROZEN = "frozen"
    SUSPENDED = "suspended"


class WalletOperationType(enum.Enum):
    """Types d'opérations sur le wallet."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    BONUS = "bonus"
    FEE = "fee"


class Wallet(Base):
    """Modèle du wallet MobiTranz.
    
    Chaque utilisateur (client ou driver) peut avoir un wallet
    pour stocker des fonds et effectuer des transactions.
    """
    
    __tablename__ = "wallets"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True
    )
    balance = Column(Integer, default=0)
    frozen_balance = Column(Integer, default=0)
    status = Column(
        Enum(WalletStatus),
        default=WalletStatus.ACTIVE,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )


class WalletOperation(Base):
    """Modèle des opérations wallet.
    
    Enregistre chaque transaction sur un wallet.
    """
    
    __tablename__ = "wallet_operations"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    wallet_id = Column(
        String(36),
        ForeignKey("wallets.id"),
        nullable=False,
        index=True
    )
    operation_type = Column(
        Enum(WalletOperationType),
        nullable=False
    )
    amount = Column(Integer, nullable=False)
    reference = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
    status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class WalletService:
    """Service de gestion des wallets MobiTranz.
    
    Gère les dépôts, retraits, paiements et soldes.
    """
    
    async def create_wallet(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Wallet:
        """Crée un nouveau wallet pour un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            Wallet: Wallet créé
        """
        wallet = Wallet(
            user_id=user_id,
            balance=0,
            frozen_balance=0,
            status=WalletStatus.ACTIVE
        )
        
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
        
        logger.info("Wallet créé", user_id=user_id, wallet_id=wallet.id)
        
        return wallet
    
    async def get_wallet(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Optional[Wallet]:
        """Récupère le wallet d'un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            Wallet: Wallet de l'utilisateur ou None
        """
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_balance(
        self,
        db: AsyncSession,
        user_id: str
    ) -> int:
        """Récupère le solde disponible d'un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            int: Solde disponible en FCFA
        """
        wallet = await self.get_wallet(db, user_id)
        
        if not wallet:
            return 0
        
        return wallet.balance
    
    async def deposit(
        self,
        db: AsyncSession,
        user_id: str,
        amount: int,
        reference: str,
        description: str = None
    ) -> WalletOperation:
        """Effectue un dépôt sur le wallet.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            amount: Montant en FCFA
            reference: Référence externe du dépôt
            description: Description de l'opération
            
        Returns:
            WalletOperation: Opération créée
        """
        wallet = await self.get_wallet(db, user_id)
        
        if not wallet:
            wallet = await self.create_wallet(db, user_id)
        
        wallet.balance += amount
        
        operation = WalletOperation(
            wallet_id=wallet.id,
            operation_type=WalletOperationType.DEPOSIT,
            amount=amount,
            reference=reference,
            description=description or f"Dépôt {reference}",
            status=PaymentStatus.COMPLETED
        )
        
        db.add(operation)
        await db.commit()
        await db.refresh(operation)
        
        logger.info(
            "Dépôt effectué",
            user_id=user_id,
            amount=amount,
            reference=reference
        )
        
        return operation
    
    async def withdraw(
        self,
        db: AsyncSession,
        user_id: str,
        amount: int,
        reference: str,
        description: str = None
    ) -> Optional[WalletOperation]:
        """Effectue un retrait sur le wallet.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            amount: Montant en FCFA
            reference: Référence externe du retrait
            description: Description de l'opération
            
        Returns:
            WalletOperation: Opération créée ou None si fonds insuffisants
        """
        wallet = await self.get_wallet(db, user_id)
        
        if not wallet or wallet.balance < amount:
            logger.warning("Fonds insuffisants pour retrait", user_id=user_id, amount=amount)
            return None
        
        wallet.balance -= amount
        
        operation = WalletOperation(
            wallet_id=wallet.id,
            operation_type=WalletOperationType.WITHDRAWAL,
            amount=-amount,
            reference=reference,
            description=description or f"Retrait {reference}",
            status=PaymentStatus.COMPLETED
        )
        
        db.add(operation)
        await db.commit()
        await db.refresh(operation)
        
        logger.info(
            "Retrait effectué",
            user_id=user_id,
            amount=amount,
            reference=reference
        )
        
        return operation
    
    async def freeze_funds(
        self,
        db: AsyncSession,
        user_id: str,
        amount: int,
        reference: str,
        description: str = None
    ) -> bool:
        """Bloque des fonds pour un paiement différé.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            amount: Montant à bloquer en FCFA
            reference: Référence du blocage
            description: Description de l'opération
            
        Returns:
            bool: True si le blocage a réussi
        """
        wallet = await self.get_wallet(db, user_id)
        
        if not wallet or wallet.balance < amount:
            return False
        
        wallet.balance -= amount
        wallet.frozen_balance += amount
        
        operation = WalletOperation(
            wallet_id=wallet.id,
            operation_type=WalletOperationType.PAYMENT,
            amount=-amount,
            reference=reference,
            description=description or f"Fonds bloqués {reference}",
            status=PaymentStatus.PROCESSING
        )
        
        db.add(operation)
        await db.commit()
        
        logger.info(
            "Fonds bloqués",
            user_id=user_id,
            amount=amount,
            reference=reference
        )
        
        return True
    
    async def release_funds(
        self,
        db: AsyncSession,
        user_id: str,
        amount: int,
        reference: str,
        to_user_id: str
    ) -> bool:
        """Libère les fonds bloqués et les transfère à un autre utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur source
            amount: Montant à libérer en FCFA
            reference: Référence de l'opération
            to_user_id: ID de l'utilisateur destinataire
            
        Returns:
            bool: True si le transfert a réussi
        """
        wallet = await self.get_wallet(db, user_id)
        
        if not wallet or wallet.frozen_balance < amount:
            return False
        
        wallet.frozen_balance -= amount
        
        to_wallet = await self.get_wallet(db, to_user_id)
        
        if not to_wallet:
            to_wallet = await self.create_wallet(db, to_user_id)
        
        to_wallet.balance += amount
        
        operation = WalletOperation(
            wallet_id=wallet.id,
            operation_type=WalletOperationType.PAYMENT,
            amount=-amount,
            reference=reference,
            description=f"Paiement vers {to_user_id}",
            status=PaymentStatus.COMPLETED
        )
        
        db.add(operation)
        await db.commit()
        
        logger.info(
            "Fonds transférés",
            from_user=user_id,
            to_user=to_user_id,
            amount=amount
        )
        
        return True
    
    async def get_operations(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 50
    ) -> list:
        """Récupère l'historique des opérations d'un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            limit: Nombre maximum d'opérations
            
        Returns:
            list: Liste des opérations
        """
        wallet = await self.get_wallet(db, user_id)
        
        if not wallet:
            return []
        
        result = await db.execute(
            select(WalletOperation)
            .where(WalletOperation.wallet_id == wallet.id)
            .order_by(WalletOperation.created_at.desc())
            .limit(limit)
        )
        
        return result.scalars().all()
    
    async def check_deferred_payment_eligibility(
        self,
        db: AsyncSession,
        user_id: str
    ) -> dict:
        """Vérifie si un utilisateur est éligible au paiement à l'arrivée.
        
        Conditions selon cahier des charges :
        - Minimum 5 trajets effectués
        - Compte de plus de 30 jours
        - Aucun paiement échoué récent
        - KYC vérifié
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            dict: Éléments de vérification et résultat
        """
        from backend.models.user import User, UserRole
        from backend.models.trip import Trip, TripStatus
        from backend.models.payment import Payment, PaymentStatus
        
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {"eligible": False, "reason": "Utilisateur non trouvé"}
        
        if not user.kyc_verified:
            return {"eligible": False, "reason": "KYC non vérifié"}
        
        account_age = datetime.now(timezone.utc) - user.created_at
        if account_age.days < 30:
            return {
                "eligible": False,
                "reason": f"Compte trop récent ({account_age.days} jours, minimum 30)"
            }
        
        if user.role != UserRole.CLIENT:
            return {"eligible": False, "reason": "Réservé aux clients"}
        
        result = await db.execute(
            select(func.count(Trip.id))
            .where(
                and_(
                    Trip.client_ids.contains(user_id),
                    Trip.status == TripStatus.COMPLETED
                )
            )
        )
        completed_trips = result.scalar() or 0
        
        if completed_trips < 5:
            return {
                "eligible": False,
                "reason": f"Trajets insuffisants ({completed_trips}/5)"
            }
        
        result = await db.execute(
            select(func.count(Payment.id))
            .where(
                and_(
                    Payment.client_id == user_id,
                    Payment.status == PaymentStatus.FAILED,
                    Payment.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
                )
            )
        )
        failed_payments = result.scalar() or 0
        
        if failed_payments > 0:
            return {
                "eligible": False,
                "reason": f"Paiements échoués récents ({failed_payments})"
            }
        
        return {
            "eligible": True,
            "completed_trips": completed_trips,
            "account_age_days": account_age.days
        }


wallet_service = WalletService()