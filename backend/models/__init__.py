# ============================================================
# Modèles SQLAlchemy MobiTranz
# Fichier : backend/models/__init__.py
# Description : Package des modèles de base de données
# ============================================================

from backend.models.user import User
from backend.models.driver import Driver
from backend.models.vehicle import Vehicle
from backend.models.trip import Trip
from backend.models.payment import Payment
from backend.models.recording import Recording
from backend.models.voice_proposal import VoiceProposal
from backend.models.incident import Incident
from backend.models.audit_log import AuditLog

__all__ = [
    "User",
    "Driver", 
    "Vehicle",
    "Trip",
    "Payment",
    "Recording",
    "VoiceProposal",
    "Incident",
    "AuditLog",
]