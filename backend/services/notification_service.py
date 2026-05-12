# ============================================================
# Service Notification Push MobiTranz
# Fichier : backend/services/notification_service.py
# Description : Firebase Cloud Messaging (FCM)
# ============================================================

from typing import Optional
import structlog

from backend.config import settings
from backend.tasks.notification_tasks import (
    send_push_notification_task,
    send_bulk_notification_task,
)

logger = structlog.get_logger()


class NotificationService:
    """Service de notifications push MobiTranz.

    Gère l'envoi de notifications via Firebase Cloud Messaging.
    Les appels FCM sont délégués à Celery pour un traitement asynchrone.
    """

    async def send_notification(
        self, token: str, title: str, body: str, data: Optional[dict] = None
    ) -> bool:
        """Envoie une notification push de manière asynchrone via Celery.

        Args:
            token: Jeton FCM de l'appareil
            title: Titre de la notification
            body: Corps de la notification
            data: Données supplémentaires

        Returns:
            bool: True si la tâche a été soumise
        """
        if not settings.firebase_credentials_path:
            logger.warning("FCM non configuré, notification ignorée")
            return False

        send_push_notification_task.delay(token, title, body, data)
        logger.info("Notification soumise à Celery", token=token[:20])
        return True

    async def send_proposal_notification(
        self, token: str, destination: str, amount: int
    ) -> bool:
        """Envoie une notification de proposition de trajet."""
        return await self.send_notification(
            token,
            "🚕 Nouvelle proposition",
            f"{destination} - {amount} XAF",
            {"type": "proposal", "destination": destination, "amount": str(amount)},
        )

    async def send_trip_started_notification(self, token: str) -> bool:
        """Envoie une notification de début de trajet."""
        return await self.send_notification(
            token,
            "🚕 Trajet commencé",
            "Votre conducteur est en route",
            {"type": "trip_started"},
        )

    async def send_payment_notification(
        self, token: str, amount: int, success: bool
    ) -> bool:
        """Envoie une notification de paiement."""
        if success:
            return await self.send_notification(
                token,
                "💳 Paiement confirmé",
                f"{amount} XAF versés avec succès",
                {"type": "payment_success", "amount": str(amount)},
            )
        else:
            return await self.send_notification(
                token,
                "❌ Paiement échoué",
                f"Échec du paiement de {amount} XAF",
                {"type": "payment_failed", "amount": str(amount)},
            )

    async def send_sos_notification(
        self, driver_tokens: list[str], location: str
    ) -> bool:
        """Envoie une notification SOS à tous les conducteurs via Celery."""
        send_bulk_notification_task.delay(
            driver_tokens,
            "🆘 URGENCE SOS",
            f"Accident signalé à {location}",
            {"type": "sos", "location": location, "priority": "high"},
        )
        logger.info("SOS notification soumise à Celery", count=len(driver_tokens), location=location)
        return True


notification_service = NotificationService()
