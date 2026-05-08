import pytest
from unittest.mock import AsyncMock, MagicMock


class TestMatchingService:

    @pytest.mark.asyncio
    async def test_get_matching_score_no_location(self):
        from backend.services.matching_service import matching_service

        mock_driver = MagicMock()
        mock_driver.current_lat = None
        mock_driver.current_lon = None
        mock_driver.rating = 4.5
        mock_driver.total_trips = 100

        score = await matching_service.get_matching_score(mock_driver, 48.8566, 2.3522)
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_get_matching_score_with_vehicle(self):
        from backend.services.matching_service import matching_service

        mock_driver = MagicMock()
        mock_driver.current_lat = 48.8570
        mock_driver.current_lon = 2.3525
        mock_driver.rating = 5.0
        mock_driver.total_trips = 100

        mock_vehicle = MagicMock()
        mock_vehicle.available_seats = 4

        score = await matching_service.get_matching_score(
            mock_driver, 48.8566, 2.3522, mock_vehicle
        )
        assert score > 0
        assert score <= 100

    @pytest.mark.asyncio
    async def test_score_nearby_driver(self):
        from backend.services.matching_service import matching_service

        mock_driver = MagicMock()
        mock_driver.current_lat = 48.8568
        mock_driver.current_lon = 2.3523
        mock_driver.rating = 5.0
        mock_driver.total_trips = 100

        score = await matching_service.get_matching_score(mock_driver, 48.8566, 2.3522)
        assert score > 80

    @pytest.mark.asyncio
    async def test_score_far_driver(self):
        from backend.services.matching_service import matching_service

        mock_driver = MagicMock()
        mock_driver.current_lat = 49.0000
        mock_driver.current_lon = 3.0000
        mock_driver.rating = 5.0
        mock_driver.total_trips = 100

        score = await matching_service.get_matching_score(mock_driver, 48.8566, 2.3522)
        assert score < 50

    @pytest.mark.asyncio
    async def test_score_experienced_driver(self):
        from backend.services.matching_service import matching_service

        mock_driver = MagicMock()
        mock_driver.current_lat = 48.8570
        mock_driver.current_lon = 2.3525
        mock_driver.rating = 5.0
        mock_driver.total_trips = 200

        mock_vehicle = MagicMock()
        mock_vehicle.available_seats = 4

        score = await matching_service.get_matching_score(
            mock_driver, 48.8566, 2.3522, mock_vehicle
        )
        assert score > 70

    @pytest.mark.asyncio
    async def test_score_low_rating(self):
        from backend.services.matching_service import matching_service

        mock_driver = MagicMock()
        mock_driver.current_lat = 48.8570
        mock_driver.current_lon = 2.3525
        mock_driver.rating = 2.0
        mock_driver.total_trips = 10

        score = await matching_service.get_matching_score(mock_driver, 48.8566, 2.3522)
        assert score < 70
