# ============================================================
# Service Géolocalisation MobiTranz
# Fichier : backend/services/geo_service.py
# Description : Géolocalisation, zones et calcul de tarifs
# ============================================================

import math
from typing import Optional, List, Tuple
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.zone import Zone


logger = structlog.get_logger()


class GeoService:
    """Service de géolocalisation MobiTranz.
    
    Gère les calculs de distance, détection de zones,
    et tarification basée sur la localisation.
    """
    
    EARTH_RADIUS_KM = 6371.0
    
    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calcule la distance entre deux points GPS avec la formule de Haversine.
        
        Args:
            lat1: Latitude du premier point
            lon1: Longitude du premier point
            lat2: Latitude du deuxième point
            lon2: Longitude du deuxième point
            
        Returns:
            float: Distance en kilomètres
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * \
            math.sin(delta_lon / 2) ** 2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = self.EARTH_RADIUS_KM * c
        
        return round(distance, 2)
    
    def calculate_eta(
        self,
        distance_km: float,
        average_speed_kmh: float = 30.0
    ) -> int:
        """Calcule le temps de trajet estimé en minutes.
        
        Args:
            distance_km: Distance en kilomètres
            average_speed_kmh: Vitesse moyenne en km/h (défaut: 30 km/h)
            
        Returns:
            int: Temps estimé en minutes
        """
        if average_speed_kmh <= 0:
            average_speed_kmh = 30.0
        
        hours = distance_km / average_speed_kmh
        minutes = int(hours * 60)
        
        return max(minutes, 1)
    
    def is_within_radius(
        self,
        center_lat: float,
        center_lon: float,
        point_lat: float,
        point_lon: float,
        radius_km: float
    ) -> bool:
        """Vérifie si un point est dans un rayon donné.
        
        Args:
            center_lat: Latitude du centre
            center_lon: Longitude du centre
            point_lat: Latitude du point à vérifier
            point_lon: Longitude du point à vérifier
            radius_km: Rayon en kilomètres
            
        Returns:
            bool: True si le point est dans le rayon
        """
        distance = self.calculate_distance(
            center_lat, center_lon,
            point_lat, point_lon
        )
        
        return distance <= radius_km
    
    async def detect_zone(
        self,
        db: AsyncSession,
        latitude: float,
        longitude: float
    ) -> Optional[Zone]:
        """Détecte la zone dans laquelle se trouve un point géographique.
        
        Args:
            db: Session de base de données
            latitude: Latitude du point
            longitude: Longitude du point
            
        Returns:
            Zone: Zone détectée ou None
        """
        result = await db.execute(select(Zone))
        zones = result.scalars().all()
        
        for zone in zones:
            if zone.polygon_coordinates:
                if self._is_point_in_polygon(
                    latitude, longitude,
                    zone.polygon_coordinates
                ):
                    return zone
        
        return None
    
    def _is_point_in_polygon(
        self,
        lat: float,
        lon: float,
        polygon: str
    ) -> bool:
        """Vérifie si un point est à l'intérieur d'un polygone.
        
        Args:
            lat: Latitude du point
            lon: Longitude du point
            polygon: Coordonnées du polygone au format "lat1,lon1;lat2,lon2;..."
            
        Returns:
            bool: True si le point est dans le polygone
        """
        try:
            points = []
            for coord in polygon.split(";"):
                lat_pt, lon_pt = coord.split(",")
                points.append((float(lat_pt), float(lon_pt)))
            
            if len(points) < 3:
                return False
            
            n = len(points)
            inside = False
            
            p1_lat, p1_lon = points[0]
            
            for i in range(1, n + 1):
                p2_lat, p2_lon = points[i % n]
                
                if lon > min(p1_lon, p2_lon):
                    if lon <= max(p1_lon, p2_lon):
                        if p1_lat != p2_lat:
                            lat_inters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                            if lat > lat_inters:
                                inside = not inside
                
                p1_lat, p1_lon = p2_lat, p2_lon
            
            return inside
            
        except Exception as e:
            logger.warning("Erreur détection zone", error=str(e))
            return False
    
    async def find_nearby_drivers(
        self,
        db: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        limit: int = 10
    ) -> List[dict]:
        """Trouve les drivers disponibles à proximité.
        
        Args:
            db: Session de base de données
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
            radius_km: Rayon de recherche en km
            limit: Nombre maximum de résultats
            
        Returns:
            list: Liste des drivers avec distance
        """
        from backend.models.driver import Driver, DriverStatus
        
        result = await db.execute(
            select(Driver).where(
                Driver.status == DriverStatus.VALIDATED,
                Driver.is_available == True,
                Driver.is_on_trip == False
            )
        )
        drivers = result.scalars().all()
        
        nearby_drivers = []
        
        for driver in drivers:
            if driver.current_lat and driver.current_lon:
                distance = self.calculate_distance(
                    latitude, longitude,
                    driver.current_lat, driver.current_lon
                )
                
                if distance <= radius_km:
                    nearby_drivers.append({
                        "driver_id": driver.id,
                        "distance_km": distance,
                        "latitude": driver.current_lat,
                        "longitude": driver.current_lon,
                        "rating": driver.rating,
                        "available_seats": 4
                    })
        
        nearby_drivers.sort(key=lambda x: x["distance_km"])
        
        return nearby_drivers[:limit]
    
    async def calculate_trip_fare(
        self,
        db: AsyncSession,
        distance_km: float,
        departure_zone_id: Optional[str] = None,
        arrival_zone_id: Optional[str] = None,
        hour: int = None
    ) -> dict:
        """Calcule le tarif d'un trajet selon la distance et les zones.
        
        Args:
            db: Session de base de données
            distance_km: Distance du trajet en km
            departure_zone_id: ID de la zone de départ
            arrival_zone_id: ID de la zone d'arrivée
            hour: Heure de départ (0-23) pour majorations
            
        Returns:
            dict: Calcul du tarif avec détails
        """
        if hour is None:
            hour = datetime.now().hour
        
        base_tariff_per_km = 100
        
        if departure_zone_id:
            result = await db.execute(
                select(Zone).where(Zone.id == departure_zone_id)
            )
            zone = result.scalar_one_or_none()
            
            if zone and zone.tariff_base:
                base_tariff_per_km = zone.tariff_base
        
        gross_amount = base_tariff_per_km * distance_km
        
        multiplier = 1.0
        
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            multiplier = 1.25
        elif hour >= 21 or hour <= 5:
            multiplier = 1.50
        
        final_amount = math.ceil(gross_amount * multiplier / 100) * 100
        
        return {
            "distance_km": distance_km,
            "base_rate_per_km": base_tariff_per_km,
            "gross_amount": int(gross_amount),
            "hour": hour,
            "multiplier": multiplier,
            "final_amount": int(final_amount),
            "currency": "FCFA"
        }
    
    def detect_route_deviation(
        self,
        route_points: List[Tuple[float, float]],
        current_lat: float,
        current_lon: float,
        tolerance_meters: float = 200.0
    ) -> bool:
        """Détecte si le véhicule s'écarte de l'itinéraire prévu.
        
        Args:
            route_points: Liste des points de l'itinéraire (lat, lon)
            current_lat: Position actuelle latitude
            current_lon: Position actuelle longitude
            tolerance_meters: Tolérance en mètres (défaut: 200m)
            
        Returns:
            bool: True si déviation détectée
        """
        if not route_points or len(route_points) < 2:
            return False
        
        min_distance = float('inf')
        
        for point in route_points:
            distance_m = self.calculate_distance(
                current_lat, current_lon,
                point[0], point[1]
            ) * 1000
            
            min_distance = min(min_distance, distance_m)
        
        return min_distance > tolerance_meters


from datetime import datetime

geo_service = GeoService()