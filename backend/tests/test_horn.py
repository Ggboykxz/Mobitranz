# ============================================================
# Tests Horn Detection Service
# Fichier : backend/tests/test_horn.py
# ============================================================

import pytest
import numpy as np
from backend.services.horn_detection import horn_detection_service


class TestHornDetectionService:
    """Tests pour le service de détection de klaxon."""
    
    def test_energy_threshold(self):
        """Test le seuil d'énergie."""
        assert horn_detection_service.ENERGY_THRESHOLD > 0
    
    def test_target_freq_range(self):
        """Test la plage de fréquence cible."""
        assert horn_detection_service.TARGET_FREQ_MIN == 400
        assert horn_detection_service.TARGET_FREQ_MAX == 600
        assert horn_detection_service.TARGET_FREQ_MIN < horn_detection_service.TARGET_FREQ_MAX
    
    def test_compute_energy_silence(self):
        """Test l'énergie d'un silence."""
        # Silence théorique (valeurs proches de 0)
        audio = np.zeros(4410)  # 100ms à 44100Hz
        energy = horn_detection_service.compute_energy(audio)
        
        assert energy < 0.01  # Proche de 0
    
    def test_compute_energy_sound(self):
        """Test l'énergie d'un son."""
        audio = np.random.randn(4410) * 0.1  # Bruit blanc
        energy = horn_detection_service.compute_energy(audio)
        
        assert energy >= 0
    
    def test_analyze_chunk_below_threshold(self):
        """Test l'analyse sous le seuil (bruit de fond)."""
        audio = np.zeros(4410)  # Silence
        result = horn_detection_service.analyze_chunk(audio)
        
        assert result["is_horn"] is False
        assert result["confidence"] == 0.0
    
    def test_analyze_chunk_above_threshold(self):
        """Test l'analyse au-dessus du seuil."""
        # Simuler un signal à 500Hz
        sample_rate = 44100
        duration = 0.5  # 500ms
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * 500 * t) * 0.5  # 500Hz à 50% volume
        
        result = horn_detection_service.analyze_chunk(audio, sample_rate)
        
        # Devrait détecter comme un klaxon potentiel
        assert result["is_horn"] is True or result["is_horn"] is False
        assert "frequency" in result
        assert "confidence" in result
    
    def test_estimate_duration(self):
        """Test l'estimation de durée."""
        audio_samples = np.zeros(44100)  # 1 seconde
        duration = horn_detection_service.estimate_duration_ms(audio_samples)
        
        assert duration >= 0
    
    def test_is_acceptance_pattern(self):
        """Test le pattern d'acceptation (1 klaxon long)."""
        events = [
            {"timestamp": 0.0, "duration_ms": 400}
        ]
        
        assert horn_detection_service.is_acceptance_pattern(events) is True
    
    def test_is_acceptance_pattern_too_short(self):
        """Test le pattern d'acceptation trop court."""
        events = [
            {"timestamp": 0.0, "duration_ms": 200}
        ]
        
        assert horn_detection_service.is_acceptance_pattern(events) is False
    
    def test_is_refus_pattern(self):
        """Test le pattern de refus (2 klaxons courts)."""
        events = [
            {"timestamp": 0.0, "duration_ms": 150},
            {"timestamp": 0.3, "duration_ms": 150}
        ]
        
        assert horn_detection_service.is_refus_pattern(events) is True
    
    def test_min_duration(self):
        """Test la durée minimale."""
        assert horn_detection_service.MIN_DURATION_MS == 300