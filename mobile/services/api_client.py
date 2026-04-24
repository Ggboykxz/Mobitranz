# ============================================================
# Client API Mobile
# Fichier : mobile/services/api_client.py
# Description : Client HTTP vers backend (httpx async)
# ============================================================

import httpx
from typing import Optional, Dict
import mobile.config as config


class APIClient:
    """Client HTTP pour l'API MobiTranz.
    
    Gère les requêtes vers le backend avec gestion
    des tokens JWT et erreurs.
    """
    
    def __init__(self):
        """Initialise le client API."""
        self._client = None
        self._access_token: Optional[str] = None
    
    async def __aenter__(self):
        """Entre dans le contexte async."""
        self._client = httpx.AsyncClient(
            base_url=config.API_BASE_URL,
            timeout=config.API_TIMEOUT,
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Sort du contexte async."""
        if self._client:
            await self._client.aclose()
    
    def set_token(self, token: str):
        """Définit le token JWT."""
        self._access_token = token
    
    def _get_headers(self) -> Dict[str, str]:
        """Retourne les en-têtes avec authentication."""
        headers = {"Content-Type": "application/json"}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers
    
    async def post(self, endpoint: str, data: Dict) -> Dict:
        """Envoie une requête POST."""
        response = await self._client.post(
            endpoint,
            json=data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Envoie une requête GET."""
        response = await self._client.get(
            endpoint,
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def login(self, phone: str, password: str) -> Dict:
        """Connexion utilisateur."""
        return await self.post("/auth/login", {
            "phone": phone,
            "password": password
        })
    
    async def register(self, phone: str, password: str, **kwargs) -> Dict:
        """Inscription utilisateur."""
        return await self.post("/auth/register", {
            "phone": phone,
            "password": password,
            **kwargs
        })
    
    async def get_trips(self) -> Dict:
        """Récupère la liste des trajets."""
        return await self.get("/trips")
    
    async def create_trip(self, data: Dict) -> Dict:
        """Crée un trajet."""
        return await self.post("/trips/", data)
    
    async def get_trip(self, trip_id: str) -> Dict:
        """Récupère un trajet."""
        return await self.get(f"/trips/{trip_id}")
    
    async def start_payment(self, trip_id: str, method: str, phone: str) -> Dict:
        """Démarre un paiement."""
        return await self.post("/payments/initiate", {
            "trip_id": trip_id,
            "method": method,
            "phone_number": phone
        })
    
    async def submit_voice_proposal(self, data: Dict) -> Dict:
        """Soumet une proposition vocale."""
        return await self.post("/voice/proposal", data)


api_client = APIClient()