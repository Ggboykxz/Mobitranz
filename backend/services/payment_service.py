# ============================================================
# Service Paiement MobiTranz
# Fichier : backend/services/payment_service.py
# Description : Intégration MoovMoney, Airtel Money, Stripe
# ============================================================

from typing import Optional
import httpx
import structlog
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.payment import Payment, PaymentStatus, PaymentMethod


logger = structlog.get_logger()


class PaymentService:
    """Service de paiement MobiTranz.
    
    Gère l'initiation et la vérification des paiements
    via MoovMoney et Airtel Money.
    """
    
    async def initiate_moovmoney_payment(
        self,
        phone: str,
        amount: int,
        reference: str
    ) -> dict:
        """Initie un paiement MoovMoney.
        
        Args:
            phone: Numéro de téléphone au format +241XXXXXXXX
            amount: Montant en FCFA
            reference: Référence unique du paiement
            
        Returns:
            dict: Réponse de l'API MoovMoney
        """
        if not settings.moovmoney_api_url:
            logger.warning("MoovMoney API non configurée")
            return {
                "status": "error",
                "message": "Service de paiement non disponible"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.moovmoney_api_url}/payments/initiate",
                    json={
                        "phone": phone,
                        "amount": amount,
                        "reference": reference,
                        "callback_url": f"https://api.mobitranz.ga/payments/webhook",
                    },
                    headers={
                        "Authorization": f"Bearer {settings.moovmoney_api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )
                
                data = response.json()
                logger.info(
                    "Paiement MoovMoney initié",
                    reference=reference,
                    status=data.get("status")
                )
                return data
                
            except httpx.TimeoutException:
                logger.error("Timeout MoovMoney", reference=reference)
                return {"status": "error", "message": "Délai d'attente dépassé"}
            except Exception as e:
                logger.error("Erreur MoovMoney", error=str(e))
                return {"status": "error", "message": str(e)}
    
    async def check_moovmoney_status(
        self,
        transaction_id: str
    ) -> dict:
        """Vérifie le statut d'un paiement MoovMoney.
        
        Args:
            transaction_id: ID de transaction MoovMoney
            
        Returns:
            dict: Statut du paiement
        """
        if not settings.moovmoney_api_url:
            return {"status": "error"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.moovmoney_api_url}/payments/{transaction_id}/status",
                    headers={
                        "Authorization": f"Bearer {settings.moovmoney_api_key}",
                    },
                    timeout=30.0,
                )
                return response.json()
            except Exception as e:
                logger.error("Erreur vérification MoovMoney", error=str(e))
                return {"status": "error"}
    
    async def initiate_airtelmoney_payment(
        self,
        phone: str,
        amount: int,
        reference: str
    ) -> dict:
        """Initie un paiement Airtel Money.
        
        Args:
            phone: Numéro de téléphone au format +241XXXXXXXX
            amount: Montant en FCFA
            reference: Référence unique du paiement
            
        Returns:
            dict: Réponse de l'API Airtel
        """
        if not settings.airtelmoney_api_url:
            logger.warning("Airtel Money API non configurée")
            return {
                "status": "error",
                "message": "Service de paiement non disponible"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.airtelmoney_api_url}/payments/initiate",
                    json={
                        "phone": phone,
                        "amount": amount,
                        "reference": reference,
                    },
                    headers={
                        "Authorization": f"Bearer {settings.airtelmoney_api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )
                
                data = response.json()
                logger.info(
                    "Paiement Airtel Money initiated",
                    reference=reference,
                    status=data.get("status")
                )
                return data
                
            except httpx.TimeoutException:
                logger.error("Timeout Airtel Money", reference=reference)
                return {"status": "error", "message": "Délai d'attente dépassé"}
            except Exception as e:
                logger.error("Erreur Airtel Money", error=str(e))
                return {"status": "error", "message": str(e)}
    
    async def create_payment_record(
        self,
        db: AsyncSession,
        trip_id: str,
        client_id: str,
        amount: int,
        method: PaymentMethod,
        phone_number: str
    ) -> Payment:
        """Crée un enregistrement de paiement.
        
        Args:
            db: Session de base de données
            trip_id: ID du trajet
            client_id: ID du client
            amount: Montant
            method: Méthode de paiement
            phone_number: Numéro de téléphone
            
        Returns:
            Payment: Enregistrement de paiement créé
        """
        payment = Payment(
            trip_id=trip_id,
            client_id=client_id,
            amount=amount,
            method=method,
            phone_number=phone_number,
            status=PaymentStatus.PENDING,
        )
        
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        
        logger.info(
            "Paiement créé",
            payment_id=payment.id,
            trip_id=trip_id
        )
        
        return payment
    
    async def mark_payment_completed(
        self,
        db: AsyncSession,
        payment: Payment,
        transaction_id: str,
        provider_reference: Optional[str] = None
    ):
        """Marque un paiement comme terminé.
        
        Args:
            db: Session de base de données
            payment: Paiement à mettre à jour
            transaction_id: ID de transaction externe
            provider_reference: Référence du provider
        """
        payment.status = PaymentStatus.COMPLETED
        payment.external_transaction_id = transaction_id
        payment.provider_reference = provider_reference
        payment.completed_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(
            "Paiement terminé",
            payment_id=payment.id,
            transaction_id=transaction_id
        )
    
    async def mark_payment_failed(
        self,
        db: AsyncSession,
        payment: Payment,
        reason: str
    ):
        """Marque un paiement comme échoué.
        
        Args:
            db: Session de base de données
            payment: Paiement à mettre à jour
            reason: Raison de l'échec
        """
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = reason
        payment.failed_at = datetime.utcnow()
        
        await db.commit()
        
        logger.warning(
            "Paiement échoué",
            payment_id=payment.id,
            reason=reason
        )


payment_service = PaymentService()