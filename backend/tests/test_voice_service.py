import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestVoiceNLP:
    def setup_method(self):
        from backend.services.voice_service import voice_proposal_service

        self.service = voice_proposal_service

    def test_normalize_text(self):
        assert self.service.normalize_text("Café") == "cafe"
        assert self.service.normalize_text("École") == "ecole"
        assert self.service.normalize_text("Français") == "francais"
        assert self.service.normalize_text("MobiTranz") == "mobitranz"
        assert self.service.normalize_text("  Spaces  ") == "  spaces  "

    def test_extract_destination_known_zones(self):
        assert (
            self.service.extract_destination("Je vais au centre-ville")
            == "centre-ville"
        )
        assert self.service.extract_destination("Direction owendo") == "owendo"
        assert (
            self.service.extract_destination("Je vais à Libreville")
            == "libreville"
        )
        assert self.service.extract_destination("Vers Port-Gentil") == "port-gentil"
        assert self.service.extract_destination("Aller à Ntoum") == "ntoum"
        assert self.service.extract_destination("À Angondjé SVP") == "angondje"
        assert self.service.extract_destination("Zone Lalala") == "lalala"

    def test_extract_destination_with_keywords(self):
        assert self.service.extract_destination("Je suis au plateau") == "centre-ville"
        assert self.service.extract_destination("Je vais au PK5") == "pk5"
        assert self.service.extract_destination("Mondah s'il vous plaît") == "akanda"

    def test_extract_destination_not_found(self):
        assert self.service.extract_destination("Je vais nulle part") is None
        assert self.service.extract_destination("Bonjour") is None

    def test_extract_amount_french_words(self):
        assert self.service.extract_amount("Mille francs") == 1000
        assert self.service.extract_amount("mille") == 1000

    def test_extract_amount_digits(self):
        assert self.service.extract_amount("1500 francs") == 1500
        assert self.service.extract_amount("2000 FCFA") == 2000
        assert self.service.extract_amount("500 XAF") == 500

    def test_extract_amount_not_found(self):
        assert self.service.extract_amount("Bonjour") is None
        assert self.service.extract_amount("Je ne sais pas") is None

    def test_extract_seats(self):
        assert self.service.extract_seats("Je suis seul") == 1
        assert self.service.extract_seats("Une place") == 1
        assert self.service.extract_seats("Deux personnes") == 2
        assert self.service.extract_seats("3 places") == 3
        assert self.service.extract_seats("4 personnes") == 4
        assert self.service.extract_seats("places 5") == 5
        assert self.service.extract_seats("Bonjour") == 1

    def test_extract_proposal_complete(self):
        result = self.service.extract_proposal(
            "Je vais au centre-ville, mille francs, seul"
        )
        assert result["destination"] == "centre-ville"
        assert result["amount"] == 1000
        assert result["seats"] == 1

    def test_extract_proposal_partial(self):
        result = self.service.extract_proposal("Direction owendo")
        assert result["destination"] == "owendo"
        assert result["amount"] is None
        assert result["seats"] == 1

    def test_extract_proposal_no_match(self):
        result = self.service.extract_proposal("Bonjour comment ça va")
        assert result["destination"] is None
        assert result["amount"] is None
        assert result["seats"] == 1

    def test_extract_seats_various_formats(self):
        assert self.service.extract_seats("3 passagers") == 3
        assert self.service.extract_seats("2 places") == 2
        assert self.service.extract_seats("seule") == 1


class TestVoiceExtractionFlow:
    def test_extract_proposition_owendo(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_proposal("Direction owendo 1000 francs seul")
        assert result["destination"] == "owendo"
        assert result["amount"] == 1000
        assert result["seats"] == 1

    def test_extract_proposition_centre_ville_multi(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_proposal("Centre-ville 500 francs 3 places")
        assert result["destination"] == "centre-ville"
        assert result["amount"] == 500
        assert result["seats"] == 3

    def test_extract_proposition_libreville(self):
        from backend.services.voice_service import voice_proposal_service

        result = voice_proposal_service.extract_proposal("Libreville mille francs")
        assert result["destination"] == "libreville"
        assert result["amount"] == 1000
        assert result["seats"] == 1


class TestVoiceConstants:
    def test_known_zones_defined(self):
        from backend.services.voice_service import VoiceProposalService

        assert "centre-ville" in VoiceProposalService.KNOWN_ZONES
        assert "owendo" in VoiceProposalService.KNOWN_ZONES
        assert "akanda" in VoiceProposalService.KNOWN_ZONES
        assert "libreville" in VoiceProposalService.KNOWN_ZONES
        assert "port-gentil" in VoiceProposalService.KNOWN_ZONES
        assert "pk5" in VoiceProposalService.KNOWN_ZONES
        assert "lalala" in VoiceProposalService.KNOWN_ZONES

    def test_french_amounts_defined(self):
        from backend.services.voice_service import VoiceProposalService

        assert VoiceProposalService.FRENCH_AMOUNTS["mille"] == 1000
        assert VoiceProposalService.FRENCH_AMOUNTS["deux-mille"] == 2000
        assert VoiceProposalService.FRENCH_AMOUNTS["cinq-mille"] == 5000
        assert VoiceProposalService.FRENCH_AMOUNTS["dix-mille"] == 10000

    def test_number_words_defined(self):
        from backend.services.voice_service import VoiceProposalService

        assert VoiceProposalService.NUMBER_WORDS["un"] == 1
        assert VoiceProposalService.NUMBER_WORDS["deux"] == 2
        assert VoiceProposalService.NUMBER_WORDS["cinq"] == 5
        assert VoiceProposalService.NUMBER_WORDS["dix"] == 10
