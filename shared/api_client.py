# ============================================================
# Client HTTP centralisé MobiTranz
# Fichier : shared/api_client.py
# Description : Point d'accès الوحيد à l'API backend
# ============================================================

import httpx
import time
import logging
import os
from typing import Optional, Any, Dict, Callable
from dataclasses import dataclass

logger = logging.getLogger("mobitranz.api_client")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT_SECONDS", "15"))


@dataclass
class APIResponse:
    """Réponse normalisée de l'API."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: int = 0


class TokenStorage:
    """Stockage des tokens JWT."""
    _access_token: Optional[str] = None
    _refresh_token: Optional[str] = None
    _token_expires_at: float = 0

    @classmethod
    def store(cls, access_token: str, refresh_token: str, expires_in_seconds: int = 900):
        cls._access_token = access_token
        cls._refresh_token = refresh_token
        cls._token_expires_at = time.time() + expires_in_seconds - 30
        logger.info("tokens_stored", expires_in=expires_in_seconds)

    @classmethod
    def get_access_token(cls) -> Optional[str]:
        if cls._access_token and time.time() < cls._token_expires_at:
            return cls._access_token
        return None

    @classmethod
    def get_refresh_token(cls) -> Optional[str]:
        return cls._refresh_token

    @classmethod
    def clear(cls):
        cls._access_token = None
        cls._refresh_token = None
        cls._token_expires_at = 0
        logger.info("tokens_cleared")


class MobiTranzClient:
    """Client HTTP pour les interfaces GUI."""

    def __init__(self, base_url: str = None):
        self._base_url = base_url or API_BASE_URL
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Client": "MobiTranz-Desktop/1.0",
        }

    def _get_headers(self) -> Dict[str, str]:
        headers = self._headers.copy()
        token = TokenStorage.get_access_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> APIResponse:
        """Exécute une requête HTTP."""
        url = f"{self._base_url}{endpoint}"

        try:
            with httpx.Client(timeout=API_TIMEOUT) as client:
                response = client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=self._get_headers(),
                )

            logger.info("api_request", method=method, endpoint=endpoint, status=response.status_code)

            if response.status_code == 401:
                if self._refresh_token():
                    return self.request(method, endpoint, data, params)
                TokenStorage.clear()
                return APIResponse(success=False, error="Session expirée", status_code=401)

            if response.status_code >= 400:
                try:
                    error_detail = response.json().get("detail", "Erreur")
                except Exception:
                    error_detail = response.text
                return APIResponse(success=False, error=str(error_detail), status_code=response.status_code)

            try:
                return APIResponse(success=True, data=response.json(), status_code=response.status_code)
            except Exception:
                return APIResponse(success=True, data={}, status_code=response.status_code)

        except httpx.ConnectError:
            return APIResponse(success=False, error="Serveur inaccessible", status_code=0)
        except httpx.TimeoutException:
            return APIResponse(success=False, error="Délai dépassé", status_code=0)
        except Exception as e:
            logger.error("api_error", error=str(e))
            return APIResponse(success=False, error=str(e), status_code=0)

    def _refresh_token(self) -> bool:
        """Tente de rafraichir le token."""
        refresh_token = TokenStorage.get_refresh_token()
        if not refresh_token:
            return False

        try:
            with httpx.Client(timeout=10) as client:
                response = client.post(
                    f"{self._base_url}/auth/refresh",
                    json={"refresh_token": refresh_token},
                    headers=self._headers,
                )

            if response.status_code == 200:
                data = response.json()
                TokenStorage.store(
                    access_token=data["access_token"],
                    refresh_token=data["refresh_token"],
                    expires_in_seconds=data.get("expires_in", 900),
                )
                return True
        except Exception:
            pass
        return False

    def get(self, endpoint: str, params: dict = None) -> APIResponse:
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: dict = None) -> APIResponse:
        return self.request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: dict = None) -> APIResponse:
        return self.request("PUT", endpoint, data=data)

    def patch(self, endpoint: str, data: dict = None) -> APIResponse:
        return self.request("PATCH", endpoint, data=data)

    def delete(self, endpoint: str) -> APIResponse:
        return self.request("DELETE", endpoint)


api = MobiTranzClient()