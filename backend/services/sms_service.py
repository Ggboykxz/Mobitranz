import structlog
from typing import Optional

from backend.config import settings

logger = structlog.get_logger()


class SMSService:
    def __init__(self):
        self.api_key: Optional[str] = settings.africastalking_api_key
        self.username: Optional[str] = settings.africastalking_username
        self.sender_id: Optional[str] = settings.africastalking_sender_id
        self._client = None

    async def _get_client(self):
        if self._client is not None:
            return self._client
        if self.api_key and self.username:
            import httpx
            self._client = httpx.AsyncClient(
                base_url="https://api.africastalking.com",
                headers={
                    "apiKey": self.api_key,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
            return self._client
        return None

    async def send_sms(self, to: str, message: str) -> dict:
        client = await self._get_client()
        if client is None:
            logger.info(
                "SMS non configuré (console fallback)",
                to=to,
                message=message,
            )
            return {"status": "logged", "to": to, "message": message}

        try:
            response = await client.post(
                "/version1/messaging",
                data={
                    "username": self.username,
                    "to": to,
                    "message": message,
                    "from": self.sender_id or "",
                },
            )
            result = response.json()
            logger.info("SMS envoyé via Africa's Talking", to=to, response=result)
            return {"status": "sent", "provider_response": result}
        except Exception as e:
            logger.error("Échec envoi SMS", to=to, error=str(e))
            return {"status": "failed", "error": str(e)}

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


sms_service = SMSService()
