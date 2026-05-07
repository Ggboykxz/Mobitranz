# ============================================================
# Module GPS MobiTranz
# Fichier : vehicle_device/hardware/gps.py
# Description : Gestion GPS pour le Raspberry Pi via gpsd
# ============================================================

import time
import threading
import structlog
from typing import Optional, Callable, Tuple


logger = structlog.get_logger()


class GPSService:
    """Service GPS pour MobiTranz Raspberry Pi.
    
    Gère la localisation en temps réel du véhicule.
    """
    
    def __init__(self):
        """Initialise le service GPS."""
        self.gpsd_session = None
        self.current_lat = None
        self.current_lon = None
        self.current_speed = None
        self.current_heading = None
        self.last_update = None
        self.is_tracking = False
        self._location_callback = None
        self._initialize_gps()
    
    def _initialize_gps(self):
        """Initialise la connexion gpsd."""
        try:
            from gps import gps, WATCH_ENABLE
            
            self.gpsd_session = gps(host="localhost", port="2947")
            self.gpsd_session.stream(WATCH_ENABLE)
            
            logger.info("GPS initialisé")
            
        except ImportError:
            logger.warning("Module gps non disponible - mode simulation")
            self.gpsd_session = None
        except Exception as e:
            logger.error("Erreur initialisation GPS", error=str(e))
            self.gpsd_session = None
    
    def start_tracking(self, callback: Callable[[float, float, float], None] = None):
        """Démarre le suivi GPS.
        
        Args:
            callback: Fonction appelée à chaque mise à jour (lat, lon, speed)
        """
        if self.is_tracking:
            return
        
        self.is_tracking = True
        self._location_callback = callback
        
        if self.gpsd_session:
            self._start_gps_tracking()
        else:
            self._simulate_tracking()
    
    def _start_gps_tracking(self):
        """Démarre le suivi GPS réel via gpsd."""
        def gps_thread():
            try:
                while self.is_tracking:
                    report = self.gpsd_session.next()
                    
                    if report["class"] == "TPV":
                        if hasattr(report, "lat") and hasattr(report, "lon"):
                            self.current_lat = report.lat
                            self.current_lon = report.lon
                            self.current_speed = getattr(report, "speed", 0) * 1.852
                            self.current_heading = getattr(report, "track", 0)
                            self.last_update = time.time()
                            
                            if self._location_callback:
                                self._location_callback(
                                    self.current_lat,
                                    self.current_lon,
                                    self.current_speed or 0
                                )
                    
                    time.sleep(1)
                    
            except Exception as e:
                logger.error("Erreur GPS", error=str(e))
        
        thread = threading.Thread(target=gps_thread, daemon=True)
        thread.start()
    
    def _simulate_tracking(self):
        """Mode simulation pour les tests."""
        import random
        
        base_lat = 0.4163
        base_lon = 9.4673
        
        def simulate():
            while self.is_tracking:
                self.current_lat = base_lat + random.uniform(-0.01, 0.01)
                self.current_lon = base_lon + random.uniform(-0.01, 0.01)
                self.current_speed = random.uniform(20, 60)
                self.current_heading = random.uniform(0, 360)
                self.last_update = time.time()
                
                if self._location_callback:
                    self._location_callback(
                        self.current_lat,
                        self.current_lon,
                        self.current_speed
                    )
                
                time.sleep(2)
        
        thread = threading.Thread(target=simulate, daemon=True)
        thread.start()
    
    def stop_tracking(self):
        """Arrête le suivi GPS."""
        self.is_tracking = False
        logger.info("GPS tracking arrêté")
    
    def get_current_position(self) -> Optional[Tuple[float, float]]:
        """Retourne la position actuelle.
        
        Returns:
            tuple: (latitude, longitude) ou None
        """
        if self.current_lat and self.current_lon:
            return (self.current_lat, self.current_lon)
        return None
    
    def get_speed(self) -> Optional[float]:
        """Retourne la vitesse actuelle en km/h.
        
        Returns:
            float: Vitesse en km/h ou None
        """
        return self.current_speed
    
    def get_heading(self) -> Optional[float]:
        """Retourne la direction actuelle en degrés.
        
        Returns:
            float: Direction en degrés (0-360) ou None
        """
        return self.current_heading
    
    def get_status(self) -> dict:
        """Retourne le statut GPS.
        
        Returns:
            dict: Statut du service GPS
        """
        return {
            "tracking": self.is_tracking,
            "latitude": self.current_lat,
            "longitude": self.current_lon,
            "speed_kmh": self.current_speed,
            "heading": self.current_heading,
            "last_update": self.last_update,
            "gps_available": self.gpsd_session is not None
        }


gps_service = GPSService()