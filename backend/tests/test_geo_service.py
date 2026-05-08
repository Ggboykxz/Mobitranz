import pytest
import math
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


class TestGeoService:

    def test_calculate_distance_same_point(self):
        from backend.services.geo_service import geo_service

        distance = geo_service.calculate_distance(48.8566, 2.3522, 48.8566, 2.3522)
        assert distance == 0.0

    def test_calculate_distance_zero_coords(self):
        from backend.services.geo_service import geo_service

        distance = geo_service.calculate_distance(0, 0, 0, 0)
        assert distance == 0.0

    def test_calculate_eta_normal(self):
        from backend.services.geo_service import geo_service

        eta = geo_service.calculate_eta(30.0, 30.0)
        assert eta == 60

    def test_calculate_eta_zero_speed(self):
        from backend.services.geo_service import geo_service

        eta = geo_service.calculate_eta(30.0, 0)
        assert eta == 60

    def test_calculate_eta_negative_speed(self):
        from backend.services.geo_service import geo_service

        eta = geo_service.calculate_eta(30.0, -10)
        assert eta == 60

    def test_calculate_eta_short_distance(self):
        from backend.services.geo_service import geo_service

        eta = geo_service.calculate_eta(0.1, 30.0)
        assert eta == 1

    def test_is_within_radius_true(self):
        from backend.services.geo_service import geo_service

        center_lat, center_lon = 48.8566, 2.3522
        point_lat, point_lon = 48.8600, 2.3550
        within = geo_service.is_within_radius(
            center_lat, center_lon, point_lat, point_lon, 1.0
        )
        assert within is True

    def test_is_within_radius_false(self):
        from backend.services.geo_service import geo_service

        center_lat, center_lon = 48.8566, 2.3522
        point_lat, point_lon = 49.0000, 2.5000
        within = geo_service.is_within_radius(
            center_lat, center_lon, point_lat, point_lon, 1.0
        )
        assert within is False

    def test_is_point_in_polygon_invalid(self):
        from backend.services.geo_service import geo_service

        polygon = "invalid"
        inside = geo_service._is_point_in_polygon(0.5, 0.5, polygon)
        assert inside is False

    def test_detect_route_deviation_empty_route(self):
        from backend.services.geo_service import geo_service

        deviation = geo_service.detect_route_deviation([], 48.8570, 2.3525, 200)
        assert deviation is False

    def test_detect_route_deviation_single_point(self):
        from backend.services.geo_service import geo_service

        deviation = geo_service.detect_route_deviation(
            [(48.8566, 2.3522)], 48.8570, 2.3525, 200
        )
        assert deviation is False

    def test_detect_route_deviation_with_deviation(self):
        from backend.services.geo_service import geo_service

        route = [(48.8566, 2.3522), (48.8570, 2.3525), (48.8575, 2.3530)]
        deviation = geo_service.detect_route_deviation(route, 49.0000, 3.0000, 200)
        assert deviation is True

    def test_detect_route_deviation_no_deviation(self):
        from backend.services.geo_service import geo_service

        route = [(48.8566, 2.3522), (48.8570, 2.3525), (48.8575, 2.3530)]
        deviation = geo_service.detect_route_deviation(route, 48.8570, 2.3525, 200)
        assert deviation is False


class TestGeoServiceAsync:

    @pytest.mark.asyncio
    async def test_calculate_trip_fare_peak_hours(self):
        from backend.services.geo_service import geo_service

        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with patch("backend.services.geo_service.datetime") as mock_dt:
            mock_dt.now.return_value.hour = 8
            result = await geo_service.calculate_trip_fare(mock_db, 10.0)

        assert result["multiplier"] == 1.25

    @pytest.mark.asyncio
    async def test_calculate_trip_fare_night(self):
        from backend.services.geo_service import geo_service

        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with patch("backend.services.geo_service.datetime") as mock_dt:
            mock_dt.now.return_value.hour = 22
            result = await geo_service.calculate_trip_fare(mock_db, 10.0)

        assert result["multiplier"] == 1.50

    @pytest.mark.asyncio
    async def test_calculate_trip_fare_off_peak(self):
        from backend.services.geo_service import geo_service

        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with patch("backend.services.geo_service.datetime") as mock_dt:
            mock_dt.now.return_value.hour = 14
            result = await geo_service.calculate_trip_fare(mock_db, 10.0)

        assert result["multiplier"] == 1.0

    @pytest.mark.asyncio
    async def test_calculate_trip_fare_weekend_night(self):
        from backend.services.geo_service import geo_service

        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with patch("backend.services.geo_service.datetime") as mock_dt:
            mock_dt.now.return_value.hour = 3
            result = await geo_service.calculate_trip_fare(mock_db, 10.0)

        assert result["multiplier"] == 1.50
