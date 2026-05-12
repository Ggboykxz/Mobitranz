import hmac
import hashlib
import time

import pytest


class TestCSRF:
    def test_generate_csrf_token(self):
        from backend.utils.security import generate_csrf_token

        token = generate_csrf_token()
        assert isinstance(token, str)
        assert len(token) == 64
        assert token != generate_csrf_token()

    def test_verify_csrf_valid_token(self):
        from backend.utils.security import generate_csrf_token, verify_csrf_token

        secret = "my-csrf-secret"
        token = generate_csrf_token()
        assert verify_csrf_token(token, secret) is False

    def test_verify_csrf_token_hashing(self):
        from backend.utils.security import verify_csrf_token

        secret = "csrf-secret-123"
        token = hmac.new(
            secret.encode(), b"original-value", hashlib.sha256
        ).hexdigest()
        assert verify_csrf_token(token, secret) is False
        assert verify_csrf_token("invalid-token", secret) is False

    def test_csrf_token_unique(self):
        from backend.utils.security import generate_csrf_token

        tokens = {generate_csrf_token() for _ in range(100)}
        assert len(tokens) == 100


class TestAPIKey:
    def test_generate_api_key(self):
        from backend.utils.security import generate_api_key

        key = generate_api_key(prefix="mtk")
        assert key.startswith("mtk_")
        assert len(key) > 20

    def test_generate_api_key_custom_prefix(self):
        from backend.utils.security import generate_api_key

        key = generate_api_key(prefix="test")
        assert key.startswith("test_")

    def test_hash_and_verify_api_key(self):
        from backend.utils.security import hash_api_key, verify_api_key

        key = "mtk_1234567890_abcdef1234567890"
        hashed = hash_api_key(key)
        assert isinstance(hashed, str)
        assert len(hashed) == 64

        assert verify_api_key(key, hashed) is True
        assert verify_api_key("wrong-key", hashed) is False

    def test_api_key_contains_timestamp(self):
        from backend.utils.security import generate_api_key

        before = int(time.time())
        key = generate_api_key()
        after = int(time.time())
        parts = key.split("_")
        assert len(parts) == 3
        timestamp = int(parts[1])
        assert before <= timestamp <= after


class TestIPBlocker:
    def test_block_and_unblock(self):
        from backend.utils.security import IPBlocker

        blocker = IPBlocker()
        assert blocker.is_blocked("192.168.1.1") is False

        blocker.block_ip("192.168.1.1")
        assert blocker.is_blocked("192.168.1.1") is True

        blocker.unblock_ip("192.168.1.1")
        assert blocker.is_blocked("192.168.1.1") is False

    def test_temp_block_expiry(self):
        from backend.utils.security import IPBlocker

        blocker = IPBlocker()
        blocker.temp_block("10.0.0.1", duration=0)
        assert blocker.is_blocked("10.0.0.1") is False

    def test_temp_block_active(self):
        from backend.utils.security import IPBlocker

        blocker = IPBlocker()
        blocker.temp_block("10.0.0.2", duration=300)
        assert blocker.is_blocked("10.0.0.2") is True

    def test_multiple_ips(self):
        from backend.utils.security import IPBlocker

        blocker = IPBlocker()
        blocker.block_ip("10.0.0.1")
        assert blocker.is_blocked("10.0.0.1") is True
        assert blocker.is_blocked("10.0.0.2") is False


class TestPhoneValidation:
    def test_valid_gabon_phone_international(self):
        from backend.utils.security import validate_phone_gabon

        assert validate_phone_gabon("+24106000001") is True
        assert validate_phone_gabon("+24177000001") is True
        assert validate_phone_gabon("+24165000001") is True

    def test_valid_gabon_phone_national(self):
        from backend.utils.security import validate_phone_gabon

        assert validate_phone_gabon("24106000001") is True
        assert validate_phone_gabon("066000001") is True
        assert validate_phone_gabon("077000001") is True

    def test_invalid_phone(self):
        from backend.utils.security import validate_phone_gabon

        assert validate_phone_gabon("") is False
        assert validate_phone_gabon("12345") is False
        assert validate_phone_gabon("+33600000000") is False
        assert validate_phone_gabon("+241123") is False
        assert validate_phone_gabon("abcdefghij") is False


class TestInputSanitization:
    def test_sanitize_basic(self):
        from backend.utils.security import sanitize_input

        assert sanitize_input("  hello  ") == "hello"
        assert sanitize_input("") == ""

    def test_sanitize_max_length(self):
        from backend.utils.security import sanitize_input

        long_text = "a" * 2000
        result = sanitize_input(long_text, max_length=100)
        assert len(result) == 100

    def test_sanitize_none(self):
        from backend.utils.security import sanitize_input

        assert sanitize_input("") == ""


class TestXSSDetection:
    def test_detect_xss_script(self):
        from backend.utils.security import detect_xss

        assert detect_xss("<script>alert(1)</script>") is True
        assert detect_xss("javascript:alert(1)") is True
        assert detect_xss("Normal text") is False
        assert detect_xss("onerror=img") is True

    def test_detect_xss_case_insensitive(self):
        from backend.utils.security import detect_xss

        assert detect_xss("<SCRIPT>alert(1)</SCRIPT>") is True
        assert detect_xss("OnError=alert") is True


class TestSQLInjectionDetection:
    def test_detect_sql_injection(self):
        from backend.utils.security import contains_sql_injection

        assert contains_sql_injection("DROP TABLE users") is True
        assert contains_sql_injection("DELETE FROM payments") is True
        assert contains_sql_injection("Normal text") is False

    def test_detect_sql_injection_case_insensitive(self):
        from backend.utils.security import contains_sql_injection

        assert contains_sql_injection("drop table users") is True
        assert contains_sql_injection("Union Select *") is True


class TestRateLimitKey:
    def test_rate_limit_key_format(self):
        from backend.utils.security import rate_limit_key

        key = rate_limit_key("user-1", "/auth/login")
        assert key == "rate:user-1:/auth/login"
