# ============================================================
# Service QR Code MobiTranz
# Fichier : backend/services/qr_service.py
# Description : Génération QR dynamique signé (expirant 5 min)
# ============================================================

import qrcode
import hmac
import hashlib
import base64
import io
from datetime import datetime, timezone, timedelta
from typing import Optional
import structlog

from backend.config import settings
from backend.redis_client import redis_client

logger = structlog.get_logger()


class QRService:
    """Service QR Code MobiTranz.

    Génère des QR Codes dynamiques avec signature HMAC
    et expiration de 5 minutes.
    """

    # Durée d'expiration du QR Code en secondes
    QR_EXPIRY_SECONDS = 300  # 5 minutes

    def generate_qr_signature(
        self, vehicle_id: str, trip_id: str, timestamp: int
    ) -> str:
        """Génère une signature HMAC pour le QR Code.

        Args:
            vehicle_id: ID du véhicule
            trip_id: ID du trajet
            timestamp: Timestamp Unix

        Returns:
            str: Signature HMAC-SHA256 encodée en base64
        """
        message = f"{vehicle_id}:{trip_id}:{timestamp}"
        signature = hmac.new(
            settings.secret_key.encode(), message.encode(), hashlib.sha256
        ).digest()

        return base64.b64encode(signature).decode()

    def verify_qr_signature(
        self, vehicle_id: str, trip_id: str, timestamp: int, signature: str
    ) -> bool:
        """Vérifie la signature d'un QR Code.

        Args:
            vehicle_id: ID du véhicule
            trip_id: ID du trajet
            timestamp: Timestamp Unix
            signature: Signature à vérifier

        Returns:
            bool: True si signature valide
        """
        expected = self.generate_qr_signature(vehicle_id, trip_id, timestamp)
        return hmac.compare_digest(expected, signature)

    async def generate_qr_code(self, vehicle_id: str, trip_id: str) -> str:
        """Génère un QR Code dynamique pour un trajet.

        Args:
            vehicle_id: ID du véhicule
            trip_id: ID du trajet

        Returns:
            str: QR Code encodé en base64 (image PNG)
        """
        timestamp = int(datetime.now(timezone.utc).timestamp())
        signature = self.generate_qr_signature(vehicle_id, trip_id, timestamp)

        # Données encodées dans le QR Code
        qr_data = f"MT:{vehicle_id}:{trip_id}:{timestamp}:{signature}"

        # Génération de l'image QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#1A3A6C", back_color="white")

        # Conversion en base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        logger.info(
            "QR Code généré",
            vehicle_id=vehicle_id,
            trip_id=trip_id,
            expires_in=self.QR_EXPIRY_SECONDS,
        )

        return f"data:image/png;base64,{qr_base64}"

    async def verify_and_use_qr(
        self, vehicle_id: str, trip_id: str, timestamp: int, signature: str
    ) -> bool:
        """Vérifie et utilise un QR Code (usage unique).

        Args:
            vehicle_id: ID du véhicule
            trip_id: ID du trajet
            timestamp: Timestamp Unix
            signature: Signature HMAC

        Returns:
            bool: True si QR Code valide et first usage
        """
        # Vérification de l'expiration
        current_time = int(datetime.now(timezone.utc).timestamp())
        if current_time - timestamp > self.QR_EXPIRY_SECONDS:
            logger.warning("QR Code expiré", trip_id=trip_id)
            return False

        # Vérification de la signature
        if not self.verify_qr_signature(vehicle_id, trip_id, timestamp, signature):
            logger.warning("Signature QR invalide", trip_id=trip_id)
            return False

        # Vérification usage unique via Redis
        qr_id = f"{vehicle_id}:{trip_id}:{timestamp}"
        used = await redis_client.use_qr_code(qr_id)

        if not used:
            logger.warning("QR Code déjà utilisé", trip_id=trip_id)
            return False

        logger.info("QR Code validé", trip_id=trip_id)
        return True

    def parse_qr_data(self, qr_data: str) -> Optional[dict]:
        """Parse les données d'un QR Code.

        Args:
            qr_data: Données brutes du QR Code

        Returns:
            dict: Données parsées ou None si invalide
        """
        try:
            # Format: MT:vehicle_id:trip_id:timestamp:signature
            parts = qr_data.split(":")
            if len(parts) != 5 or parts[0] != "MT":
                return None

            return {
                "vehicle_id": parts[1],
                "trip_id": parts[2],
                "timestamp": int(parts[3]),
                "signature": parts[4],
            }
        except Exception as e:
            logger.error("Erreur parsing QR", error=str(e))
            return None


qr_service = QRService()
