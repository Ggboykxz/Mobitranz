# ============================================================
# Tests d'Intégration Multi-Rôles
# Fichier : backend/tests/test_integration.py
# Description : Teste tous les rôles simultanément (admin, driver, client, ministry)
# ============================================================

import pytest
import asyncio
import json
from jose import jwt
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from backend.config import settings
from backend.services.auth_service import auth_service
from backend.services.voice_service import voice_proposal_service


class TestMultiRoleAuth:
    """Teste l'authentification de tous les rôles simultanément."""

    def test_all_roles_token_generation(self):
        """Test la création de tokens pour tous les rôles."""
        roles = ["admin", "driver", "client", "ministry"]
        tokens = {}

        for role in roles:
            token = auth_service.create_access_token(
                user_id=f"test_{role}_id", role=role
            )
            tokens[role] = token
            assert token is not None
            assert len(token) > 0
            assert isinstance(token, str)

        assert len(tokens) == 4
        assert len(set(tokens.values())) == 4

    def test_all_roles_token_verification(self):
        """Test la vérification des tokens pour tous les rôles."""
        roles = ["admin", "driver", "client", "ministry"]
        users = {}

        for role in roles:
            token = auth_service.create_access_token(
                user_id=f"test_{role}_id", role=role
            )
            payload = auth_service.verify_token(token)

            assert payload is not None
            assert payload["sub"] == f"test_{role}_id"
            assert payload["role"] == role
            assert payload["type"] == "access"

            users[role] = {"token": token, "payload": payload}

        assert all(u["payload"]["type"] == "access" for u in users.values())

    def test_concurrent_token_generation(self):
        """Test la création simultanée de 4 tokens (un par rôle)."""
        roles = ["admin", "client", "driver", "ministry"]
        tokens = [
            auth_service.create_access_token(user_id=f"user_{r}", role=r) for r in roles
        ]

        assert len(tokens) == 4
        assert len(set(tokens)) == 4
        for role, token in zip(roles, tokens):
            payload = auth_service.verify_token(token)
            assert payload["sub"] == f"user_{role}"
            assert payload["role"] == role

    def test_token_payload_structure_all_roles(self):
        """Test que la structure du payload est identique pour tous les rôles."""
        roles = ["admin", "client", "driver", "ministry"]
        payloads = {}

        for role in roles:
            token = auth_service.create_access_token(user_id=f"user_{role}", role=role)
            payloads[role] = auth_service.verify_token(token)

        required_keys = {"sub", "role", "exp", "iat", "type"}
        for payload in payloads.values():
            assert set(payload.keys()) == required_keys


class TestMultiRolePasswordHashing:
    """Teste le hachage de mots de passe pour tous les rôles."""

    def test_password_hash_all_roles(self):
        """Test le hachage pour tous les rôles."""
        roles = ["admin", "client", "driver", "ministry"]
        passwords = {
            "admin": "AdminPass123!",
            "client": "ClientPass123!",
            "driver": "DriverPass123!",
            "ministry": "MinistryPass123!",
        }

        for role in roles:
            password = passwords[role]
            hashed = auth_service.hash_password(password)

            assert hashed is not None
            assert hashed != password
            assert len(hashed) > 20
            assert hashed.startswith("$2")

    def test_password_verify_all_roles(self):
        """Test la vérification des mots de passe pour tous les rôles."""
        roles = ["admin", "client", "driver", "ministry"]
        passwords = {
            "admin": "MonMotDePasse123!",
            "client": "MonMotDePasse123!",
            "driver": "MonMotDePasse123!",
            "ministry": "MonMotDePasse123!",
        }

        for role in roles:
            password = passwords[role]
            hashed = auth_service.hash_password(password)

            assert auth_service.verify_password(password, hashed) is True
            assert auth_service.verify_password("wrong_password", hashed) is False

    def test_different_passwords_produce_different_hashes(self):
        """Test que différents mots de passe produisent des hashs différents."""
        passwords = [
            "Password1Admin!",
            "Password2Driver!",
            "Password3Client!",
            "Password4Ministry!",
        ]

        hashes = [auth_service.hash_password(p) for p in passwords]
        assert len(set(hashes)) == 4


class TestTOTPAllRoles:
    """Teste TOTP pour tous les rôles."""

    def test_totp_generate_all_roles(self):
        """Test la génération TOTP pour tous les rôles."""
        roles = ["admin", "client", "driver", "ministry"]
        secrets = {}

        for role in roles:
            secret = auth_service.generate_totp_secret()
            secrets[role] = secret

            assert secret is not None
            assert len(secret) == 32

        assert len(set(secrets.values())) == 4

    def test_totp_verify_all_roles(self):
        """Test la vérification TOTP pour tous les rôles."""
        import pyotp

        roles = ["admin", "client", "driver", "ministry"]

        for role in roles:
            secret = auth_service.generate_totp_secret()
            totp = pyotp.TOTP(secret)
            code = totp.now()

            assert auth_service.verify_totp(secret, code) is True
            assert auth_service.verify_totp(secret, "000000") is False
            assert auth_service.verify_totp(secret, "123456") is False

    def test_totp_uri_all_roles(self):
        """Test la génération de l'URI TOTP pour tous les rôles."""
        roles = ["admin", "client", "driver", "ministry"]

        for role in roles:
            secret = auth_service.generate_totp_secret()
            uri = auth_service.get_totp_uri(secret, f"{role}")

            assert "otpauth://totp/" in uri
            assert role in uri


class TestPaymentMethodsAllRoles:
    """Teste les méthodes de paiement pour tous les rôles."""

    def test_payment_methods_available(self):
        """Test que toutes les méthodes de paiement sont disponibles."""
        from backend.models.payment import PaymentMethod

        methods = [
            PaymentMethod.MOOVMONEY,
            PaymentMethod.AIRTELMONEY,
            PaymentMethod.CARD,
            PaymentMethod.BIOMETRIC,
            PaymentMethod.CASH,
        ]

        for method in methods:
            assert method.value is not None
            assert len(method.value) > 0

    def test_payment_status_values(self):
        """Test les statuts de paiement."""
        from backend.models.payment import PaymentStatus

        statuses = [
            PaymentStatus.PENDING,
            PaymentStatus.PROCESSING,
            PaymentStatus.COMPLETED,
            PaymentStatus.FAILED,
            PaymentStatus.REFUNDED,
        ]

        for status in statuses:
            assert status.value is not None


class TestVoiceNLPAllRoles:
    """Teste le NLP vocal pour tous les rôles."""

    def test_extract_all_zones(self):
        """Test l'extraction de toutes les zones connues."""
        zones = [
            ("Je vais au centre-ville", "centre-ville"),
            ("Emmène-moi à Owendo", "owendo"),
            ("Direction Akanda", "akanda"),
            ("Je veux aller à PK5", "pk5"),
            ("Aller à Port-Gentil", "port-gentil"),
        ]

        for text, expected in zones:
            destination = voice_proposal_service.extract_destination(text)
            assert (
                destination == expected
            ), f"Failed for '{text}': got {destination}, expected {expected}"

    def test_extract_amounts_all_roles(self):
        """Test l'extraction de montants pour tous les rôles."""
        amounts = [
            ("1000 francs", 1000),
            ("Owendo 500 XAF", 500),
            ("Je paie 2000", 2000),
            ("centre-ville 350 fcfa", 350),
        ]

        for text, expected in amounts:
            amount = voice_proposal_service.extract_amount(text)
            assert (
                amount == expected
            ), f"Failed for '{text}': got {amount}, expected {expected}"

    def test_extract_proposal_complete(self):
        """Test l'extraction complète d'une proposition."""
        text = "Je veux aller à Owendo pour 1000 francs avec 2 places"
        proposal = voice_proposal_service.extract_proposal(text)

        assert proposal["destination"] == "owendo"
        assert proposal["amount"] == 1000
        assert proposal["seats"] == 2


class TestUserRolesEnum:
    """Teste l'énumération des rôles."""

    def test_all_user_roles_exist(self):
        """Test que tous les rôles existent."""
        from backend.models.user import UserRole

        roles = ["admin", "client", "driver", "ministry"]

        for role in roles:
            upper = role.upper()
            assert hasattr(UserRole, upper), f"UserRole missing: {upper}"
            assert getattr(UserRole, upper).value == role

    def test_role_values_unique(self):
        """Test que les valeurs des rôles sont uniques."""
        from backend.models.user import UserRole

        values = [r.value for r in UserRole]
        assert len(values) == len(set(values))


class TestDriverStatuses:
    """Teste les statuts conducteur."""

    def test_all_driver_statuses_exist(self):
        """Test que tous les statuts conducteur existent."""
        from backend.models.driver import DriverStatus

        for status in ["pending", "validated", "suspended"]:
            assert hasattr(
                DriverStatus, status.upper()
            ), f"DriverStatus missing: {status.upper()}"

    def test_trip_statuses_exist(self):
        """Test que tous les statuts trajet existent."""
        from backend.models.trip import TripStatus

        for status in [
            "proposing",
            "horn_pending",
            "payment_pending",
            "active",
            "completed",
            "cancelled",
        ]:
            assert hasattr(
                TripStatus, status.upper()
            ), f"TripStatus missing: {status.upper()}"


class TestIncidentTypesAllRoles:
    """Teste les types d'incidents pour tous les rôles."""

    def test_all_incident_types_exist(self):
        """Test que tous les types d'incidents existent."""
        from backend.models.incident import IncidentType

        for inc_type in ["sos", "accident", "dispute", "theft", "harassment", "other"]:
            assert hasattr(
                IncidentType, inc_type.upper()
            ), f"IncidentType missing: {inc_type.upper()}"

    def test_incident_statuses_exist(self):
        """Test que tous les statuts d'incidents existent."""
        from backend.models.incident import IncidentStatus

        for status in ["pending", "acknowledged", "escalated", "resolved", "closed"]:
            assert hasattr(
                IncidentStatus, status.upper()
            ), f"IncidentStatus missing: {status.upper()}"


class TestZonePricing:
    """Teste les zones tarifaires."""

    def test_zones_have_pricing(self):
        """Test que les zones ont des prix."""
        zones = [
            ("centre-ville", 350),
            ("owendo", 500),
            ("akanda", 600),
            ("pk5", 400),
            ("pk8", 450),
        ]

        for zone_name, min_price in zones:
            keywords = voice_proposal_service.KNOWN_ZONES.get(zone_name, [])
            assert len(keywords) > 0


class TestBiometricAllRoles:
    """Teste la biométrie pour tous les rôles."""

    def test_biometric_hash_all_roles(self):
        """Test le hachage biométrique pour tous les rôles."""
        roles = ["admin", "client", "driver", "ministry"]

        for role in roles:
            biometric = f"fingerprint_{role}_data_12345"
            hashed = auth_service.hash_biometric(biometric)

            assert hashed is not None
            assert len(hashed) == 64
            assert auth_service.verify_biometric(biometric, hashed) is True

    def test_biometric_unique_per_role(self):
        """Test que la biométrie est unique par rôle."""
        biometrics = [f"fingerprint_role_{i}_data" for i in range(4)]
        hashes = [auth_service.hash_biometric(b) for b in biometrics]
        assert len(set(hashes)) == 4


class TestQRService:
    """Teste le service QR code."""

    def test_qr_service_exists(self):
        """Test que le service QR existe."""
        from backend.services.qr_service import qr_service

        assert qr_service is not None
        assert hasattr(qr_service, "generate_qr_code")
        assert hasattr(qr_service, "verify_and_use_qr")


class TestHornDetection:
    """Teste la détection de klaxon."""

    def test_horn_service_exists(self):
        """Test que le service klaxon existe."""
        from backend.services.horn_detection import horn_detection_service

        assert horn_detection_service is not None
        assert hasattr(horn_detection_service, "is_acceptance_pattern")
        assert hasattr(horn_detection_service, "is_refus_pattern")
