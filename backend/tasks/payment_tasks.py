import asyncio
import structlog
import httpx

from backend.config import settings
from backend.tasks.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    name="payment_tasks.initiate_moovmoney",
)
def initiate_moovmoney_payment_task(self, phone: str, amount: int, reference: str) -> dict:
    try:
        result = asyncio.run(_do_moovmoney_payment(phone, amount, reference))
        return result
    except Exception as exc:
        logger.error("MoovMoney task failed", reference=reference, error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    name="payment_tasks.initiate_airtelmoney",
)
def initiate_airtelmoney_payment_task(self, phone: str, amount: int, reference: str) -> dict:
    try:
        result = asyncio.run(_do_airtelmoney_payment(phone, amount, reference))
        return result
    except Exception as exc:
        logger.error("Airtel Money task failed", reference=reference, error=str(exc))
        raise self.retry(exc=exc)


async def _do_moovmoney_payment(phone: str, amount: int, reference: str) -> dict:
    if not settings.moovmoney_api_url:
        logger.warning("MoovMoney API non configurée")
        return {"status": "error", "message": "Service de paiement non disponible"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.moovmoney_api_url}/payments/initiate",
                json={
                    "phone": phone,
                    "amount": amount,
                    "reference": reference,
                    "callback_url": "https://api.mobitranz.ga/payments/webhook",
                },
                headers={
                    "Authorization": f"Bearer {settings.moovmoney_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            data = response.json()
            logger.info("Paiement MoovMoney initié", reference=reference, status=data.get("status"))
            return data
        except httpx.TimeoutException:
            logger.error("Timeout MoovMoney", reference=reference)
            return {"status": "error", "message": "Délai d'attente dépassé"}
        except Exception as e:
            logger.error("Erreur MoovMoney", error=str(e), reference=reference)
            return {"status": "error", "message": str(e)}


async def _do_airtelmoney_payment(phone: str, amount: int, reference: str) -> dict:
    if not settings.airtelmoney_api_url:
        logger.warning("Airtel Money API non configurée")
        return {"status": "error", "message": "Service de paiement non disponible"}

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
            logger.info("Paiement Airtel Money initié", reference=reference, status=data.get("status"))
            return data
        except httpx.TimeoutException:
            logger.error("Timeout Airtel Money", reference=reference)
            return {"status": "error", "message": "Délai d'attente dépassé"}
        except Exception as e:
            logger.error("Erreur Airtel Money", error=str(e), reference=reference)
            return {"status": "error", "message": str(e)}
