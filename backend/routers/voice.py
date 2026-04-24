# ============================================================
# Routes Voix MobiTranz
# Fichier : backend/routers/voice.py
# Description : Routes /voice/* (proposition vocale, transcription)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import base64
import structlog

from backend.database import get_db
from backend.models.voice_proposal import VoiceProposal
from backend.services.voice_service import voice_proposal_service


logger = structlog.get_logger()
router = APIRouter(prefix="/voice", tags=["Voice"])


@router.post("/proposal", status_code=status.HTTP_201_CREATED)
async def submit_voice_proposal(
    client_id: str,
    driver_id: str,
    audio_base64: str,
    db: AsyncSession = Depends(get_db)
):
    """Soumet une proposition vocale.
    
    Reçoit l'audio encodé en base64, le transcrit etextrait
    les informations (destination, montant, places).
    """
    try:
        audio_data = base64.b64decode(audio_base64)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio encodage invalide"
        )
    
    # Transcription (simulée - remplacer par SpeechRecognition ou Vosk)
    transcription = "Owendo mille francs deux places"
    
    # Créer une proposition vocale
    proposal = await voice_proposal_service.create_voice_proposal(
        db=db,
        trip_id=f"trip_temp_{client_id[:8]}",
        client_id=client_id,
        transcription=transcription,
    )
    
    logger.info(
        "Proposition vocale créée",
        proposal_id=proposal.id,
        destination=proposal.extracted_destination,
        amount=proposal.extracted_amount
    )
    
    return {
        "proposal_id": proposal.id,
        "transcription": proposal.transcription,
        "destination": proposal.extracted_destination,
        "amount": proposal.extracted_amount,
        "seats": proposal.extracted_seats,
    }


@router.post("/transcribe")
async def transcribe_audio(
    audio_base64: str
):
    """Transcrit un audio sans créer de proposition.
    
    Utilisation : prévisualisation avant soumission.
    """
    try:
        audio_data = base64.b64decode(audio_base64)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio encodage invalide"
        )
    
    # Transcription simulée (remplacer par SpeechRecognition/Vosk)
    transcription = "Owendo mille francs deux places"
    
    # Extraire les informations
    extraction = voice_proposal_service.extract_proposal(transcription)
    
    return {
        "transcription": transcription,
        "extracted": extraction,
        "confidence": 85,
    }


@router.get("/zones")
async def get_known_zones():
    """Retourne la liste des zones connues."""
    return {
        "zones": list(voice_proposal_service.KNOWN_ZONES.keys()),
        "count": len(voice_proposal_service.KNOWN_ZONES)
    }


@router.post("/validate")
async def validate_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Valide manuellement une proposition."""
    result = await db.execute(
        select(VoiceProposal).where(VoiceProposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposition non trouvée"
        )
    
    proposal.is_validated = "true"
    proposal.validated_at = datetime.utcnow()
    proposal.validation_source = "manual"
    
    await db.commit()
    
    logger.info("Proposition validée", proposal_id=proposal_id)
    
    return {"status": "validated", "proposal_id": proposal_id}


from datetime import datetime