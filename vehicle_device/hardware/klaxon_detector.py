# ============================================================
# Détecteur de Klaxon MobiTranz
# Fichier : vehicle_device/hardware/klaxon_detector.py
# Description : Détection et analyse du klaxon véhicule via PyAudio et librosa
# ============================================================

import numpy as np
import time
import structlog
from typing import Optional, List, Callable


logger = structlog.get_logger()


KLAXON_MIN_DB = 85
KLAXON_FREQ_MIN = 400
KLAXON_FREQ_MAX = 800
KLAXON_BEEP_MIN_MS = 200
KLAXON_BEEP_MAX_MS = 600
KLAXON_INTERVAL_MAX_MS = 2000
KLAXON_ACCEPT = 1
KLAXON_REFUSE = 2
KLAXON_TIMEOUT_SEC = 10


class KlaxonDetector:
    """Détecteur de klaxon pour validation de trajet.
    
    Analyse le signal audio pour détecter les patterns de klaxon :
    - 1 bip court = ACCEPTÉ
    - 2 bips courts = REFUSÉ
    """
    
    def __init__(self):
        """Initialise le détecteur de klaxon."""
        self.audio = None
        self.sample_rate = 44100
        self.is_listening = False
        self.beeps_detected = []
        self.callback = None
        self._initialize_audio()
    
    def _initialize_audio(self):
        """Initialise le microphone pour l'écoute."""
        try:
            import pyaudio
            self.audio = pyaudio.PyAudio()
            logger.info("KlaxonDetector initialisé")
        except ImportError:
            logger.warning("PyAudio non disponible - mode simulation")
            self.audio = None
    
    def start_listening(self, callback: Callable[[int], None]):
        """Démarre l'écoute du microphone pour détecter les klaxons.
        
        Args:
            callback: Fonction appelée avec le résultat (1=accept, 2=refuse)
        """
        if self.is_listening:
            return
        
        self.callback = callback
        self.beeps_detected = []
        self.is_listening = True
        
        if self.audio:
            self._start_audio_stream()
        else:
            self._simulate_listening()
    
    def _start_audio_stream(self):
        """Démarre le flux audio pour l'analyse en temps réel."""
        import threading
        
        def audio_thread():
            try:
                stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=4096
                )
                
                while self.is_listening:
                    data = stream.read(4096, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    result = self._analyze_chunk(audio_data)
                    
                    if result["is_horn"]:
                        self.beeps_detected.append({
                            "timestamp": time.time(),
                            "duration_ms": result.get("duration_ms", 0)
                        })
                        
                        self._check_pattern()
                        
            except Exception as e:
                logger.error("Erreur flux audio", error=str(e))
            finally:
                if stream:
                    stream.stop_stream()
                    stream.close()
        
        thread = threading.Thread(target=audio_thread, daemon=True)
        thread.start()
    
    def _analyze_chunk(self, audio_data: np.ndarray) -> dict:
        """Analyse un chunk de données audio pour détecter un klaxon.
        
        Args:
            audio_data: Données audio brutes
            
        Returns:
            dict: Résultat de l'analyse (is_horn, confidence, etc.)
        """
        energy = self._compute_energy(audio_data)
        
        if energy < KLAXON_MIN_DB:
            return {"is_horn": False, "confidence": 0.0, "energy": energy}
        
        fft = np.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(len(audio_data), 1.0 / self.sample_rate)
        
        magnitude = np.abs(fft)
        
        dominant_freq_idx = np.argmax(magnitude)
        dominant_freq = freqs[dominant_freq_idx]
        
        if KLAXON_FREQ_MIN <= dominant_freq <= KLAXON_FREQ_MAX:
            confidence = min(energy / 120.0, 1.0)
            
            duration_ms = len(audio_data) * 1000 / self.sample_rate
            
            return {
                "is_horn": True,
                "confidence": confidence,
                "frequency": dominant_freq,
                "energy": energy,
                "duration_ms": duration_ms
            }
        
        return {"is_horn": False, "confidence": 0.0, "energy": energy}
    
    def _compute_energy(self, audio_data: np.ndarray) -> float:
        """Calcule l'énergie RMS du signal audio en dB.
        
        Args:
            audio_data: Données audio brutes
            
        Returns:
            float: Énergie en dB
        """
        if len(audio_data) == 0:
            return 0.0
        
        rms = np.sqrt(np.mean(audio_data.astype(float) ** 2))
        
        if rms > 0:
            db = 20 * np.log10(rms / 32768.0)
            return max(db, 0.0)
        
        return 0.0
    
    def _check_pattern(self):
        """Vérifie si le pattern de klaxons correspond à accept ou refuse."""
        if not self.beeps_detected:
            return
        
        if len(self.beeps_detected) == 1:
            beep = self.beeps_detected[-1]
            if KLAXON_BEEP_MIN_MS <= beep["duration_ms"] <= KLAXON_BEEP_MAX_MS:
                self._send_result(KLAXON_ACCEPT)
                self.stop_listening()
                
        elif len(self.beeps_detected) >= 2:
            last_two = self.beeps_detected[-2:]
            time_diff = (last_two[1]["timestamp"] - last_two[0]["timestamp"]) * 1000
            
            if time_diff <= KLAXON_INTERVAL_MAX_MS:
                self._send_result(KLAXON_REFUSE)
                self.stop_listening()
    
    def _send_result(self, result: int):
        """Envoie le résultat au callback.
        
        Args:
            result: 1=accept, 2=refuse
        """
        if self.callback:
            logger.info("Klaxon détecté", pattern=result)
            self.callback(result)
    
    def stop_listening(self):
        """Arrête l'écoute du microphone."""
        self.is_listening = False
        logger.info("KlaxonDetector arrêté")
    
    def _simulate_listening(self):
        """Mode simulation pour tests sans microphone."""
        import threading
        
        def simulate():
            time.sleep(KLAXON_TIMEOUT_SEC)
            if self.is_listening and not self.beeps_detected:
                logger.info("Timeout klaxon - refus automatique")
                self._send_result(KLAXON_REFUSE)
                self.stop_listening()
        
        thread = threading.Thread(target=simulate, daemon=True)
        thread.start()
    
    def process_audio_file(self, audio_file_path: str) -> Optional[int]:
        """Traite un fichier audio et retourne le pattern détecté.
        
        Args:
            audio_file_path: Chemin vers le fichier audio
            
        Returns:
            int: 1=accept, 2=refuse, ou None si aucun pattern
        """
        try:
            import librosa
            
            y, sr = librosa.load(audio_file_path, sr=self.sample_rate)
            
            energy_db = librosa.feature.rms(y=y)[0]
            times = librosa.times_like(energy_db, sr=sr)
            
            beeps = []
            
            for i, (t, e) in enumerate(zip(times, energy_db)):
                e_db = 20 * np.log10(e + 1e-10)
                
                if e_db > KLAXON_MIN_DB:
                    duration = 0
                    j = i
                    while j < len(energy_db) and 20 * np.log10(energy_db[j] + 1e-10) > KLAXON_MIN_DB:
                        duration += 1
                        j += 1
                    
                    duration_ms = duration * 1000 / sr
                    
                    if KLAXON_BEEP_MIN_MS <= duration_ms <= KLAXON_BEEP_MAX_MS:
                        beeps.append({"timestamp": t, "duration_ms": duration_ms})
            
            if len(beeps) == 1:
                return KLAXON_ACCEPT
            elif len(beeps) >= 2:
                if (beeps[1]["timestamp"] - beeps[0]["timestamp"]) * 1000 <= KLAXON_INTERVAL_MAX_MS:
                    return KLAXON_REFUSE
            
            return None
            
        except Exception as e:
            logger.error("Erreur traitement audio", error=str(e))
            return None
    
    def get_energy_threshold(self) -> float:
        """Retourne le seuil d'énergie en dB.
        
        Returns:
            float: Seuil d'énergie
        """
        return KLAXON_MIN_DB
    
    def get_frequency_range(self) -> tuple:
        """Retourne la plage de fréquence des klaxons.
        
        Returns:
            tuple: (fréquence_min, fréquence_max) en Hz
        """
        return (KLAXON_FREQ_MIN, KLAXON_FREQ_MAX)


klaxon_detector = KlaxonDetector()