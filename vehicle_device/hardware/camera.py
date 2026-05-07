# ============================================================
# Caméra Embarquée MobiTranz
# Fichier : vehicle_device/hardware/camera.py
# Description : Gestion caméra Raspberry Pi avec OpenCV et picamera2
# ============================================================

import os
import time
import threading
import structlog
from typing import Optional, Callable
from datetime import datetime
import numpy as np


logger = structlog.get_logger()


class CameraService:
    """Service de caméra embarquée pour MobiTranz.
    
    Gère l'enregistrement vidéo de l'intérieur du véhicule
    pendant les trajets pour la sécurité.
    """
    
    def __init__(self, encryption_key: bytes = None):
        """Initialise le service caméra.
        
        Args:
            encryption_key: Clé AES pour chiffrement des vidéos
        """
        self.camera = None
        self.is_recording = False
        self.current_trip_id = None
        self.output_dir = "/var/mobitranz/recordings"
        self.encryption_key = encryption_key
        self._frame_callback = None
        self._initialize_camera()
    
    def _initialize_camera(self):
        """Initialise la caméra Raspberry Pi."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            
            from picamera2 import Picamera2
            self.camera = Picamera2()
            
            config = self.camera.create_video_configuration(
                main={"size": (1920, 1080), "format": "XBGR8888"},
                lores={"size": (640, 480), "format": "YUV420"}
            )
            self.camera.configure(config)
            
            logger.info("Caméra initialisée", resolution="1080p")
            
        except ImportError:
            logger.warning("picamera2 non disponible - mode simulation")
            self.camera = None
        except Exception as e:
            logger.error("Erreur initialisation caméra", error=str(e))
            self.camera = None
    
    def start_recording(self, trip_id: str) -> bool:
        """Démarre l'enregistrement vidéo pour un trajet.
        
        Args:
            trip_id: ID du trajet en cours
            
        Returns:
            bool: True si l'enregistrement a démarré
        """
        if self.is_recording:
            logger.warning("Enregistrement déjà en cours")
            return False
        
        self.current_trip_id = trip_id
        self.is_recording = True
        
        if self.camera:
            self._start_camera_recording()
        else:
            self._simulate_recording()
        
        logger.info("Enregistrement démarré", trip_id=trip_id)
        
        return True
    
    def _start_camera_recording(self):
        """Démarre l'enregistrement réel avec la caméra."""
        def recording_loop():
            try:
                self.camera.start()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.output_dir}/{self.current_trip_id}_{timestamp}.mp4"
                
                while self.is_recording:
                    frame = self.camera.capture_array()
                    
                    if self._frame_callback:
                        self._frame_callback(frame)
                    
                    time.sleep(0.033)
                    
            except Exception as e:
                logger.error("Erreur enregistrement", error=str(e))
            finally:
                self.camera.stop()
        
        thread = threading.Thread(target=recording_loop, daemon=True)
        thread.start()
    
    def _simulate_recording(self):
        """Mode simulation pour les tests."""
        logger.info("Mode simulation enregistrement", trip_id=self.current_trip_id)
    
    def stop_recording(self) -> Optional[str]:
        """Arrête l'enregistrement vidéo.
        
        Returns:
            str: Chemin du fichier enregistré ou None
        """
        if not self.is_recording:
            return None
        
        self.is_recording = False
        
        if self.current_trip_id:
            filename = f"{self.output_dir}/{self.current_trip_id}_recording"
            logger.info("Enregistrement arrêté", trip_id=self.current_trip_id, file=filename)
            return filename
        
        return None
    
    def set_frame_callback(self, callback: Callable):
        """Définit un callback pour traiter chaque frame.
        
        Args:
            callback: Fonction appelée pour chaque frame
        """
        self._frame_callback = callback
    
    def capture_photo(self) -> Optional[np.ndarray]:
        """Capture une photo unique.
        
        Returns:
            np.ndarray: Image capturée ou None
        """
        if not self.camera:
            return None
        
        try:
            self.camera.start()
            time.sleep(0.5)
            frame = self.camera.capture_array()
            self.camera.stop()
            
            return frame
            
        except Exception as e:
            logger.error("Erreur capture photo", error=str(e))
            return None
    
    def is_active(self) -> bool:
        """Vérifie si la caméra est active.
        
        Returns:
            bool: True si la caméra est en cours d'enregistrement
        """
        return self.is_recording
    
    def get_status(self) -> dict:
        """Retourne le statut actuel de la caméra.
        
        Returns:
            dict: Statut de la caméra
        """
        return {
            "recording": self.is_recording,
            "trip_id": self.current_trip_id,
            "camera_available": self.camera is not None,
            "output_dir": self.output_dir
        }
    
    def delete_old_recordings(self, days: int = 7):
        """Supprime les enregistrements plus anciens que N jours.
        
        Args:
            days: Nombre de jours de rétention
        """
        if not os.path.exists(self.output_dir):
            return
        
        cutoff_time = time.time() - (days * 86400)
        
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            
            if os.path.isfile(filepath):
                if os.path.getmtime(filepath) < cutoff_time:
                    try:
                        os.remove(filepath)
                        logger.info("Ancien enregistrement supprimé", file=filename)
                    except Exception as e:
                        logger.error("Erreur suppression", file=filename, error=str(e))


import os

camera_service = CameraService()