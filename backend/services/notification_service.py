# ============================================================
# Service Notification Push MobiTranz
# Fichier : backend/services/notification_service.py
# Description : Firebase Cloud Messaging (FCM)
# ============================================================

from typing import Optional
import structlog
import httpx

from backend.config import settings

logger = structlog.get_logger()


class NotificationService:
    """Service de notifications push MobiTranz.

    Gère l'envoi de notifications via Firebase Cloud Messaging.
    """

    def __init__(self):
        self._initialized = False
        self._fcm_api_key: str | None = None
        self._project_id: str | None = None
        self._initialize()

    def _initialize(self):
        """Initialise FCM avec les credentials."""
        if settings.firebase_credentials_path:
            try:
                import json

                with open(settings.firebase_credentials_path, "r") as f:
                    creds = json.load(f)
                    self._project_id = creds.get("project_id")
                    self._fcm_api_key = creds.get("api_key")
                    self._initialized = True
                    logger.info("FCM initialisé", project=self._project_id)
            except FileNotFoundError:
                logger.warning("FCM credentials non trouvés, notifications désactivées")
            except Exception as e:
                logger.error("Erreur init FCM", error=str(e))
        else:
            logger.warning("FCM désactivé (pas de credentials_path)")

    async def send_notification(
        self, token: str, title: str, body: str, data: Optional[dict] = None
    ) -> bool:
        """Envoie une notification push via FCM HTTP v1 API.

        Args:
            token: Jeton FCM de l'appareil
            title: Titre de la notification
            body: Corps de la notification
            data: Données supplémentaires

        Returns:
            bool: True si envoyée avec succès
        """
        if not self._initialized or not self._project_id:
            logger.warning("FCM non configuré, notification ignorée")
            return False

        message = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body,
                },
                "data": data or {},
                "android": {
                    "priority": "high",
                    "notification": {
                        "channel_id": "mobitranz_default",
                    },
                },
                "apns": {
                    "payload": {
                        "aps": {
                            "sound": "default",
                        }
                    }
                },
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://fcm.googleapis.com/v1/projects/{self._project_id}/messages:send",
                    json=message,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self._fcm_api_key}",
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        "Notification envoyée",
                        message_id=result.get("name", "").split("/")[-1],
                        token=token[:20] + "...",
                    )
                    return True
                else:
                    logger.error(
                        "Erreur FCM",
                        status=response.status_code,
                        body=response.text[:200],
                    )
                    return False

        except httpx.TimeoutException:
            logger.error("FCM timeout")
            return False
        except Exception as e:
            logger.error("Erreur notification", error=str(e))
            return False

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
        """Envoie une notification SOS à tous les conducteurs."""
        results = []
        for token in driver_tokens:
            result = await self.send_notification(
                token,
                "🆘 URGENCE SOS",
                f"Accident signalé à {location}",
                {"type": "sos", "location": location, "priority": "high"},
            )
            results.append(result)
        return any(results)


notification_service = NotificationService()
