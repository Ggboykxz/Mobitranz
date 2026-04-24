# ============================================================
# Service Notification Push MobiTranz
# Fichier : backend/services/notification_service.py
# Description : Firebase Cloud Messaging (FCM)
# ============================================================

import structlog
from typing import Optional
import httpx


logger = structlog.get_logger()


class NotificationService:
    """Service de notifications push MobiTranz.
    
    Gère l'envoi de notifications via Firebase Cloud Messaging.
    """
    
    async def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> bool:
        """Envoie une notification push.
        
        Args:
            token: Jeton FCM de l'appareil
            title: Titre de la notification
            body: Corps de la notification
            data: Données supplémentaires
            
        Returns:
            bool: True si envoyée avec succès
        """
        if not hasattr(self, '_fcm_initialized'):
            logger.warning("FCM non initialisé")
            return False
        
        message = {
            "to": token,
            "notification": {
                "title": title,
                "body": body,
            },
            "data": data or {},
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://fcm.googleapis.com/fcm/send",
                    json=message,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"key={self.server_key}"
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    logger.info("Notification envoyée", token=token[:20])
                    return True
                else:
                    logger.error("Erreur FCM", status=response.status_code)
                    return False
                    
        except Exception as e:
            logger.error("Erreur notification", error=str(e))
            return False
    
    async def send_proposal_notification(
        self,
        token: str,
        destination: str,
        amount: int
    ):
        """Envoie une notification de proposition de trajet.
        
        Args:
            token: Jeton FCM
            destination: Destination
            amount: Montant
        """
        return await self.send_notification(
            token,
            "Nouvelle proposition de trajet",
            f"Destination: {destination}, Montant: {amount} XAF",
            {"type": "proposal", "destination": destination}
        )
    
    async def send_trip_started_notification(
        self,
        token: str
    ):
        """Envoie une notification de début de trajet."""
        return await self.send_notification(
            token,
            "Trajet commencé",
            "Votre trajet est en cours",
            {"type": "trip_started"}
        )


notification_service = NotificationService()