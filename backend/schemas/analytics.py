# ============================================================
# Schémas Analytics et Rapports
# Fichier : backend/schemas/analytics.py
# Description : Schémas pour les analytics et rapports ministériels
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class KPIsResponse(BaseModel):
    """Schéma pour les KPIs du dashboard."""
    
    trips_today: int
    revenue_today: int
    active_drivers: int
    active_vehicles: int
    active_clients: int
    open_incidents: int
    timestamp: str


class TripsByDayResponse(BaseModel):
    """Schéma pour les trajets par jour."""
    
    date: str
    count: int


class RevenueByDayResponse(BaseModel):
    """Schéma pour les revenus par jour."""
    
    date: str
    amount: int


class PaymentMethodsResponse(BaseModel):
    """Schéma pour les méthodes de paiement."""
    
    method: str
    count: int


class TopDriverResponse(BaseModel):
    """Schéma pour les top drivers."""
    
    id: str
    total_trips: int
    total_earnings: int
    rating: float


class IncidentsByTypeResponse(BaseModel):
    """Schéma pour les incidents par type."""
    
    type: str
    count: int


class MinistryReportRequest(BaseModel):
    """Schéma pour la demande de rapport ministère."""
    
    year: int = Field(..., description="Année", ge=2020, le=2100)
    month: int = Field(..., description="Mois", ge=1, le=12)


class MinistryReportResponse(BaseModel):
    """Schéma pour la réponse du rapport ministère."""
    
    period: str
    total_trips: int
    total_revenue_xaf: int
    total_incidents: int
    generated_at: str


class ExportCSVRequest(BaseModel):
    """Schéma pour l'export CSV."""
    
    start_date: str = Field(..., description="Date de début (ISO)")
    end_date: str = Field(..., description="Date de fin (ISO)")