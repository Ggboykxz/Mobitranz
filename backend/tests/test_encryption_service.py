import pytest


class TestEncryptionServiceBasics:

    def test_encryption_service_init(self):
        from backend.services.encryption_service import encryption_service

        assert encryption_service is not None

    def test_generate_aes_key(self):
        from backend.services.encryption_service import encryption_service

        key = encryption_service.generate_aes_key()
        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_generate_nonce(self):
        from backend.services.encryption_service import encryption_service

        nonce = encryption_service.generate_nonce()
        assert isinstance(nonce, bytes)
        assert len(nonce) == 12

    def test_encrypt_decrypt_roundtrip(self):
        from backend.services.encryption_service import encryption_service

        key = encryption_service.generate_aes_key()
        original = b"Secret data"

        ciphertext, nonce = encryption_service.encrypt_aesgcm(original, key)
        decrypted = encryption_service.decrypt_aesgcm(ciphertext, key, nonce)

        assert decrypted == original

    def test_encrypt_different_nonce(self):
        from backend.services.encryption_service import encryption_service

        key = encryption_service.generate_aes_key()
        original = b"Data"

        ct1, n1 = encryption_service.encrypt_aesgcm(original, key)
        ct2, n2 = encryption_service.encrypt_aesgcm(original, key)

        assert n1 != n2

    def test_encrypt_long_data(self):
        from backend.services.encryption_service import encryption_service

        key = encryption_service.generate_aes_key()
        original = b"A" * 10000

        ct, nonce = encryption_service.encrypt_aesgcm(original, key)
        decrypted = encryption_service.decrypt_aesgcm(ct, key, nonce)

        assert decrypted == original

    def test_encrypt_empty(self):
        from backend.services.encryption_service import encryption_service

        key = encryption_service.generate_aes_key()
        original = b""

        ct, nonce = encryption_service.encrypt_aesgcm(original, key)
        decrypted = encryption_service.decrypt_aesgcm(ct, key, nonce)

        assert decrypted == b""

    def test_hash_sha256(self):
        from backend.services.encryption_service import encryption_service

        result = encryption_service.hash_sha256("test")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_hash_sha256_consistency(self):
        from backend.services.encryption_service import encryption_service

        r1 = encryption_service.hash_sha256("test")
        r2 = encryption_service.hash_sha256("test")

        assert r1 == r2

    def test_aes_key_size_constant(self):
        from backend.services.encryption_service import EncryptionService

        assert EncryptionService.AES_KEY_SIZE == 32
        assert EncryptionService.NONCE_SIZE == 12
