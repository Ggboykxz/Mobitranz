import pytest
from unittest.mock import AsyncMock, MagicMock


class TestVoiceProposalService:

    def test_normalize_text(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.normalize_text("Café")
        assert "cafe" in result

    def test_normalize_text_accents(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.normalize_text("École")
        assert "ecole" in result

    def test_extract_destination_centre_ville(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_destination("Je vais au centre-ville")
        assert result == "centre-ville"

    def test_extract_destination_owendo(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_destination("Direction owendo")
        assert result == "owendo"

    def test_extract_destination_libreville(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_destination("Vers libreville")
        assert result == "libreville"

    def test_extract_destination_not_found(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_destination("nulle part")
        assert result is None

    def test_extract_amount_mille(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_amount("Mille francs")
        assert result == 1000

    def test_extract_amount_chiffre(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_amount("2000 francs")
        assert result == 2000

    def test_extract_amount_not_found(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_amount("Bonjour")
        assert result is None

    def test_extract_seats_un(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_seats("une place")
        assert result == 1

    def test_extract_seats_deux(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_seats("deux personnes")
        assert result == 2

    def test_known_zones(self):
        from backend.services.voice_service import VoiceProposalService

        assert "centre-ville" in VoiceProposalService.KNOWN_ZONES
        assert "owendo" in VoiceProposalService.KNOWN_ZONES

    def test_french_amounts(self):
        from backend.services.voice_service import VoiceProposalService

        assert VoiceProposalService.FRENCH_AMOUNTS["mille"] == 1000

    def test_number_words(self):
        from backend.services.voice_service import VoiceProposalService

        assert VoiceProposalService.NUMBER_WORDS["un"] == 1
        assert VoiceProposalService.NUMBER_WORDS["cinq"] == 5
