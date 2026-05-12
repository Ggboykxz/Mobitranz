import asyncio
import structlog
import httpx
from typing import Optional

from backend.config import settings
from backend.tasks.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    name="notification_tasks.send_push",
)
def send_push_notification_task(self, token: str, title: str, body: str, data: Optional[dict] = None) -> bool:
    try:
        return asyncio.run(_do_send_push(token, title, body, data))
    except Exception as exc:
        logger.error("Push notification task failed", token=token[:20], error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    name="notification_tasks.send_bulk",
)
def send_bulk_notification_task(self, tokens: list[str], title: str, body: str, data: Optional[dict] = None) -> bool:
    try:
        return asyncio.run(_do_send_bulk(tokens, title, body, data))
    except Exception as exc:
        logger.error("Bulk notification task failed", count=len(tokens), error=str(exc))
        raise self.retry(exc=exc)


async def _get_fcm_access_token() -> Optional[str]:
    try:
        import json as _json

        with open(settings.firebase_credentials_path, "r") as f:
            creds = _json.load(f)

        import time
        private_key = creds.get("private_key", "").replace("\\n", "\n")
        client_email = creds.get("client_email", "")
        scope = "https://www.googleapis.com/auth/firebase.messaging"

        from jose import jwt as jose_jwt
        now = int(time.time())
        assertion_payload = {
            "iss": client_email,
            "sub": client_email,
            "aud": "https://oauth2.googleapis.com/token",
            "iat": now,
            "exp": now + 3600,
            "scope": scope,
        }
        signed_jwt = jose_jwt.encode(assertion_payload, private_key, algorithm="RS256")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": signed_jwt,
                },
                timeout=15.0,
            )
            if resp.status_code == 200:
                return resp.json().get("access_token")
            logger.error("Erreur obtention token OAuth2 FCM", status=resp.status_code)
            return None
    except Exception as e:
        logger.error("Erreur génération token OAuth2 FCM", error=str(e))
        return None


async def _do_send_push(token: str, title: str, body: str, data: Optional[dict] = None) -> bool:
    if not settings.firebase_credentials_path:
        logger.warning("FCM non configuré, notification ignorée")
        return False

    try:
        import json as _json

        with open(settings.firebase_credentials_path, "r") as f:
            creds = _json.load(f)
        project_id_val = creds.get("project_id")
    except Exception as e:
        logger.error("Erreur chargement credentials FCM", error=str(e))
        return False

    access_token = await _get_fcm_access_token()
    if not access_token:
        logger.error("Impossible d'obtenir un token OAuth2 FCM")
        return False

    message = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body,
            },
            "data": data or {},
            "android": {
                "priority": "high",
                "notification": {
                    "channel_id": "mobitranz_default",
                },
            },
            "apns": {
                "payload": {
                    "aps": {
                        "sound": "default",
                    }
                }
            },
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://fcm.googleapis.com/v1/projects/{project_id_val}/messages:send",
                json=message,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(
                    "Notification envoyée",
                    message_id=result.get("name", "").split("/")[-1],
                    token=token[:20],
                )
                return True
            else:
                logger.error("Erreur FCM", status=response.status_code, body=response.text[:200])
                return False

    except httpx.TimeoutException:
        logger.error("FCM timeout")
        return False
    except Exception as e:
        logger.error("Erreur notification", error=str(e))
        return False


async def _do_send_bulk(tokens: list[str], title: str, body: str, data: Optional[dict] = None) -> bool:
    results = []
    for token in tokens:
        result = await _do_send_push(token, title, body, data)
        results.append(result)
    logger.info("Notifications en masse terminées", total=len(tokens), succeeded=sum(results))
    return any(results)
