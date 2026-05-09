# ============================================================
# Tests Auth Service
# Fichier : backend/tests/test_auth_service.py
# ============================================================

import pytest
from backend.services.auth_service import AuthService


class TestAuthService:
    """Tests pour le service d'authentification."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.auth_service = AuthService()

    def test_hash_password(self):
        """Test le hachage du mot de passe."""
        password = "testpassword123"
        hashed = self.auth_service.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 50

    def test_verify_password_success(self):
        """Test vérification mot de passe correct."""
        password = "testpassword123"
        hashed = self.auth_service.hash_password(password)
        
        assert self.auth_service.verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test vérification mot de passe incorrect."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = self.auth_service.hash_password(password)
        
        assert self.auth_service.verify_password(wrong_password, hashed) is False

    def test_create_access_token(self):
        """Test création token d'accès."""
        token = self.auth_service.create_access_token(
            user_id="user123",
            role="client"
        )
        
        assert token is not None
        assert len(token) > 20
        assert "." in token

    def test_create_access_token_with_ip(self):
        """Test création token avec IP."""
        token = self.auth_service.create_access_token(
            user_id="user123",
            role="client",
            ip_address="192.168.1.1"
        )
        
        assert token is not None

    def test_create_refresh_token(self):
        """Test création token de rafraîchissement."""
        token = self.auth_service.create_refresh_token(user_id="user123")
        
        assert token is not None
        assert len(token) > 20
        assert "." in token

    def test_verify_token_valid(self):
        """Test vérification token valide."""
        token = self.auth_service.create_access_token(
            user_id="user123",
            role="client"
        )
        
        payload = self.auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["role"] == "client"

    def test_verify_token_invalid(self):
        """Test vérification token invalide."""
        payload = self.auth_service.verify_token("invalid.token.here")
        
        assert payload is None

    def test_generate_totp_secret(self):
        """Test génération secret TOTP."""
        secret = self.auth_service.generate_totp_secret()
        
        assert secret is not None
        assert len(secret) == 32

    def test_get_totp_uri(self):
        """Test génération URI TOTP."""
        secret = self.auth_service.generate_totp_secret()
        uri = self.auth_service.get_totp_uri(secret, "+24106000000")
        
        assert uri.startswith("otpauth://totp/")
        assert "MobiTranz" in uri
        assert secret in uri

    def test_verify_totp_valid(self):
        """Test vérification TOTP valide."""
        secret = self.auth_service.generate_totp_secret()
        totp = __import__("pyotp").TOTP(secret)
        code = totp.now()
        
        assert self.auth_service.verify_totp(secret, code) is True

    def test_verify_totp_invalid(self):
        """Test vérification TOTP invalide."""
        secret = self.auth_service.generate_totp_secret()
        
        assert self.auth_service.verify_totp(secret, "000000") is False

    def test_hash_biometric(self):
        """Test hachage biométrie."""
        biometric = "fingerprint_data_123"
        hashed = self.auth_service.hash_biometric(biometric)
        
        assert hashed is not None
        assert len(hashed) == 64

    def test_verify_biometric_success(self):
        """Test vérification biométrie."""
        biometric = "fingerprint_data_123"
        hashed = self.auth_service.hash_biometric(biometric)
        
        assert self.auth_service.verify_biometric(biometric, hashed) is True

    def test_verify_biometric_failure(self):
        """Test vérification biométrie échouée."""
        biometric = "fingerprint_data_123"
        wrong_biometric = "wrong_fingerprint"
        hashed = self.auth_service.hash_biometric(biometric)
        
        assert self.auth_service.verify_biometric(wrong_biometric, hashed) is False