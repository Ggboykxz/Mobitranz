import math
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestHaversineDistance:
    def setup_method(self):
        from backend.services.geo_service import geo_service

        self.service = geo_service

    def test_same_point(self):
        d = self.service.calculate_distance(48.8566, 2.3522, 48.8566, 2.3522)
        assert d == 0.0

    def test_known_distance_paris_to_lyon(self):
        d = self.service.calculate_distance(48.8566, 2.3522, 45.7573, 4.8344)
        assert 390 < d < 400

    def test_known_distance_libreville_to_port_gentil(self):
        d = self.service.calculate_distance(0.4163, 9.4673, -0.7191, 8.7817)
        assert 140 < d < 155

    def test_equator_points(self):
        d = self.service.calculate_distance(0.0, 0.0, 0.0, 1.0)
        assert 110 < d < 112

    def test_antipodal(self):
        d = self.service.calculate_distance(0.0, 0.0, 0.0, 180.0)
        assert 20000 < d < 20100

    def test_symmetric(self):
        d1 = self.service.calculate_distance(48.8566, 2.3522, 45.7573, 4.8344)
        d2 = self.service.calculate_distance(45.7573, 4.8344, 48.8566, 2.3522)
        assert d1 == d2

    def test_zero_coordinates(self):
        d = self.service.calculate_distance(0, 0, 0, 0)
        assert d == 0.0


class TestETA:
    def setup_method(self):
        from backend.services.geo_service import geo_service

        self.service = geo_service

    def test_eta_30km_30kmh(self):
        eta = self.service.calculate_eta(30.0, 30.0)
        assert eta == 60

    def test_eta_short_distance(self):
        eta = self.service.calculate_eta(0.5, 30.0)
        assert eta == 1

    def test_eta_zero_speed(self):
        eta = self.service.calculate_eta(30.0, 0)
        assert eta == 60

    def test_eta_negative_speed(self):
        eta = self.service.calculate_eta(30.0, -10)
        assert eta == 60

    def test_eta_fast_speed(self):
        eta = self.service.calculate_eta(60.0, 120.0)
        assert eta == 30

    def test_eta_minimum_one_minute(self):
        eta = self.service.calculate_eta(0.01, 100.0)
        assert eta == 1


class TestWithinRadius:
    def setup_method(self):
        from backend.services.geo_service import geo_service

        self.service = geo_service

    def test_within_radius_true(self):
        center = (48.8566, 2.3522)
        point = (48.8600, 2.3550)
        assert self.service.is_within_radius(*center, *point, 1.0) is True

    def test_within_radius_false(self):
        center = (48.8566, 2.3522)
        point = (49.0000, 2.5000)
        assert self.service.is_within_radius(*center, *point, 1.0) is False

    def test_exact_radius_boundary(self):
        center = (48.8566, 2.3522)
        point = (48.8570, 2.3525)
        assert self.service.is_within_radius(*center, *point, 0.2) is True
        assert self.service.is_within_radius(*center, *point, 0.01) is False


class TestPointInPolygon:
    def setup_method(self):
        from backend.services.geo_service import geo_service

        self.service = geo_service

    def test_invalid_polygon(self):
        assert self.service._is_point_in_polygon(0, 0, "invalid") is False

    def test_less_than_3_points(self):
        assert (
            self.service._is_point_in_polygon(0, 0, "0,0;1,1") is False
        )

    def test_point_inside_polygon(self):
        polygon = "0,0;3,0;1,2"
        assert self.service._is_point_in_polygon(1, 1, polygon) is True

    def test_point_outside_polygon(self):
        polygon = "0,0;3,0;1,2"
        inside = self.service._is_point_in_polygon(5, 5, polygon)
        assert inside is False


class TestRouteDeviation:
    def setup_method(self):
        from backend.services.geo_service import geo_service

        self.service = geo_service

    def test_empty_route(self):
        assert self.service.detect_route_deviation([], 48.857, 2.3525, 200) is False

    def test_single_point_route(self):
        assert (
            self.service.detect_route_deviation(
                [(48.8566, 2.3522)], 48.857, 2.3525, 200
            )
            is False
        )

    def test_on_route(self):
        route = [(48.8566, 2.3522), (48.8570, 2.3525), (48.8575, 2.3530)]
        assert (
            self.service.detect_route_deviation(route, 48.8570, 2.3525, 200)
            is False
        )

    def test_deviated(self):
        route = [(48.8566, 2.3522), (48.8570, 2.3525), (48.8575, 2.3530)]
        assert (
            self.service.detect_route_deviation(route, 49.0000, 3.0000, 200)
            is True
        )

    def test_tight_tolerance(self):
        route = [(48.8566, 2.3522), (48.8570, 2.3525)]
        assert (
            self.service.detect_route_deviation(route, 48.8566, 2.3522, 10)
            is False
        )


class TestTripFare:
    def setup_method(self):
        from backend.services.geo_service import geo_service

        self.service = geo_service

    async def test_base_fare_off_peak(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await self.service.calculate_trip_fare(
            mock_db, 10.0, hour=14
        )
        assert result["multiplier"] == 1.0
        assert result["distance_km"] == 10.0
        assert result["base_rate_per_km"] == 100
        assert result["gross_amount"] == 1000
        assert result["currency"] == "FCFA"

    async def test_fare_peak_morning(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        for hour in (7, 8, 9):
            result = await self.service.calculate_trip_fare(
                mock_db, 10.0, hour=hour
            )
            assert result["multiplier"] == 1.25

    async def test_fare_peak_evening(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        for hour in (17, 18, 19):
            result = await self.service.calculate_trip_fare(
                mock_db, 10.0, hour=hour
            )
            assert result["multiplier"] == 1.25

    async def test_fare_night(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        for hour in (21, 22, 23, 5, 4, 3):
            result = await self.service.calculate_trip_fare(
                mock_db, 10.0, hour=hour
            )
            assert result["multiplier"] == 1.50

    async def test_fare_rounding_to_100(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await self.service.calculate_trip_fare(
            mock_db, 1.5, hour=14
        )
        assert result["final_amount"] % 100 == 0

    async def test_fare_with_zone_multiplier_departure(self):
        mock_db = AsyncMock()
        mock_zone = MagicMock()
        mock_zone.base_price = 150
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_zone
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await self.service.calculate_trip_fare(
            mock_db, 10.0,
            departure_zone_id="zone-1",
            hour=14,
        )
        assert result["base_rate_per_km"] == 150
        assert result["gross_amount"] == 1500


class TestFindNearbyDrivers:
    async def test_find_nearby(self):
        from backend.services.geo_service import geo_service

        mock_driver = MagicMock()
        mock_driver.id = "driver-1"
        mock_driver.current_lat = 48.8575
        mock_driver.current_lon = 2.3530
        mock_driver.rating = 4.5

        mock_db = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_driver]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await geo_service.find_nearby_drivers(
            mock_db, 48.8566, 2.3522, radius_km=5.0
        )
        assert len(result) == 1
        assert result[0]["driver_id"] == "driver-1"
        assert result[0]["distance_km"] > 0
        assert result[0]["rating"] == 4.5

    async def test_find_nearby_outside_radius(self):
        from backend.services.geo_service import geo_service

        mock_driver = MagicMock()
        mock_driver.id = "driver-2"
        mock_driver.current_lat = 49.0000
        mock_driver.current_lon = 3.0000
        mock_driver.rating = 4.5

        mock_db = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_driver]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await geo_service.find_nearby_drivers(
            mock_db, 48.8566, 2.3522, radius_km=1.0
        )
        assert len(result) == 0

    async def test_find_nearby_no_location(self):
        from backend.services.geo_service import geo_service

        mock_driver = MagicMock()
        mock_driver.current_lat = None
        mock_driver.current_lon = None

        mock_db = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_driver]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await geo_service.find_nearby_drivers(
            mock_db, 48.8566, 2.3522
        )
        assert len(result) == 0

    async def test_find_nearby_sorted_by_distance(self):
        from backend.services.geo_service import geo_service

        driver1 = MagicMock()
        driver1.id = "near"
        driver1.current_lat = 48.8569
        driver1.current_lon = 2.3523
        driver1.rating = 4.0

        driver2 = MagicMock()
        driver2.id = "far"
        driver2.current_lat = 48.8600
        driver2.current_lon = 2.3600
        driver2.rating = 5.0

        mock_db = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [driver1, driver2]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await geo_service.find_nearby_drivers(
            mock_db, 48.8566, 2.3522, radius_km=2.0
        )
        assert result[0]["driver_id"] == "near"
        assert result[0]["distance_km"] < result[1]["distance_km"]


class TestDetectZone:
    async def test_detect_zone_found(self):
        from backend.services.geo_service import geo_service

        mock_zone = MagicMock()
        mock_zone.contains_point.return_value = True

        mock_db = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_zone]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await geo_service.detect_zone(mock_db, 48.8566, 2.3522)
        assert result is mock_zone
        mock_zone.contains_point.assert_called_once_with(48.8566, 2.3522)

    async def test_detect_zone_not_found(self):
        from backend.services.geo_service import geo_service

        mock_zone = MagicMock()
        mock_zone.contains_point.return_value = False

        mock_db = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_zone]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await geo_service.detect_zone(mock_db, 48.8566, 2.3522)
        assert result is None
