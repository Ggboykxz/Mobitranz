# ============================================================
# Tests User Model
# Fichier : backend/tests/test_user_model.py
# ============================================================

import pytest
from backend.models.user import User, UserRole, UserStatus


class TestUserModel:
    """Tests pour le modèle User."""

    def test_user_creation(self):
        """Test création utilisateur."""
        user = User(
            phone="+24106000000",
            password_hash="hashed_password",
            role=UserRole.CLIENT,
            status=UserStatus.ACTIVE
        )
        
        assert user.phone == "+24106000000"
        assert user.password_hash == "hashed_password"
        assert user.role == UserRole.CLIENT
        assert user.status == UserStatus.ACTIVE

    def test_user_roles(self):
        """Test les rôles utilisateurs."""
        assert UserRole.CLIENT.value == "client"
        assert UserRole.DRIVER.value == "driver"
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MINISTRY.value == "ministry"

    def test_user_status(self):
        """Test les statuts utilisateurs."""
        assert UserStatus.PENDING.value == "pending"
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.SUSPENDED.value == "suspended"
        assert UserStatus.DELETED.value == "deleted"

    def test_user_default_values(self):
        """Test les valeurs par défaut."""
        user = User(
            phone="+24106000000",
            password_hash="hashed"
        )
        
        assert user.role == UserRole.CLIENT
        assert user.status == UserStatus.PENDING
        assert user.kyc_verified is False
        assert user.failed_login_attempts == 0

    def test_user_repr(self):
        """Test la représentation string."""
        user = User(
            phone="+24106000000",
            password_hash="hashed",
            role=UserRole.CLIENT
        )
        
        assert "client" in repr(user)
        assert "+24106000000" in repr(user)