# ============================================================
# Tests Auth Service
# Fichier : backend/tests/test_auth.py
# ============================================================

import pytest
from backend.services.auth_service import auth_service


class TestAuthService:
    """Tests pour le service d'authentification."""
    
    def test_hash_password(self):
        """Test le hachage d'un mot de passe."""
        password = "test_password_123"
        hashed = auth_service.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test la vérification avec le bon mot de passe."""
        password = "test_password_123"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test la vérification avec le mauvais mot de passe."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(wrong_password, hashed) is False
    
    def test_create_access_token(self):
        """Test la création d'un token d'accès."""
        token = auth_service.create_access_token(
            user_id="test_user_id",
            role="client"
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test la création d'un token de rafraîchissement."""
        token = auth_service.create_refresh_token(
            user_id="test_user_id"
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token_valid(self):
        """Test la vérification d'un token valide."""
        token = auth_service.create_access_token(
            user_id="test_user_id",
            role="client"
        )
        
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test_user_id"
        assert payload["role"] == "client"
        assert payload["type"] == "access"
    
    def test_verify_token_invalid(self):
        """Test la vérification d'un token invalide."""
        payload = auth_service.verify_token("invalid_token_string")
        
        assert payload is None
    
    def test_generate_totp_secret(self):
        """Test la génération d'un secret TOTP."""
        secret = auth_service.generate_totp_secret()
        
        assert secret is not None
        assert isinstance(secret, str)
        assert len(secret) > 0
    
    def test_get_totp_uri(self):
        """Test la génération de l'URI TOTP."""
        secret = auth_service.generate_totp_secret()
        uri = auth_service.get_totp_uri(secret, "test_user")
        
        assert uri is not None
        assert "otpauth://totp/" in uri
        assert "test_user" in uri
    
    def test_verify_totp_valid(self):
        """Test la vérification d'un code TOTP valide."""
        secret = auth_service.generate_totp_secret()
        import pyotp
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        assert auth_service.verify_totp(secret, code) is True
    
    def test_verify_totp_invalid(self):
        """Test la vérification d'un code TOTP invalide."""
        secret = auth_service.generate_totp_secret()
        
        assert auth_service.verify_totp(secret, "000000") is False
    
    def test_hash_biometric(self):
        """Test le hachage de données biométriques."""
        biometric = "fingerprint_data_12345"
        hashed = auth_service.hash_biometric(biometric)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA-256 hex length
    
    def test_verify_biometric_correct(self):
        """Test la vérification biométrique correcte."""
        biometric = "fingerprint_data_12345"
        hashed = auth_service.hash_biometric(biometric)
        
        assert auth_service.verify_biometric(biometric, hashed) is True
    
    def test_verify_biometric_incorrect(self):
        """Test la vérification biométrique incorrecte."""
        biometric = "fingerprint_data_12345"
        wrong_biometric = "wrong_fingerprint"
        hashed = auth_service.hash_biometric(biometric)
        
        assert auth_service.verify_biometric(wrong_biometric, hashed) is False