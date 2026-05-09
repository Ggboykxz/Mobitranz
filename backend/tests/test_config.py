# ============================================================
# Tests Configuration
# Fichier : backend/tests/test_config.py
# ============================================================

import pytest
from backend.config import Settings


class TestSettings:
    """Tests pour la configuration."""

    def test_default_values(self):
        """Test les valeurs par défaut."""
        settings = Settings()
        assert settings.app_name == "MobiTranz"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.tz == "Africa/Libreville"

    def test_jwt_config(self):
        """Test la configuration JWT."""
        settings = Settings()
        assert settings.access_token_expire_minutes == 15
        assert settings.refresh_token_expire_days == 7
        assert settings.jwt_algorithm == "HS256"

    def test_rate_limiting_config(self):
        """Test la configuration rate limiting."""
        settings = Settings()
        assert settings.rate_limit_auth_requests == 5
        assert settings.rate_limit_auth_window == 900
        assert settings.rate_limit_payment_requests == 10

    def test_database_defaults(self):
        """Test les valeurs par défaut de la base."""
        settings = Settings()
        assert "localhost" in settings.database_url
        assert "5432" in settings.database_url

    def test_redis_defaults(self):
        """Test les valeurs par défaut Redis."""
        settings = Settings()
        assert "redis" in settings.redis_url
        assert "6379" in settings.redis_url

    def test_tz_setting(self):
        """Test le fuseau horaire."""
        settings = Settings()
        assert settings.tz == "Africa/Libreville"