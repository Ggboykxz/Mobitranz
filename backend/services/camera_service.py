# ============================================================
# Service Caméra MobiTranz
# Fichier : backend/services/camera_service.py
# Description : Contrôle caméra, déclenchement, chiffrement vidéo
# ============================================================

import cv2
import structlog
import numpy as np
from typing import Optional
from datetime import datetime

from backend.services.encryption_service import encryption_service

logger = structlog.get_logger()


class CameraService:
    """Service de caméra embarquée MobiTranz.

    Gère le contrôle de la caméra USB, le déclenchement
    et le chiffrement des vidéos en temps réel.
    """

    def __init__(self):
        """Initialise le service caméra."""
        self._capture = None
        self._current_key = None

    def open_camera(self, device_id: int = 0) -> bool:
        """Ouvre la caméra.

        Args:
            device_id: ID du périphérique vidéo

        Returns:
            bool: True si succès
        """
        try:
            if self._capture is not None:
                self._capture.release()

            self._capture = cv2.VideoCapture(device_id)

            if not self._capture.isOpened():
                logger.error("Caméra non trouvée", device_id=device_id)
                return False

            logger.info("Caméra ouverte", device_id=device_id)
            return True

        except Exception as e:
            logger.error("Erreur ouverture caméra", error=str(e))
            return False

    def close_camera(self):
        """Ferme la caméra."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
            logger.info("Caméra fermée")

    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture une frame vidéo.

        Returns:
            np.ndarray: Image capturée ou None
        """
        if self._capture is None:
            return None

        ret, frame = self._capture.read()
        if ret:
            return frame
        return None

    def start_recording(self, trip_id: str) -> str:
        """Démarre l'enregistrement pour un trajet.

        Args:
            trip_id: ID du trajet

        Returns:
            str: Clé de chiffrement pour le trajet
        """
        self._current_key = encryption_service.generate_aes_key()

        logger.info(
            "Enregistrement démarré",
            trip_id=trip_id,
            key=encryption_service.encode_key_base64(self._current_key)[:20],
        )

        return encryption_service.encode_key_base64(self._current_key)

    def encrypt_frame(self, frame: np.ndarray) -> tuple:
        """Chiffre une frame vidéo.

        Args:
            frame: Image à chiffrer

        Returns:
            tuple: (données chiffrées, nonce)
        """
        if self._current_key is None:
            raise ValueError("Pas de clé de chiffrement active")

        key = encryption_service.decode_key_base64(self._current_key)
        frame_bytes = cv2.imencode(".jpg", frame)[1].tobytes()

        return encryption_service.encrypt_video_chunk(frame_bytes, key)

    def stop_recording(self) -> None:
        """Arrête l'enregistrement et sécurise la clé."""
        key = self._current_key
        self._current_key = None

        logger.info("Enregistrement arrêté", key_stored=str(key)[:20] if key else None)

    def is_recording(self) -> bool:
        """Vérifie si l'enregistrement est en cours."""
        return self._current_key is not None

    def set_quality(self, width: int = 1280, height: int = 720):
        """Configure la résolution vidéo.

        Args:
            width: Largeur
            height: Hauteur
        """
        if self._capture is not None:
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


camera_service = CameraService()
