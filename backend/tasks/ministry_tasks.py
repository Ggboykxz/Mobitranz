import asyncio
import structlog
import httpx
from datetime import datetime

from backend.config import settings
from backend.tasks.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    name="ministry_tasks.send_transport_report",
)
def send_transport_report_task(self, data: dict) -> bool:
    try:
        return asyncio.run(_do_send_transport_report(data))
    except Exception as exc:
        logger.error("Transport report task failed", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    name="ministry_tasks.send_interior_report",
)
def send_interior_report_task(self, data: dict) -> bool:
    try:
        return asyncio.run(_do_send_interior_report(data))
    except Exception as exc:
        logger.error("Interior report task failed", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    name="ministry_tasks.send_sos_alert",
)
def send_sos_alert_task(self, incident_id: str, trip_id: str, latitude: float, longitude: float, timestamp: str) -> bool:
    try:
        alert_data = {
            "incident_type": "SOS",
            "incident_id": incident_id,
            "trip_id": trip_id,
            "location": {"latitude": latitude, "longitude": longitude},
            "timestamp": timestamp,
            "source": "MobiTranz",
        }
        return asyncio.run(_do_send_interior_report(alert_data))
    except Exception as exc:
        logger.error("SOS alert task failed", incident_id=incident_id, error=str(exc))
        raise self.retry(exc=exc)


async def _do_send_transport_report(data: dict) -> bool:
    if not settings.ministry_transport_webhook:
        logger.warning("Ministère Transport webhook non configuré")
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.ministry_transport_webhook,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": settings.ministry_api_key or "",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            logger.info("Rapport envoyé au Ministère des Transports")
            return True
    except httpx.TimeoutException:
        logger.error("Timeout envoi rapport Ministère Transport")
        return False
    except Exception as e:
        logger.error("Erreur envoi rapport Ministère Transport", error=str(e))
        return False


async def _do_send_interior_report(data: dict) -> bool:
    if not settings.ministry_interior_webhook:
        logger.warning("Ministère Intérieur webhook non configuré")
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.ministry_interior_webhook,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": settings.ministry_api_key or "",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            logger.info("Rapport envoyé au Ministère de l'Intérieur")
            return True
    except httpx.TimeoutException:
        logger.error("Timeout envoi rapport Ministère Intérieur")
        return False
    except Exception as e:
        logger.error("Erreur envoi rapport Ministère Intérieur", error=str(e))
        return False
