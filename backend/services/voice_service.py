# ============================================================
# Service Proposition Vocale MobiTranz
# Fichier : backend/services/voice_service.py
# Description : NLP extraction destination + montant + places
# ============================================================

import re
import unicoded
from typing import Optional, Dict
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.voice_proposal import VoiceProposal


logger = structlog.get_logger()


class VoiceProposalService:
    """Service de reconnaissance vocale pour les propositions de trajet.
    
    Utilise SpeechRecognition ou Vosk pour la transcription.
    Extrait destination, montant et nombre de places.
    """
    
    KNOWN_ZONES = {
        "centre-ville": ["centre", "plateau", "haut de gue-gue", "lgbt"],
        "owendo": ["owendo", "ouen"],
        "akanda": ["akanda", "mondah"],
        "libreville": ["libreville", "lbv"],
        "port-gentil": ["port", "gentil", "pg"],
        "ntoum": ["ntoum"],
        "angondje": ["angondje", "angondjé"],
        "lalala": ["lalala"],
        "pk5": ["pk5", "p-k-5"],
        "pk8": ["pk8", "p-k-8"],
        "pk12": ["pk12", "p-k-12"],
        "nombakele": ["nombakélé", "nombakele"],
    }
    
    NUMBER_WORDS = {
        "zéro": 0, "un": 1, "une": 1, "deux": 2, "trois": 3,
        "quatre": 4, "cinq": 5, "six": 6, "sept": 7,
        "huit": 8, "neuf": 9, "dix": 10, "onze": 11,
        "douze": 12, "treize": 13, "quatorze": 14, "quinze": 15,
    }
    
    def normalize_text(self, text: str) -> str:
        """Normalise le texte pour l'analyse.
        
        Args:
            text: Texte brut
            
        Returns:
            str: Texte normalisé
        """
        text = text.lower()
        text = unicoded.normalize("NFD", text)
        text = "".join(
            c for c in text if unicoded.category(c) != "Mn"
        )
        return text
    
    def extract_destination(self, text: str) -> Optional[str]:
        """Extrait la destination du texte.
        
        Args:
            text: Texte normalisé
            
        Returns:
            str: Nom de la destination ou None
        """
        text = self.normalize_text(text)
        
        for zone, keywords in self.KNOWN_ZONES.items():
            for keyword in keywords:
                if keyword in text:
                    logger.info("Destination trouvée", destination=zone)
                    return zone
        
        return None
    
    def extract_amount(self, text: str) -> Optional[int]:
        """Extrait le montant du texte.
        
        Args:
            text: Texte normalisé
            
        Returns:
            int: Montant en XAF ou None
        """
        text = self.normalize_text(text)
        
        patterns = [
            r"(\d+)\s*(?:mille|famille|francs?|xaf?|fcfa)",
            r"(?:mille|famille)(\d+)",
            r"(\d+)\s*(?:francs?|xaf?|fcfa)",
            r"(\d+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                amount = int(match.group(1))
                if amount >= 100:
                    logger.info("Montant trouvé", amount=amount)
                    return amount
        
        return None
    
    def extract_seats(self, text: str) -> int:
        """Extrait le nombre de places.
        
        Args:
            text: Texte normalisé
            
        Returns:
            int: Nombre de places (défaut 1)
        """
        text = self.normalize_text(text)
        
        patterns = [
            r"(\d+)\s*(?:places?|personnes?|passagers?)",
            r"(?:places?|personnes?|passagers?)\s*(\d+)",
            r"(?:seul|seule)",
            r"(?:deux\s*(?:personnes?|places?))",
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text)
            if match:
                if i == 0 or i == 1:
                    return int(match.group(1))
                elif i == 2:
                    return 1
                elif i == 3:
                    return 2
        
        return 1
    
    def extract_proposal(self, transcription: str) -> Dict[str, any]:
        """Extrait les informations d'une proposition vocale.
        
        Args:
            transcription: Texte transcrit
            
        Returns:
            dict: {"destination": str, "amount": int, "seats": int}
        """
        destination = self.extract_destination(transcription)
        amount = self.extract_amount(transcription)
        seats = self.extract_seats(transcription)
        
        return {
            "destination": destination,
            "amount": amount,
            "seats": seats,
        }
    
    async def create_voice_proposal(
        self,
        db: AsyncSession,
        trip_id: str,
        client_id: str,
        transcription: str,
        audio_path: Optional[str] = None
    ) -> VoiceProposal:
        """Crée une proposition vocale.
        
        Args:
            db: Session de base de données
            trip_id: ID du trajet
            client_id: ID du client
            transcription: Texte transcrit
            audio_path: Chemin du fichier audio
            
        Returns:
            VoiceProposal: Proposition créée
        """
        extracted = self.extract_proposal(transcription)
        
        proposal = VoiceProposal(
            trip_id=trip_id,
            client_id=client_id,
            audio_path=audio_path,
            transcription=transcription,
            extracted_destination=extracted.get("destination"),
            extracted_amount=extracted.get("amount"),
            extracted_seats=extracted.get("seats"),
        )
        
        db.add(proposal)
        await db.commit()
        await db.refresh(proposal)
        
        logger.info(
            "Proposition vocale créée",
            trip_id=trip_id,
            destination=extracted.get("destination"),
            amount=extracted.get("amount")
        )
        
        return proposal


voice_proposal_service = VoiceProposalService()