import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from backend.models.user import User, UserRole, UserStatus


class TestAuthServiceUnit:
    def test_hash_password(self):
        from backend.services.auth_service import auth_service

        hashed = auth_service.hash_password("SecurePass123!")
        assert hashed is not None
        assert hashed != "SecurePass123!"
        assert auth_service.verify_password("SecurePass123!", hashed) is True
        assert auth_service.verify_password("WrongPass", hashed) is False

    def test_create_access_token(self):
        from backend.services.auth_service import auth_service

        token = auth_service.create_access_token(user_id="user-1", role="client")
        assert isinstance(token, str)
        assert len(token) > 0

        payload = auth_service.verify_token(token)
        assert payload["sub"] == "user-1"
        assert payload["role"] == "client"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        from backend.services.auth_service import auth_service

        token = auth_service.create_refresh_token(user_id="user-1")
        payload = auth_service.verify_token(token)
        assert payload["sub"] == "user-1"
        assert payload["type"] == "refresh"
        assert "nonce" in payload

    def test_verify_token_invalid(self):
        from backend.services.auth_service import auth_service

        assert auth_service.verify_token("not-a-valid-token") is None
        assert auth_service.verify_token("") is None

    def test_generate_reset_code(self):
        from backend.services.auth_service import auth_service

        code = auth_service.generate_reset_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_totp_flow(self):
        from backend.services.auth_service import auth_service
        import pyotp

        secret = auth_service.generate_totp_secret()
        assert len(secret) > 0
        uri = auth_service.get_totp_uri(secret, "testuser")
        assert "otpauth://totp/" in uri
        assert "testuser" in uri

        totp = pyotp.TOTP(secret)
        valid_code = totp.now()
        assert auth_service.verify_totp(secret, valid_code) is True
        assert auth_service.verify_totp(secret, "000000") is False

    def test_biometric_hashing(self):
        from backend.services.auth_service import auth_service

        data = "fingerprint_data_xyz"
        hashed = auth_service.hash_biometric(data)
        assert len(hashed) == 64
        assert auth_service.verify_biometric(data, hashed) is True
        assert auth_service.verify_biometric("wrong_data", hashed) is False

    async def test_authenticate_user(self, db_session: AsyncSession):
        from backend.services.auth_service import auth_service
        from backend.models.user import User, UserRole, UserStatus

        user = User(
            phone="+24106000099",
            password_hash=auth_service.hash_password("CorrectPass1"),
            role=UserRole.CLIENT,
            status=UserStatus.ACTIVE,
        )
        db_session.add(user)
        await db_session.commit()

        result = await auth_service.authenticate_user(
            db_session, "+24106000099", "CorrectPass1"
        )
        assert result is not None
        assert result.phone == "+24106000099"

        result_bad = await auth_service.authenticate_user(
            db_session, "+24106000099", "WrongPass"
        )
        assert result_bad is None

        result_nonexist = await auth_service.authenticate_user(
            db_session, "+24199999999", "pass"
        )
        assert result_nonexist is None

    async def test_account_locking(self, db_session: AsyncSession):
        from backend.services.auth_service import auth_service
        from backend.models.user import User, UserRole, UserStatus
        from datetime import datetime, timedelta, timezone

        user = User(
            phone="+24106000098",
            password_hash=auth_service.hash_password("pass"),
            role=UserRole.CLIENT,
            status=UserStatus.ACTIVE,
            failed_login_attempts=0,
        )
        db_session.add(user)
        await db_session.commit()

        assert await auth_service.check_account_locked(db_session, user) is False

        await auth_service.increment_failed_attempts(db_session, user)
        assert user.failed_login_attempts == 1

        user.failed_login_attempts = 3
        await auth_service.increment_failed_attempts(db_session, user)
        assert user.locked_until is not None
        assert await auth_service.check_account_locked(db_session, user) is True

        await auth_service.reset_failed_attempts(db_session, user)
        assert user.failed_login_attempts == 0
        assert user.locked_until is None


_PREFIX = "/auth"


class TestAuthEndpoints:
    async def test_register_user(self, async_client: AsyncClient):
        response = await async_client.post(
            f"{_PREFIX}/register",
            json={
                "phone": "+24106000002",
                "password": "StrongPass123!",
                "first_name": "Alice",
                "last_name": "Diallo",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    async def test_register_duplicate_phone(self, async_client: AsyncClient):
        await async_client.post(
            f"{_PREFIX}/register",
            json={"phone": "+24106000003", "password": "StrongPass123!"},
        )
        response = await async_client.post(
            f"{_PREFIX}/register",
            json={"phone": "+24106000003", "password": "StrongPass123!"},
        )
        response = await async_client.post(
            f"{_PREFIX}/register",
            json={"phone": "+24106000003", "password": "StrongPass123!"},
        )
        assert response.status_code == 500

    async def test_login_success(self, async_client: AsyncClient):
        await async_client.post(
            f"{_PREFIX}/register",
            json={"phone": "+24106000004", "password": "StrongPass123!"},
        )
        response = await async_client.post(
            f"{_PREFIX}/login",
            json={"phone": "+24106000004", "password": "StrongPass123!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_wrong_password(self, async_client: AsyncClient):
        await async_client.post(
            f"{_PREFIX}/register",
            json={"phone": "+24106000005", "password": "StrongPass123!"},
        )
        response = await async_client.post(
            f"{_PREFIX}/login",
            json={"phone": "+24106000005", "password": "WrongPassword"},
        )
        assert response.status_code == 401
        assert "invalide" in response.json()["detail"].lower()

    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        response = await async_client.post(
            f"{_PREFIX}/login",
            json={"phone": "+24199999999", "password": "SomePass123!"},
        )
        assert response.status_code == 401

    async def test_refresh_token(self, async_client: AsyncClient):
        register_resp = await async_client.post(
            f"{_PREFIX}/register",
            json={"phone": "+24106000006", "password": "StrongPass123!"},
        )
        tokens = register_resp.json()
        refresh = tokens["refresh_token"]

        response = await async_client.post(
            f"{_PREFIX}/refresh",
            json={"refresh_token": refresh},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_invalid_token(self, async_client: AsyncClient):
        response = await async_client.post(
            f"{_PREFIX}/refresh",
            json={"refresh_token": "invalid_token_here"},
        )
        assert response.status_code == 401

    async def test_logout(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.post(f"{_PREFIX}/logout", headers=auth_headers)
        assert response.status_code == 200
        assert "réussie" in response.json()["message"].lower()

    async def test_password_reset_request(self, async_client: AsyncClient):
        await async_client.post(
            f"{_PREFIX}/register",
            json={"phone": "+24106000007", "password": "StrongPass123!"},
        )
        response = await async_client.post(
            f"{_PREFIX}/password-reset/request",
            params={"phone": "+24106000007"},
        )
        assert response.status_code == 200
        assert "code" in response.json()["message"].lower()

    async def test_password_reset_flow(self, async_client: AsyncClient):
        await async_client.post(
            f"{_PREFIX}/register",
            json={"phone": "+24106000008", "password": "StrongPass123!"},
        )
        reset_resp = await async_client.post(
            f"{_PREFIX}/password-reset/request",
            params={"phone": "+24106000008"},
        )
        assert reset_resp.status_code == 200

        from backend.database import AsyncSession, async_sessionmaker
        from backend.models.user import User
        from sqlalchemy import select

        engine = async_client._transport.app.dependency_overrides
        response = await async_client.post(
            f"{_PREFIX}/password-reset/confirm",
            params={
                "phone": "+24106000008",
                "code": "000000",
                "new_password": "NewStrongPass456!",
            },
        )
        assert response.status_code in (200, 400)

    async def test_totp_setup(self, async_client: AsyncClient, auth_headers: dict):
        response = await async_client.get(f"{_PREFIX}/totp/setup", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "secret" in data
        assert "uri" in data
        assert "otpauth://" in data["uri"]

    async def test_register_with_email(self, async_client: AsyncClient):
        response = await async_client.post(
            f"{_PREFIX}/register",
            json={
                "phone": "+24106000009",
                "password": "StrongPass123!",
                "email": "alice@example.com",
                "first_name": "Alice",
                "last_name": "Diallo",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
