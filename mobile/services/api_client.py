import httpx
from typing import Optional, Dict
import mobile.config as config


class APIClient:
    def __init__(self):
        self._client = httpx.AsyncClient(
            base_url=config.API_BASE_URL,
            timeout=config.API_TIMEOUT,
        )
        self._access_token: Optional[str] = None

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    def set_token(self, token: str):
        self._access_token = token

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    def _url(self, endpoint: str) -> str:
        return f"{config.API_PREFIX}{endpoint}"

    async def post(self, endpoint: str, data: Dict) -> Dict:
        if not self._client:
            raise RuntimeError("API client not initialized")
        response = await self._client.post(
            self._url(endpoint),
            json=data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        if not self._client:
            raise RuntimeError("API client not initialized")
        response = await self._client.get(
            self._url(endpoint),
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    async def login(self, phone: str, password: str) -> Dict:
        return await self.post("/auth/login", {
            "phone": phone,
            "password": password
        })

    async def register(self, phone: str, password: str, **kwargs) -> Dict:
        return await self.post("/auth/register", {
            "phone": phone,
            "password": password,
            **kwargs
        })

    async def get_trips(self) -> Dict:
        return await self.get("/trips")

    async def get_trips_active(self) -> Dict:
        return await self.get("/trips/active")

    async def create_trip(self, data: Dict) -> Dict:
        return await self.post("/trips", data)

    async def get_trip(self, trip_id: str) -> Dict:
        return await self.get(f"/trips/{trip_id}")

    async def start_payment(self, trip_id: str, method: str, phone: str) -> Dict:
        return await self.post("/payments/initiate", {
            "trip_id": trip_id,
            "method": method,
            "phone_number": phone
        })

    async def submit_voice_proposal(self, data: Dict) -> Dict:
        return await self.post("/voice/proposal", data)

    async def submit_rating(self, data: Dict) -> Dict:
        return await self.post("/ratings", data)


api_client = APIClient()
