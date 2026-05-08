import pytest
from fastapi.testclient import TestClient


class TestRouterImports:

    def test_auth_router_import(self):
        from backend.routers.auth import router

        assert router is not None

    def test_users_router_import(self):
        from backend.routers.users import router

        assert router is not None

    def test_drivers_router_import(self):
        from backend.routers.drivers import router

        assert router is not None

    def test_vehicles_router_import(self):
        from backend.routers.vehicles import router

        assert router is not None

    def test_trips_router_import(self):
        from backend.routers.trips import router

        assert router is not None

    def test_payments_router_import(self):
        from backend.routers.payments import router

        assert router is not None

    def test_incidents_router_import(self):
        from backend.routers.incidents import router

        assert router is not None

    def test_analytics_router_import(self):
        from backend.routers.analytics import router

        assert router is not None

    def test_admin_router_import(self):
        from backend.routers.admin import router

        assert router is not None

    def test_voice_router_import(self):
        from backend.routers.voice import router

        assert router is not None


class TestRouterPrefixes:

    def test_auth_router_prefix(self):
        from backend.routers.auth import router

        assert router.prefix == "/auth"

    def test_users_router_prefix(self):
        from backend.routers.users import router

        assert router.prefix == "/users"

    def test_drivers_router_prefix(self):
        from backend.routers.drivers import router

        assert router.prefix == "/drivers"

    def test_vehicles_router_prefix(self):
        from backend.routers.vehicles import router

        assert router.prefix == "/vehicles"

    def test_trips_router_prefix(self):
        from backend.routers.trips import router

        assert router.prefix == "/trips"

    def test_payments_router_prefix(self):
        from backend.routers.payments import router

        assert router.prefix == "/payments"

    def test_incidents_router_prefix(self):
        from backend.routers.incidents import router

        assert router.prefix == "/incidents"

    def test_analytics_router_prefix(self):
        from backend.routers.analytics import router

        assert router.prefix == "/analytics"

    def test_admin_router_prefix(self):
        from backend.routers.admin import router

        assert router.prefix == "/admin"

    def test_voice_router_prefix(self):
        from backend.routers.voice import router

        assert router.prefix == "/voice"


class TestRouterTags:

    def test_auth_router_tags(self):
        from backend.routers.auth import router

        assert "Authentication" in router.tags

    def test_users_router_tags(self):
        from backend.routers.users import router

        assert "Users" in router.tags

    def test_drivers_router_tags(self):
        from backend.routers.drivers import router

        assert "Drivers" in router.tags

    def test_vehicles_router_tags(self):
        from backend.routers.vehicles import router

        assert "Vehicles" in router.tags

    def test_trips_router_tags(self):
        from backend.routers.trips import router

        assert "Trips" in router.tags

    def test_payments_router_tags(self):
        from backend.routers.payments import router

        assert "Payments" in router.tags

    def test_incidents_router_tags(self):
        from backend.routers.incidents import router

        assert "Incidents" in router.tags

    def test_analytics_router_tags(self):
        from backend.routers.analytics import router

        assert "Analytics" in router.tags

    def test_admin_router_tags(self):
        from backend.routers.admin import router

        assert "Admin" in router.tags

    def test_voice_router_tags(self):
        from backend.routers.voice import router

        assert "Voice" in router.tags or "Voice AI" in router.tags


class TestRouterRoutes:

    def test_auth_routes_count(self):
        from backend.routers.auth import router

        routes = [r.path for r in router.routes]
        assert len(routes) >= 5

    def test_users_routes_count(self):
        from backend.routers.users import router

        routes = [r.path for r in router.routes]
        assert len(routes) >= 3

    def test_drivers_routes_count(self):
        from backend.routers.drivers import router

        routes = [r.path for r in router.routes]
        assert len(routes) >= 3

    def test_vehicles_routes_count(self):
        from backend.routers.vehicles import router

        routes = [r.path for r in router.routes]
        assert len(routes) >= 3

    def test_trips_routes_count(self):
        from backend.routers.trips import router

        routes = [r.path for r in router.routes]
        assert len(routes) >= 3

    def test_payments_routes_count(self):
        from backend.routers.payments import router

        routes = [r.path for r in router.routes]
        assert len(routes) >= 3

    def test_incidents_routes_count(self):
        from backend.routers.incidents import router

        routes = [r.path for r in router.routes]
        assert len(routes) >= 2

    def test_analytics_routes_count(self):
        from backend.routers.analytics import router

        routes = [r.path for r in router.routes]
        assert len(routes) >= 3

    def test_admin_routes_count(self):
        from backend.routers.admin import router

        routes = [r.path for r in router.routes]
        assert len(routes) >= 10


class TestMainApp:

    def test_main_app_import(self):
        from backend.main import app

        assert app is not None

    def test_app_title(self):
        from backend.main import app

        assert app.title is not None

    def test_app_routes_count(self):
        from backend.main import app

        routes = [r.path for r in app.routes]
        assert len(routes) >= 50

    def test_app_has_health_endpoint(self):
        from backend.main import app

        routes = [r.path for r in app.routes]
        assert any("/health" in r for r in routes)

    def test_app_has_docs(self):
        from backend.main import app

        assert app.docs_url is not None

    def test_app_has_openapi(self):
        from backend.main import app

        assert app.openapi_url is not None
