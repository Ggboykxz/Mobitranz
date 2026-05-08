import pytest


class TestRouterEndpointsStructure:

    def test_auth_login_endpoint_exists(self):
        from backend.routers.auth import router

        routes = [r.path for r in router.routes]
        assert any("login" in r for r in routes)

    def test_auth_register_endpoint_exists(self):
        from backend.routers.auth import router

        routes = [r.path for r in router.routes]
        assert any("register" in r for r in routes)

    def test_users_list_endpoint_exists(self):
        from backend.routers.users import router

        routes = [r.path for r in router.routes]
        assert len(routes) > 0

    def test_drivers_list_endpoint_exists(self):
        from backend.routers.drivers import router

        routes = [r.path for r in router.routes]
        assert "drivers" in str(routes)

    def test_vehicles_list_endpoint_exists(self):
        from backend.routers.vehicles import router

        routes = [r.path for r in router.routes]
        assert "vehicles" in str(routes)

    def test_trips_list_endpoint_exists(self):
        from backend.routers.trips import router

        routes = [r.path for r in router.routes]
        assert "trips" in str(routes)

    def test_payments_list_endpoint_exists(self):
        from backend.routers.payments import router

        routes = [r.path for r in router.routes]
        assert "payments" in str(routes)

    def test_incidents_list_endpoint_exists(self):
        from backend.routers.incidents import router

        routes = [r.path for r in router.routes]
        assert "incidents" in str(routes)

    def test_analytics_dashboard_endpoint_exists(self):
        from backend.routers.analytics import router

        routes = [r.path for r in router.routes]
        assert len(routes) > 0

    def test_admin_dashboard_endpoint_exists(self):
        from backend.routers.admin import router

        routes = [r.path for r in router.routes]
        assert any("dashboard" in r or "kpi" in r for r in routes)


class TestDependenciesImports:

    def test_auth_deps_import(self):
        from backend.deps import auth_deps

        assert auth_deps is not None

    def test_database_import(self):
        from backend import database

        assert hasattr(database, "get_db")
        assert hasattr(database, "Base")

    def test_schemas_import(self):
        from backend import schemas

        assert schemas is not None

    def test_config_import(self):
        from backend import config

        assert config is not None


class TestModelEnums:

    def test_user_role_enum(self):
        from backend.models.user import UserRole

        assert UserRole.CLIENT.value == "client"
        assert UserRole.DRIVER.value == "driver"
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MINISTRY.value == "ministry"

    def test_user_status_enum(self):
        from backend.models.user import UserStatus

        assert UserStatus.PENDING.value == "pending"
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.SUSPENDED.value == "suspended"

    def test_driver_status_enum(self):
        from backend.models.driver import DriverStatus

        assert DriverStatus.PENDING.value == "pending"
        assert DriverStatus.VALIDATED.value == "validated"
        assert DriverStatus.SUSPENDED.value == "suspended"

    def test_trip_status_enum(self):
        from backend.models.trip import TripStatus

        assert TripStatus.PROPOSING.value == "proposing"
        assert TripStatus.HORN_PENDING.value == "horn_pending"
        assert TripStatus.PAYMENT_PENDING.value == "payment_pending"
        assert TripStatus.ACTIVE.value == "active"
        assert TripStatus.COMPLETED.value == "completed"
        assert TripStatus.CANCELLED.value == "cancelled"

    def test_payment_status_enum(self):
        from backend.models.payment import PaymentStatus

        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.PROCESSING.value == "processing"
        assert PaymentStatus.COMPLETED.value == "completed"
        assert PaymentStatus.FAILED.value == "failed"

    def test_incident_status_enum(self):
        from backend.models.incident import IncidentStatus

        assert IncidentStatus.PENDING.value == "pending"
        assert IncidentStatus.ACKNOWLEDGED.value == "acknowledged"
        assert IncidentStatus.ESCALATED.value == "escalated"
        assert IncidentStatus.RESOLVED.value == "resolved"
        assert IncidentStatus.CLOSED.value == "closed"
