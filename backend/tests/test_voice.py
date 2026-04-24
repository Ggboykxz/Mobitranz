# ============================================================
# Tests Voice Service
# Fichier : backend/tests/test_voice.py
# ============================================================

import pytest
from backend.services.voice_service import voice_proposal_service


class TestVoiceProposalService:
    """Tests pour le service de proposition vocale."""
    
    def test_known_zones_loaded(self):
        """Test que les zones connues sont chargées."""
        assert len(voice_proposal_service.KNOWN_ZONES) > 0
    
    def test_extract_destination_centre_ville(self):
        """Test l'extraction du centre-ville."""
        text = "Je vais au centre-ville"
        destination = voice_proposal_service.extract_destination(text)
        
        assert destination == "centre-ville"
    
    def test_extract_destination_owendo(self):
        """Test l'extraction d'Owendo."""
        text = "Aller à owendo"
        destination = voice_proposal_service.extract_destination(text)
        
        assert destination == "owendo"
    
    def test_extract_destination_not_found(self):
        """Test quand la destination n'est pas trouvée."""
        text = "Je vais quelque part"
        destination = voice_proposal_service.extract_destination(text)
        
        assert destination is None
    
    def test_extract_amount_mille(self):
        """Test l'extraction du montant en texte."""
        text = "Owendo mille francs deux places"
        amount = voice_proposal_service.extract_amount(text)
        
        assert amount == 1000
    
    def test_extract_amount_number(self):
        """Test l'extraction du montant en chiffre."""
        text = "Owendo 1500 francs"
        amount = voice_proposal_service.extract_amount(text)
        
        assert amount == 1500
    
    def test_extract_amount_not_found(self):
        """Test quand le montant n'est pas trouvé."""
        text = "Owendo svp"
        amount = voice_proposal_service.extract_amount(text)
        
        assert amount is None
    
    def test_extract_seats_two(self):
        """Test l'extraction de deux places."""
        text = "Owendo mille francs deux places"
        seats = voice_proposal_service.extract_seats(text)
        
        assert seats == 2
    
    def test_extract_seats_one(self):
        """Test l'extraction d'une place (seul)."""
        text = "Owendo mille francs"
        seats = voice_proposal_service.extract_seats(text)
        
        assert seats == 1
    
    def test_extract_proposal_complete(self):
        """Test l'extraction complète d'une proposition."""
        transcription = "Owendo mille francs deux places"
        proposal = voice_proposal_service.extract_proposal(transcription)
        
        assert proposal["destination"] == "owendo"
        assert proposal["amount"] == 1000
        assert proposal["seats"] == 2
    
    def test_normalize_text(self):
        """Test la normalisation du texte."""
        text = "Owendo"
        normalized = voice_proposal_service.normalize_text(text)
        
        assert normalized == "owendo"
    
    def test_number_words_mapping(self):
        """Test le mapping des mots en nombres."""
        assert voice_proposal_service.NUMBER_WORDS["un"] == 1
        assert voice_proposal_service.NUMBER_WORDS["dix"] == 10