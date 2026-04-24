# ============================================================
# Service Détection Klaxon MobiTranz
# Fichier : backend/services/horn_detection.py
# Description : Détection acoustique klaxon (librosa + PyAudio)
# ============================================================

import numpy as np
import structlog
from scipy import signal


logger = structlog.get_logger()


class HornDetectionService:
    """Service de détection acoustique du klaxon de validation.
    
    Analyse le flux audio en temps réel pour détecter le pattern sonore
    d'un klaxon de véhicule (400-600 Hz, durée > 300ms).
    
    Patterns reconnus :
    - 1 klaxon long (>300ms) = ACCEPTATION
    - 2 klaxons courts (<200ms, intervalle <500ms) = REFUS
    """
    
    TARGET_FREQ_MIN = 400  # Hz
    TARGET_FREQ_MAX = 600  # Hz
    MIN_DURATION_MS = 300  # ms
    ENERGY_THRESHOLD = 0.02
    SAMPLE_RATE = 44100  # Hz
    
    def compute_energy(self, audio_chunk: np.ndarray) -> float:
        """Calcule l'énergie RMS d'un chunk audio.
        
        Args:
            audio_chunk: Samples audio
            
        Returns:
            float: Énergie RMS normalisée
        """
        return np.sqrt(np.mean(audio_chunk ** 2))
    
    def detect_frequency(
        self,
        audio_chunk: np.ndarray,
        sample_rate: int = None
    ) -> float:
        """Détecte la fréquence dominante via FFT.
        
        Args:
            audio_chunk: Samples audio
            sample_rate: Taux d'échantillonnage
            
        Returns:
            float: Fréquence dominante en Hz
        """
        if sample_rate is None:
            sample_rate = self.SAMPLE_RATE
        
        # Application d'une fenêtre Hann
        windowed = audio_chunk * signal.windows.hann(len(audio_chunk))
        
        # FFT
        spec = np.fft.rfft(windowed)
        freqs = np.fft.rfftfreq(len(audio_chunk), 1 / sample_rate)
        
        # Trouver le pic spectral
        peaks, _ = signal.find_peaks(
            np.abs(spec),
            height=np.max(np.abs(spec)) * 0.1
        )
        
        if len(peaks) > 0:
            idx = peaks[np.argmax(np.abs(spec)[peaks])]
            return freqs[idx]
        
        return 0.0
    
    def analyze_chunk(
        self,
        audio_chunk: np.ndarray,
        sample_rate: int = None
    ) -> dict:
        """Analyse un chunk audio pour détecter la présence d'un klaxon.
        
        Args:
            audio_chunk: Samples audio (float32, normalisé)
            sample_rate: Taux d'échantillonnage
            
        Returns:
            dict: {"is_horn": bool, "frequency": float, "confidence": float}
        """
        if sample_rate is None:
            sample_rate = self.SAMPLE_RATE
        
        energy = self.compute_energy(audio_chunk)
        
        if energy < self.ENERGY_THRESHOLD:
            return {
                "is_horn": False,
                "frequency": 0.0,
                "confidence": 0.0
            }
        
        frequency = self.detect_frequency(audio_chunk, sample_rate)
        
        if self.TARGET_FREQ_MIN <= frequency <= self.TARGET_FREQ_MAX:
            # Calcul du score de confiance
            center = (self.TARGET_FREQ_MIN + self.TARGET_FREQ_MAX) / 2
            bandwidth = (self.TARGET_FREQ_MAX - self.TARGET_FREQ_MIN) / 2
            confidence = 1.0 - abs(frequency - center) / bandwidth
            
            return {
                "is_horn": True,
                "frequency": frequency,
                "confidence": max(0, min(1, confidence)),
                "energy": energy
            }
        
        return {
            "is_horn": False,
            "frequency": frequency,
            "confidence": 0.0
        }
    
    def estimate_duration_ms(
        self,
        audio_samples: np.ndarray,
        sample_rate: int = None
    ) -> float:
        """Estime la durée d'un signal audio en millisecondes.
        
        Args:
            audio_samples: Samples audio
            sample_rate: Taux d'échantillonnage
            
        Returns:
            float: Durée en ms
        """
        if sample_rate is None:
            sample_rate = self.SAMPLE_RATE
        
        return (len(audio_samples) / sample_rate) * 1000
    
    def is_acceptance_pattern(
        self,
        detected_events: list
    ) -> bool:
        """Détecte un pattern d'acceptation (1 klaxon long).
        
        Args:
            detected_events: Liste des événements détectés
            
        Returns:
            bool: True si pattern d'acceptation
        """
        if not detected_events:
            return False
        
        last_event = detected_events[-1]
        if last_event.get("duration_ms", 0) >= self.MIN_DURATION_MS:
            logger.info("Pattern ACCEPTATION détecté")
            return True
        
        return False
    
    def is_refus_pattern(
        self,
        detected_events: list
    ) -> bool:
        """Détecte un pattern de refus (2 klaxons courts).
        
        Args:
            detected_events: Liste des événements détectés
            
        Returns:
            bool: True si pattern de refus
        """
        if len(detected_events) < 2:
            return False
        
        last_two = detected_events[-2:]
        
        first_duration = last_two[0].get("duration_ms", 0)
        second_duration = last_two[1].get("duration_ms", 0)
        
        if first_duration > 200 or second_duration > 200:
            return False
        
        interval_ms = (last_two[1]["timestamp"] - last_two[0]["timestamp"]) * 1000
        
        if interval_ms < 500:
            logger.info("Pattern REFUS détecté")
            return True
        
        return False


horn_detection_service = HornDetectionService()