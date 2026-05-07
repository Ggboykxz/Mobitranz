# ============================================================
# API Client pour Desktop Admin
# Fichier : desktop_admin/api_service.py
# Description : Client API connecté au backend
# ============================================================

import httpx
from typing import Optional, Dict, List
import json
import os


class AdminAPIClient:
    """Client API pour l'interface admin.
    
    Connecté au backend FastAPI pour toutes les opérations CRUD.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialise le client API."""
        self.base_url = base_url
        self._token: Optional[str] = None
        self._client = httpx.Client(timeout=30.0)
    
    def set_token(self, token: str):
        """Définit le token JWT."""
        self._token = token
    
    def _get_headers(self) -> Dict[str, str]:
        """Retourne les en-têtes avec authentication."""
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers
    
    # ============ AUTH ============
    def login(self, phone: str, password: str) -> Dict:
        """Connexion admin."""
        response = self._client.post(
            f"{self.base_url}/auth/login",
            json={"phone": phone, "password": password},
            headers=self._get_headers()
        )
        response.raise_for_status()
        data = response.json()
        if "access_token" in data:
            self.set_token(data["access_token"])
        return data
    
    # ============ USERS ============
    def get_users(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupère la liste des utilisateurs."""
        response = self._client.get(
            f"{self.base_url}/admin/users",
            params={"skip": skip, "limit": limit},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id: str) -> Dict:
        """Récupère un utilisateur."""
        response = self._client.get(
            f"{self.base_url}/users/users/{user_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def activate_user(self, user_id: str) -> Dict:
        """Active un utilisateur."""
        response = self._client.post(
            f"{self.base_url}/admin/users/{user_id}/activate",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def suspend_user(self, user_id: str) -> Dict:
        """Suspend un utilisateur."""
        response = self._client.post(
            f"{self.base_url}/admin/users/{user_id}/suspend",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # ============ DRIVERS ============
    def get_drivers(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupère la liste des chauffeurs."""
        response = self._client.get(
            f"{self.base_url}/admin/drivers",
            params={"skip": skip, "limit": limit},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def validate_driver(self, driver_id: str) -> Dict:
        """Valide un chauffeur."""
        response = self._client.post(
            f"{self.base_url}/admin/drivers/{driver_id}/validate",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_driver_location(self, driver_id: str) -> Dict:
        """Récupère la position GPS d'un chauffeur."""
        response = self._client.get(
            f"{self.base_url}/drivers/drivers/{driver_id}/location",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # ============ VEHICLES ============
    def get_vehicles(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupère la liste des véhicules."""
        response = self._client.get(
            f"{self.base_url}/admin/vehicles",
            params={"skip": skip, "limit": limit},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_vehicle_location(self, vehicle_id: str) -> Dict:
        """Récupère la position GPS d'un véhicule."""
        response = self._client.get(
            f"{self.base_url}/vehicles/vehicles/{vehicle_id}/location",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # ============ TRIPS ============
    def get_trips(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupère la liste des trajets."""
        response = self._client.get(
            f"{self.base_url}/trips/trips/",
            params={"skip": skip, "limit": limit},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_trip(self, trip_id: str) -> Dict:
        """Récupère un trajet."""
        response = self._client.get(
            f"{self.base_url}/trips/trips/{trip_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_active_trip(self, driver_id: str) -> Dict:
        """Récupère le trajet actif d'un chauffeur."""
        response = self._client.get(
            f"{self.base_url}/trips/trips/driver/{driver_id}/active",
            headers=self._get_headers()
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    
    # ============ TRANSACTIONS ============
    def get_transactions(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupère la liste des transactions."""
        response = self._client.get(
            f"{self.base_url}/admin/transactions",
            params={"skip": skip, "limit": limit},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_payment(self, payment_id: str) -> Dict:
        """Récupère une transaction."""
        response = self._client.get(
            f"{self.base_url}/payments/payments/{payment_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # ============ INCIDENTS ============
    def get_incidents(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupère la liste des incidents."""
        response = self._client.get(
            f"{self.base_url}/admin/incidents",
            params={"skip": skip, "limit": limit},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def resolve_incident(self, incident_id: str) -> Dict:
        """Résout un incident."""
        response = self._client.post(
            f"{self.base_url}/admin/incidents/{incident_id}/resolve",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # ============ ANALYTICS ============
    def get_kpis(self) -> Dict:
        """Récupère les KPIs du dashboard."""
        response = self._client.get(
            f"{self.base_url}/admin/admin/dashboard/kpis",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_analytics(self, period: str = "month") -> Dict:
        """Récupère les analytics."""
        response = self._client.get(
            f"{self.base_url}/analytics/analytics/kpis",
            params={"period": period},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_revenue_by_day(self, days: int = 30) -> List[Dict]:
        """Récupère les revenus par jour."""
        response = self._client.get(
            f"{self.base_url}/analytics/analytics/revenue/by-day",
            params={"days": days},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_trips_by_day(self, days: int = 30) -> List[Dict]:
        """Récupère les trajets par jour."""
        response = self._client.get(
            f"{self.base_url}/analytics/analytics/trips/by-day",
            params={"days": days},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_incidents_by_type(self) -> List[Dict]:
        """Récupère les incidents par type."""
        response = self._client.get(
            f"{self.base_url}/analytics/analytics/incidents/by-type",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # ============ REPORTS ============
    def export_csv(self, report_type: str) -> bytes:
        """Exporte un rapport CSV."""
        response = self._client.get(
            f"{self.base_url}/analytics/analytics/export/csv",
            params={"type": report_type},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.content
    
    def export_ministry_report(self) -> bytes:
        """Exporte le rapport ministère."""
        response = self._client.get(
            f"{self.base_url}/analytics/analytics/ministry-report",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.content
    
    # ============ AUDIT ============
    def get_logs(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Récupère les logs d'audit."""
        response = self._client.get(
            f"{self.base_url}/admin/admin/logs",
            params={"skip": skip, "limit": limit},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # ============ SYSTEM ============
    def get_health(self) -> Dict:
        """Vérifie la santé du système."""
        response = self._client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_backup(self) -> Dict:
        """Démarre une sauvegarde."""
        response = self._client.post(
            f"{self.base_url}/admin/admin/system/backup",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """Ferme le client."""
        self._client.close()


api_client = AdminAPIClient()