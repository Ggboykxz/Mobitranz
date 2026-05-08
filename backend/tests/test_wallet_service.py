import pytest


class TestWalletEnums:

    def test_wallet_status_enum(self):
        from backend.services.wallet_service import WalletStatus

        assert WalletStatus.ACTIVE.value == "active"
        assert WalletStatus.FROZEN.value == "frozen"
        assert WalletStatus.SUSPENDED.value == "suspended"

    def test_wallet_operation_type_enum(self):
        from backend.services.wallet_service import WalletOperationType

        assert WalletOperationType.DEPOSIT.value == "deposit"
        assert WalletOperationType.WITHDRAWAL.value == "withdrawal"
        assert WalletOperationType.PAYMENT.value == "payment"
        assert WalletOperationType.REFUND.value == "refund"
        assert WalletOperationType.BONUS.value == "bonus"
        assert WalletOperationType.FEE.value == "fee"

    def test_wallet_status_values(self):
        from backend.services.wallet_service import WalletStatus

        statuses = [s.value for s in WalletStatus]
        assert "active" in statuses
        assert "frozen" in statuses
        assert "suspended" in statuses

    def test_wallet_operation_type_values(self):
        from backend.services.wallet_service import WalletOperationType

        operations = [o.value for o in WalletOperationType]
        assert "deposit" in operations
        assert "withdrawal" in operations
        assert "payment" in operations
        assert "refund" in operations
        assert "bonus" in operations
        assert "fee" in operations
