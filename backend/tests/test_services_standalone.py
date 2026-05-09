# ============================================================
# Tests Services - Sans Dépendance DB
# Fichier : backend/tests/test_services_standalone.py
# ============================================================

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys

# ============================================================
# Test Config Settings
# ============================================================
class TestConfigSettings:
    """Tests pour la configuration."""
    
    def test_app_name_default(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            from backend.config import settings
            assert settings.app_name == "MobiTranz"
    
    def test_app_version_default(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            from backend.config import settings
            assert settings.app_version == "1.0.0"
    
    def test_debug_default(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            from backend.config import settings
            assert settings.debug is False
    
    def test_jwt_algorithm(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            from backend.config import settings
            assert settings.jwt_algorithm == "HS256"
    
    def test_access_token_expire_minutes(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            from backend.config import settings
            assert settings.access_token_expire_minutes == 15
    
    def test_refresh_token_expire_days(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            from backend.config import settings
            assert settings.refresh_token_expire_days == 7
    
    def test_rate_limit_auth_requests(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            from backend.config import settings
            assert settings.rate_limit_auth_requests == 5
    
    def test_rate_limit_payment_requests(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            from backend.config import settings
            assert settings.rate_limit_payment_requests == 10
    
    def test_tz_default(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            from backend.config import settings
            assert settings.tz == "Africa/Libreville"


# ============================================================
# Test AuthService - Password
# ============================================================
class TestAuthServicePassword:
    """Tests pour AuthService - gestion des mots de passe."""
    
    def test_hash_password_length(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings') as mock_settings:
                mock_settings.secret_key = "test"
                mock_settings.jwt_algorithm = "HS256"
                mock_settings.access_token_expire_minutes = 15
                mock_settings.refresh_token_expire_days = 7
                
                from backend.services.auth_service import AuthService
                service = AuthService()
                hashed = service.hash_password("password123")
                assert len(hashed) > 50
    
    def test_verify_password_correct(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings') as mock_settings:
                mock_settings.secret_key = "test"
                mock_settings.jwt_algorithm = "HS256"
                mock_settings.access_token_expire_minutes = 15
                mock_settings.refresh_token_expire_days = 7
                
                from backend.services.auth_service import AuthService
                service = AuthService()
                hashed = service.hash_password("password123")
                assert service.verify_password("password123", hashed) is True
    
    def test_verify_password_incorrect(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings') as mock_settings:
                mock_settings.secret_key = "test"
                mock_settings.jwt_algorithm = "HS256"
                mock_settings.access_token_expire_minutes = 15
                mock_settings.refresh_token_expire_days = 7
                
                from backend.services.auth_service import AuthService
                service = AuthService()
                hashed = service.hash_password("password123")
                assert service.verify_password("wrongpassword", hashed) is False


# ============================================================
# Test AuthService - JWT
# ============================================================
class TestAuthServiceJWT:
    """Tests pour AuthService - JWT."""
    
    def test_create_access_token(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings') as mock_settings:
                mock_settings.secret_key = "test_secret_key_12345678901234567890"
                mock_settings.jwt_algorithm = "HS256"
                mock_settings.access_token_expire_minutes = 15
                mock_settings.refresh_token_expire_days = 7
                
                from backend.services.auth_service import AuthService
                service = AuthService()
                token = service.create_access_token("user123", "client")
                assert token is not None
                assert len(token) > 20
    
    def test_create_access_token_with_ip(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings') as mock_settings:
                mock_settings.secret_key = "test_secret_key_12345678901234567890"
                mock_settings.jwt_algorithm = "HS256"
                mock_settings.access_token_expire_minutes = 15
                mock_settings.refresh_token_expire_days = 7
                
                from backend.services.auth_service import AuthService
                service = AuthService()
                token = service.create_access_token("user123", "client", "192.168.1.1")
                assert token is not None
    
    def test_create_refresh_token(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings') as mock_settings:
                mock_settings.secret_key = "test_secret_key_12345678901234567890"
                mock_settings.jwt_algorithm = "HS256"
                mock_settings.access_token_expire_minutes = 15
                mock_settings.refresh_token_expire_days = 7
                
                from backend.services.auth_service import AuthService
                service = AuthService()
                token = service.create_refresh_token("user123")
                assert token is not None
                assert len(token) > 20
    
    def test_verify_token_valid(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings') as mock_settings:
                mock_settings.secret_key = "test_secret_key_12345678901234567890"
                mock_settings.jwt_algorithm = "HS256"
                mock_settings.access_token_expire_minutes = 15
                mock_settings.refresh_token_expire_days = 7
                
                from backend.services.auth_service import AuthService
                service = AuthService()
                token = service.create_access_token("user123", "client")
                payload = service.verify_token(token)
                assert payload is not None
                assert payload["sub"] == "user123"
                assert payload["role"] == "client"
    
    def test_verify_token_invalid(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings') as mock_settings:
                mock_settings.secret_key = "test_secret_key_12345678901234567890"
                mock_settings.jwt_algorithm = "HS256"
                mock_settings.access_token_expire_minutes = 15
                mock_settings.refresh_token_expire_days = 7
                
                from backend.services.auth_service import AuthService
                service = AuthService()
                payload = service.verify_token("invalid.token.here")
                assert payload is None


# ============================================================
# Test AuthService - TOTP
# ============================================================
class TestAuthServiceTOTP:
    """Tests pour AuthService - TOTP."""
    
    def test_generate_totp_secret(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings'):
                from backend.services.auth_service import AuthService
                service = AuthService()
                secret = service.generate_totp_secret()
                assert secret is not None
                assert len(secret) == 32
    
    def test_get_totp_uri(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings'):
                from backend.services.auth_service import AuthService
                service = AuthService()
                secret = service.generate_totp_secret()
                uri = service.get_totp_uri(secret, "+24106000000")
                assert uri.startswith("otpauth://totp/")
                assert "MobiTranz" in uri
    
    def test_verify_totp_valid(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings'):
                import pyotp
                from backend.services.auth_service import AuthService
                service = AuthService()
                secret = service.generate_totp_secret()
                totp = pyotp.TOTP(secret)
                code = totp.now()
                assert service.verify_totp(secret, code) is True
    
    def test_verify_totp_invalid(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings'):
                from backend.services.auth_service import AuthService
                service = AuthService()
                secret = service.generate_totp_secret()
                assert service.verify_totp(secret, "000000") is False


# ============================================================
# Test AuthService - Biométrie
# ============================================================
class TestAuthServiceBiometric:
    """Tests pour AuthService - biométrie."""
    
    def test_hash_biometric(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings'):
                from backend.services.auth_service import AuthService
                service = AuthService()
                hashed = service.hash_biometric("fingerprint_data")
                assert hashed is not None
                assert len(hashed) == 64
    
    def test_verify_biometric_success(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings'):
                from backend.services.auth_service import AuthService
                service = AuthService()
                hashed = service.hash_biometric("fingerprint_data")
                assert service.verify_biometric("fingerprint_data", hashed) is True
    
    def test_verify_biometric_failure(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings'):
                from backend.services.auth_service import AuthService
                service = AuthService()
                hashed = service.hash_biometric("fingerprint_data")
                assert service.verify_biometric("wrong_fingerprint", hashed) is False


# ============================================================
# Test AuthService - Reset Code
# ============================================================
class TestAuthServiceResetCode:
    """Tests pour AuthService - code de réinitialisation."""
    
    def test_generate_reset_code(self):
        with patch.dict('os.environ', {'SECRET_KEY': 'test'}):
            with patch('backend.services.auth_service.settings'):
                from backend.services.auth_service import AuthService
                service = AuthService()
                code = service.generate_reset_code()
                assert code is not None
                assert len(code) == 6
                assert code.isdigit()


# ============================================================
# Test Security Utils
# ============================================================
class TestSecurityUtils:
    """Tests pour les utilitaires de sécurité."""
    
    def test_generate_csrf_token(self):
        from backend.utils.security import generate_csrf_token
        token = generate_csrf_token()
        assert token is not None
        assert len(token) == 64
    
    def test_generate_api_key(self):
        from backend.utils.security import generate_api_key
        key = generate_api_key("test")
        assert key is not None
        assert key.startswith("test_")
    
    def test_hash_api_key(self):
        from backend.utils.security import hash_api_key, verify_api_key
        key = "test_key_123"
        hashed = hash_api_key(key)
        assert hashed is not None
        assert len(hashed) == 64
        assert verify_api_key(key, hashed) is True
    
    def test_verify_api_key_wrong(self):
        from backend.utils.security import hash_api_key, verify_api_key
        key = "test_key_123"
        hashed = hash_api_key(key)
        assert verify_api_key("wrong_key", hashed) is False
    
    def test_sanitize_input(self):
        from backend.utils.security import sanitize_input
        result = sanitize_input("  hello  ")
        assert result == "hello"
    
    def test_sanitize_input_max_length(self):
        from backend.utils.security import sanitize_input
        long_text = "a" * 2000
        result = sanitize_input(long_text, max_length=100)
        assert len(result) == 100
    
    def test_validate_phone_gabon_valid(self):
        from backend.utils.security import validate_phone_gabon
        assert validate_phone_gabon("+24106000000") is True
        assert validate_phone_gabon("24106000000") is True
    
    def test_validate_phone_gabon_invalid(self):
        from backend.utils.security import validate_phone_gabon
        assert validate_phone_gabon("invalid") is False
        assert validate_phone_gabon("+1234567890") is False
        assert validate_phone_gabon("06000000") is False
    
    def test_contains_sql_injection_true(self):
        from backend.utils.security import contains_sql_injection
        assert contains_sql_injection("DROP TABLE users") is True
        assert contains_sql_injection("DELETE FROM") is True
    
    def test_contains_sql_injection_false(self):
        from backend.utils.security import contains_sql_injection
        assert contains_sql_injection("Normal text") is False
        assert contains_sql_injection("SELECT") is False
    
    def test_detect_xss_true(self):
        from backend.utils.security import detect_xss
        assert detect_xss("<script>alert(1)</script>") is True
        assert detect_xss("javascript:alert(1)") is True
    
    def test_detect_xss_false(self):
        from backend.utils.security import detect_xss
        assert detect_xss("Normal text") is False
        assert detect_xss("Hello world") is False