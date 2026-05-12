# ============================================================
# Service Transcription Vocale MobiTranz
# Fichier : backend/services/transcription_service.py
# Description : Transcription audio → texte avec SpeechRecognition
# ============================================================

import tempfile
import structlog
from typing import Optional
from pathlib import Path

logger = structlog.get_logger()


class TranscriptionService:
    """Service de transcription vocale MobiTranz.

    Utilise Google Speech Recognition (via SpeechRecognition)
    ou alternatively Vosk pour offline.
    """

    def __init__(self):
        self._sr_available = False
        self._vosk_available = False
        self._detect_engine()

    def _detect_engine(self):
        """Détecte le moteur de transcription disponible."""
        try:
            import speech_recognition

            self._recognizer = speech_recognition.Recognizer()
            self._sr_available = True
            logger.info("Moteur: Google Speech Recognition")
        except ImportError:
            logger.warning("SpeechRecognition non disponible")

        try:
            import vosk

            self._vosk_available = True
            logger.info("Moteur: Vosk offline disponible")
        except ImportError:
            logger.warning("Vosk non disponible")

    def transcribe(self, audio_data: bytes, language: str = "fr-FR") -> str:
        """Transcrit l'audio en texte.

        Args:
            audio_data: Données audio brutes (WAV 16kHz mono)
            language: Code langue (défaut: fr-FR)

        Returns:
            str: Texte transcrit
        """
        if self._sr_available:
            return self._transcribe_google(audio_data, language)
        elif self._vosk_available:
            return self._transcribe_vosk(audio_data, language)
        else:
            return self._transcribe_fallback(audio_data, language)

    def _transcribe_google(self, audio_data: bytes, language: str) -> str:
        """Transcrit via Google Speech API."""
        import speech_recognition

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            f.flush()
            audio_path = f.name

        try:
            with speech_recognition.AudioFile(audio_path) as source:
                audio = self._recognizer.record(source)

            text = self._recognizer.recognize_google(audio, language=language)
            logger.info("Transcription Google", text=text[:50])
            return text
        except speech_recognition.UnknownValueError:
            logger.warning("Google: parole non reconnue")
            return ""
        except speech_recognition.RequestError as e:
            logger.error("Google API error", error=str(e))
            return ""
        finally:
            Path(audio_path).unlink(missing_ok=True)

    def _transcribe_vosk(self, audio_data: bytes, language: str) -> str:
        """Transcrit via Vosk offline."""
        import json
        import wave
        import vosk

        model = vosk.Model("model-fr")
        recognizer = vosk.KaldiRecognizer(model, 16000)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            f.flush()
            audio_path = f.name

        try:
            wf = wave.open(audio_path, "rb")
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                recognizer.AcceptWaveform(data)
            result = json.loads(recognizer.FinalResult())
            text = result.get("text", "")
            logger.info("Transcription Vosk", text=text[:50])
            return text
        except Exception as e:
            logger.error("Vosk error", error=str(e))
            return ""
        finally:
            Path(audio_path).unlink(missing_ok=True)

    def _transcribe_fallback(self, audio_data: bytes, language: str) -> str:
        """Fallback: transcription vide avec log."""
        logger.warning(
            "Aucune engine de transcription disponible",
            language=language,
            audio_size=len(audio_data),
        )
        return ""


transcription_service = TranscriptionService()
