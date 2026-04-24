# ============================================================
# Routes Paiements MobiTranz
# Fichier : backend/routers/payments.py
# Description : Routes /payments/* (initiation, webhook, confirmation)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import structlog

from backend.database import get_db
from backend.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentWebhook,
    PaymentConfirmRequest,
)
from backend.models.payment import Payment, PaymentStatus, PaymentMethod
from backend.models.trip import Trip, TripStatus
from backend.services.payment_service import payment_service


logger = structlog.get_logger()
router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/initiate", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def initiate_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Initie un paiement pour un trajet.
    
    Crée un enregistrement de paiement et initiates l'appel API
    vers le provider (MoovMoney ou Airtel Money).
    """
    # Vérifier le trajet
    result = await db.execute(select(Trip).where(Trip.id == data.trip_id))
    trip = result.scalar_one_or_none()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trajet non trouvé"
        )
    
    if trip.status != TripStatus.HORN_PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trajet non validé par le klaxon"
        )
    
    # Créer l'enregistrement de paiement
    payment = await payment_service.create_payment_record(
        db=db,
        trip_id=trip.id,
        client_id=trip.client_ids[0] if trip.client_ids else "",
        amount=trip.amount,
        method=PaymentMethod(data.method),
        phone_number=data.phone_number
    )
    
    # Initier l'appel API au provider
    if data.method == "moovmoney":
        api_response = await payment_service.initiate_moovmoney_payment(
            phone=data.phone_number,
            amount=trip.amount,
            reference=payment.id
        )
    elif data.method == "airtelmoney":
        api_response = await payment_service.initiate_airtelmoney_payment(
            phone=data.phone_number,
            amount=trip.amount,
            reference=payment.id
        )
    else:
        api_response = {"status": "pending", "message": "Méthode non supportée"}
    
    # Mettre à jour le paiement avec la réponse du provider
    if api_response.get("status") == "success":
        payment.external_transaction_id = api_response.get("transaction_id")
        payment.provider_reference = api_response.get("provider_reference")
        payment.status = PaymentStatus.PROCESSING
        trip.status = TripStatus.PAYMENT_PENDING
    else:
        payment.provider_response = str(api_response)
        payment.status = PaymentStatus.FAILED
    
    await db.commit()
    await db.refresh(payment)
    
    logger.info(
        "Paiement initiated",
        payment_id=payment.id,
        trip_id=trip.id,
        method=data.method
    )
    
    return payment


@router.post("/webhook")
async def payment_webhook(
    data: PaymentWebhook,
    db: AsyncSession = Depends(get_db)
):
    """Webhook pour recevoir les callbacks des providers de paiement.
    
    Endpoint appelé par MoovMoney/Airtel Money lors du changement
    de statut d'un paiement.
    """
    # Trouver le paiement par transaction ID externe
    result = await db.execute(
        select(Payment).where(
            Payment.external_transaction_id == data.transaction_id
        )
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        logger.warning("Webhook: paiement non trouvé", transaction_id=data.transaction_id)
        return {"status": "ignored"}
    
    # Mettre à jour selon le statut
    if data.status == "success":
        await payment_service.mark_payment_completed(
            db=db,
            payment=payment,
            transaction_id=data.transaction_id
        )
        
        # Mettre à jour le trajet
        trip_result = await db.execute(
            select(Trip).where(Trip.id == payment.trip_id)
        )
        trip = trip_result.scalar_one_or_none()
        if trip:
            trip.payment_at = datetime.utcnow()
        
        logger.info("Paiement confirmé via webhook", payment_id=payment.id)
        
    elif data.status == "failed":
        await payment_service.mark_payment_failed(
            db=db,
            payment=payment,
            reason=data.message or "Échec via webhook"
        )
        logger.warning("Paiement échoué via webhook", payment_id=payment.id)
    
    await db.commit()
    
    return {"status": "received"}


@router.post("/confirm", response_model=PaymentResponse)
async def confirm_payment(
    data: PaymentConfirmRequest,
    db: AsyncSession = Depends(get_db)
):
    """Confirme manuellement un paiement (pour fallback ou test).
    
    Vérifie le statut auprès du provider et met à jour
    l'enregistrement local.
    """
    result = await db.execute(
        select(Payment).where(
            Payment.external_transaction_id == data.transaction_id
        )
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paiement non trouvé"
        )
    
    # Vérifier le statut auprès du provider
    if payment.method == PaymentMethod.MOOVMONEY:
        status_response = await payment_service.check_moovmoney_status(
            data.transaction_id
        )
    else:
        status_response = {"status": "unknown"}
    
    if status_response.get("status") == "success":
        await payment_service.mark_payment_completed(
            db=db,
            payment=payment,
            transaction_id=data.transaction_id
        )
        
        # Mettre à jour le trajet
        trip_result = await db.execute(
            select(Trip).where(Trip.id == payment.trip_id)
        )
        trip = trip_result.scalar_one_or_none()
        if trip:
            trip.payment_at = datetime.utcnow()
        
        await db.commit()
        logger.info("Paiement confirmé", payment_id=payment.id)
    
    await db.refresh(payment)
    return payment


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Récupère les détails d'un paiement."""
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paiement non trouvé"
        )
    
    return payment


@router.get("/trip/{trip_id}")
async def get_payment_by_trip(
    trip_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Récupère le paiement d'un trajet."""
    result = await db.execute(
        select(Payment).where(Payment.trip_id == trip_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        return None
    
    return {
        "id": payment.id,
        "amount": payment.amount,
        "method": payment.method.value,
        "status": payment.status.value,
        "created_at": payment.created_at,
        "completed_at": payment.completed_at,
    }