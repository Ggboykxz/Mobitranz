import pytest


class TestAuditServiceMethods:

    def test_audit_service_exists(self):
        from backend.services.audit_service import audit_service

        assert audit_service is not None

    def test_audit_service_has_log_action(self):
        from backend.services.audit_service import AuditService

        assert hasattr(AuditService, "log_action")

    def test_audit_service_has_log_user_login(self):
        from backend.services.audit_service import AuditService

        assert hasattr(AuditService, "log_user_login")

    def test_audit_service_has_log_user_logout(self):
        from backend.services.audit_service import AuditService

        assert hasattr(AuditService, "log_user_logout")

    def test_audit_service_has_log_payment(self):
        from backend.services.audit_service import AuditService

        assert hasattr(AuditService, "log_payment")
