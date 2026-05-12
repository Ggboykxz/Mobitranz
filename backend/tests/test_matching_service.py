from unittest.mock import AsyncMock, MagicMock

import pytest


class TestMatchingScore:
    def setup_method(self):
        from backend.services.matching_service import matching_service

        self.service = matching_service

    async def test_no_location_returns_zero(self):
        driver = MagicMock()
        driver.current_lat = None
        driver.current_lon = None
        driver.rating = 4.5
        driver.total_trips = 100

        score = await self.service.get_matching_score(
            driver, 48.8566, 2.3522
        )
        assert score == 0.0

    async def test_perfect_score_components(self):
        driver = MagicMock()
        driver.current_lat = 48.8566
        driver.current_lon = 2.3522
        driver.rating = 5.0
        driver.total_trips = 200

        vehicle = MagicMock()
        vehicle.available_seats = 4

        score = await self.service.get_matching_score(
            driver, 48.8566, 2.3522, vehicle
        )
        assert 80 <= score <= 85

    async def test_far_distance_lowers_score(self):
        driver = MagicMock()
        driver.current_lat = 49.0000
        driver.current_lon = 3.0000
        driver.rating = 5.0
        driver.total_trips = 200

        vehicle = MagicMock()
        vehicle.available_seats = 4

        score = await self.service.get_matching_score(
            driver, 48.8566, 2.3522, vehicle
        )
        assert score < 60

    async def test_low_rating_penalizes_score(self):
        driver = MagicMock()
        driver.current_lat = 48.8568
        driver.current_lon = 2.3523
        driver.rating = 2.0
        driver.total_trips = 10

        score = await self.service.get_matching_score(
            driver, 48.8566, 2.3522
        )
        assert score < 70

    async def test_high_experience_boosts_score(self):
        driver = MagicMock()
        driver.current_lat = 48.8570
        driver.current_lon = 2.3525
        driver.rating = 4.5
        driver.total_trips = 500

        vehicle = MagicMock()
        vehicle.available_seats = 4

        score = await self.service.get_matching_score(
            driver, 48.8566, 2.3522, vehicle
        )
        assert score > 70

    async def test_no_vehicle_defaults_4_seats(self):
        driver = MagicMock()
        driver.current_lat = 48.8566
        driver.current_lon = 2.3522
        driver.rating = 4.0
        driver.total_trips = 100

        score_no_vehicle = await self.service.get_matching_score(
            driver, 48.8566, 2.3522
        )
        score_with_4_seats = await self.service.get_matching_score(
            driver, 48.8566, 2.3522, MagicMock(available_seats=4)
        )
        assert score_no_vehicle == score_with_4_seats


class TestFindAvailableTaxis:
    async def test_find_available(self):
        from backend.services.matching_service import matching_service

        mock_user = MagicMock()
        mock_user.first_name = "Jean"
        mock_user.last_name = "Mba"
        mock_user.phone = "+24106000001"

        mock_driver = MagicMock()
        mock_driver.id = "driver-1"
        mock_driver.current_lat = 48.8570
        mock_driver.current_lon = 2.3525
        mock_driver.rating = 4.5
        mock_driver.total_trips = 100
        mock_driver.user = mock_user
        mock_driver.vehicle_id = "vehicle-1"

        mock_db = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_driver]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await matching_service.find_available_taxis(
            mock_db, 48.8566, 2.3522, radius_km=5.0
        )
        assert len(result) == 1
        assert result[0]["driver_id"] == "driver-1"
        assert result[0]["driver_name"] == "Jean Mba"

    async def test_no_drivers_available(self):
        from backend.services.matching_service import matching_service

        mock_db = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await matching_service.find_available_taxis(
            mock_db, 48.8566, 2.3522
        )
        assert len(result) == 0


class TestCreateProposal:
    async def test_create_proposal(self):
        from backend.services.matching_service import matching_service

        mock_db = AsyncMock()
        mock_fare_result = AsyncMock()
        mock_fare_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_fare_result

        mock_proposal = MagicMock()
        mock_proposal.id = "proposal-1"
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        def refresh_side_effect(instance):
            instance.id = "proposal-1"
            return None

        mock_db.refresh = AsyncMock(side_effect=refresh_side_effect)

        result = await matching_service.create_proposal(
            db=mock_db,
            driver_id="driver-1",
            client_id="client-1",
            pickup_lat=48.8566,
            pickup_lon=2.3522,
            dest_lat=48.8600,
            dest_lon=2.3550,
            dest_label="Centre-ville",
        )
        assert result["proposal_id"] is not None
        assert result["amount"] > 0
        assert result["distance_km"] > 0
        assert result["eta_minutes"] >= 1


class TestCalculateEstimatedFare:
    async def test_calculate_fare(self):
        from backend.services.matching_service import matching_service

        mock_driver = MagicMock()
        mock_driver.current_lat = 48.8566
        mock_driver.current_lon = 2.3522

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_driver
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await matching_service.calculate_estimated_fare(
            mock_db, "driver-1", 48.8600, 2.3550
        )
        assert result["distance_km"] > 0
        assert result["gross_amount"] > 0
        assert result["pickup_distance_km"] > 0
        assert result["currency"] == "FCFA"

    async def test_calculate_fare_driver_not_found(self):
        from backend.services.matching_service import matching_service

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await matching_service.calculate_estimated_fare(
            mock_db, "nonexistent", 48.8600, 2.3550
        )
        assert "error" in result
