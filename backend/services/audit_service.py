# ============================================================
# Service d'Audit MobiTranz
# Fichier : backend/services/audit_service.py
# Description : Journalisation des actions pour conformité et sécurité
# ============================================================

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.audit_log import AuditLog

logger = structlog.get_logger()


class AuditService:
    """Service d'audit MobiTranz.

    Enregistre chaque action significative dans le système
    pour la conformité, la sécurité et le suivi.
    """

    async def log_action(
        self,
        db: AsyncSession,
        user_id: str,
        action: str,
        resource: str,
        ip_address: str = None,
        user_agent: str = None,
        result: str = "success",
        data: dict = None,
    ) -> AuditLog:
        """Enregistre une action dans l'audit log.

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            action: Type d'action (CREATE, UPDATE, DELETE, etc.)
            resource: Ressource touchée (users, trips, payments, etc.)
            ip_address: Adresse IP du client
            user_agent: User agent du client
            result: Résultat de l'action (success, failure, etc.)
            data: Données supplémentaires (sérialisées en JSON)

        Returns:
            AuditLog: Entrée d'audit créée
        """
        data_hash = None
        if data:
            data_str = json.dumps(data, sort_keys=True, default=str)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            result=result,
            data_hash=data_hash,
            timestamp=datetime.now(timezone.utc),
        )

        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)

        logger.info(
            "Action auditée",
            user_id=user_id,
            action=action,
            resource=resource,
            result=result,
        )

        return audit_log

    async def log_user_login(
        self,
        db: AsyncSession,
        user_id: str,
        ip_address: str = None,
        success: bool = True,
    ):
        """Enregistre une tentative de connexion.

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            ip_address: Adresse IP
            success: True si connexion réussie
        """
        await self.log_action(
            db=db,
            user_id=user_id,
            action="LOGIN",
            resource="auth",
            ip_address=ip_address,
            result="success" if success else "failure",
        )

    async def log_user_logout(
        self, db: AsyncSession, user_id: str, ip_address: str = None
    ):
        """Enregistre une déconnexion.

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            ip_address: Adresse IP
        """
        await self.log_action(
            db=db,
            user_id=user_id,
            action="LOGOUT",
            resource="auth",
            ip_address=ip_address,
        )

    async def log_payment(
        self,
        db: AsyncSession,
        user_id: str,
        payment_id: str,
        amount: int,
        action: str,
        ip_address: str = None,
    ):
        """Enregistre une action de paiement.

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            payment_id: ID du paiement
            amount: Montant
            action: Type d'action
            ip_address: Adresse IP
        """
        await self.log_action(
            db=db,
            user_id=user_id,
            action=action,
            resource=f"payments:{payment_id}",
            ip_address=ip_address,
            data={"amount": amount},
        )

    async def log_trip_action(
        self,
        db: AsyncSession,
        user_id: str,
        trip_id: str,
        action: str,
        ip_address: str = None,
    ):
        """Enregistre une action sur un trajet.

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            trip_id: ID du trajet
            action: Type d'action
            ip_address: Adresse IP
        """
        await self.log_action(
            db=db,
            user_id=user_id,
            action=action,
            resource=f"trips:{trip_id}",
            ip_address=ip_address,
        )

    async def log_admin_action(
        self,
        db: AsyncSession,
        admin_id: str,
        action: str,
        resource: str,
        target_id: str = None,
        ip_address: str = None,
        data: dict = None,
    ):
        """Enregistre une action d'administration.

        Args:
            db: Session de base de données
            admin_id: ID de l'administrateur
            action: Type d'action admin
            resource: Ressource touchée
            target_id: ID de la cible
            ip_address: Adresse IP
            data: Données additionnelles
        """
        await self.log_action(
            db=db,
            user_id=admin_id,
            action=f"ADMIN_{action}",
            resource=f"{resource}:{target_id}" if target_id else resource,
            ip_address=ip_address,
            data=data,
        )

    async def log_incident(
        self,
        db: AsyncSession,
        user_id: str,
        incident_id: str,
        incident_type: str,
        ip_address: str = None,
    ):
        """Enregistre la création d'un incident.

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            incident_id: ID de l'incident
            incident_type: Type d'incident
            ip_address: Adresse IP
        """
        await self.log_action(
            db=db,
            user_id=user_id,
            action="INCIDENT_CREATED",
            resource=f"incidents:{incident_id}",
            ip_address=ip_address,
            data={"type": incident_type},
        )

    async def log_camera_access(
        self, db: AsyncSession, admin_id: str, trip_id: str, ip_address: str = None
    ):
        """Enregistre l'accès à une vidéo de caméra.

        Args:
            db: Session de base de données
            admin_id: ID de l'administrateur
            trip_id: ID du trajet
            ip_address: Adresse IP
        """
        await self.log_action(
            db=db,
            user_id=admin_id,
            action="CAMERA_ACCESS",
            resource=f"recordings:{trip_id}",
            ip_address=ip_address,
            result="success",
        )

    async def get_user_logs(
        self, db: AsyncSession, user_id: str, limit: int = 50
    ) -> list:
        """Récupère les logs d'un utilisateur.

        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            limit: Nombre de résultats

        Returns:
            list: Liste des logs
        """
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )

        return result.scalars().all()


audit_service = AuditService()
