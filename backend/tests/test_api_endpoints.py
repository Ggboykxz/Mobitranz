# ============================================================
# Tests API Routers
# Fichier : backend/tests/test_api_endpoints.py
# ============================================================

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from backend.main import app


class TestHealthEndpoint:
    """Tests pour l'endpoint health."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "degraded"]

    @pytest.mark.asyncio
    async def test_health_services(self):
        """Test health check inclut les services."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            
        data = response.json()
        assert "services" in data


class TestAuthEndpoints:
    """Tests pour les endpoints d'authentification."""

    @pytest.mark.asyncio
    async def test_register_validation(self):
        """Test validation inscription."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/auth/register", json={
                "phone": "invalid"
            })
            
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_validation(self):
        """Test validation connexion."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/auth/login", json={
                "phone": "invalid"
            })
            
        assert response.status_code == 422


class TestTripsEndpoints:
    """Tests pour les endpoints de trajets."""

    @pytest.mark.asyncio
    async def test_create_trip_validation(self):
        """Test validation création trajet."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/trips/", json={})
            
        assert response.status_code == 422


class TestPaymentsEndpoints:
    """Tests pour les endpoints de paiements."""

    @pytest.mark.asyncio
    async def test_initiate_payment_validation(self):
        """Test validation paiement."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/payments/initiate", json={})
            
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_payment_not_found(self):
        """Test paiement non trouvé."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/payments/nonexistent")
            
        assert response.status_code == 404