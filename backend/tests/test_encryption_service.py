import base64

import pytest
from cryptography.exceptions import InvalidTag


class TestEncryptionService:
    def setup_method(self):
        from backend.services.encryption_service import encryption_service

        self.service = encryption_service

    def test_aes_key_generation(self):
        key = self.service.generate_aes_key()
        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_nonce_generation(self):
        nonce = self.service.generate_nonce()
        assert isinstance(nonce, bytes)
        assert len(nonce) == 12

    def test_encrypt_decrypt_roundtrip(self):
        key = self.service.generate_aes_key()
        original = b"This is secret data for MobiTranz"
        ciphertext, nonce = self.service.encrypt_aesgcm(original, key)
        decrypted = self.service.decrypt_aesgcm(ciphertext, key, nonce)
        assert decrypted == original

    def test_encrypt_empty_data(self):
        key = self.service.generate_aes_key()
        original = b""
        ciphertext, nonce = self.service.encrypt_aesgcm(original, key)
        decrypted = self.service.decrypt_aesgcm(ciphertext, key, nonce)
        assert decrypted == b""

    def test_encrypt_large_data(self):
        key = self.service.generate_aes_key()
        original = b"A" * 100000
        ciphertext, nonce = self.service.encrypt_aesgcm(original, key)
        decrypted = self.service.decrypt_aesgcm(ciphertext, key, nonce)
        assert decrypted == original

    def test_different_nonce_each_time(self):
        key = self.service.generate_aes_key()
        original = b"Data"
        ct1, n1 = self.service.encrypt_aesgcm(original, key)
        ct2, n2 = self.service.encrypt_aesgcm(original, key)
        assert n1 != n2
        assert ct1 != ct2

    def test_decrypt_with_wrong_key(self):
        key = self.service.generate_aes_key()
        wrong_key = self.service.generate_aes_key()
        original = b"Secret"
        ciphertext, nonce = self.service.encrypt_aesgcm(original, key)
        with pytest.raises(InvalidTag):
            self.service.decrypt_aesgcm(ciphertext, wrong_key, nonce)

    def test_decrypt_with_wrong_nonce(self):
        key = self.service.generate_aes_key()
        original = b"Secret"
        ciphertext, _ = self.service.encrypt_aesgcm(original, key)
        wrong_nonce = self.service.generate_nonce()
        with pytest.raises(InvalidTag):
            self.service.decrypt_aesgcm(ciphertext, key, wrong_nonce)

    def test_decrypt_tampered_ciphertext(self):
        key = self.service.generate_aes_key()
        original = b"Secret"
        ciphertext, nonce = self.service.encrypt_aesgcm(original, key)
        tampered = bytearray(ciphertext)
        tampered[0] ^= 0xFF
        with pytest.raises(InvalidTag):
            self.service.decrypt_aesgcm(bytes(tampered), key, nonce)

    def test_key_derivation(self):
        password = "MySecurePassword123!"
        salt = b"fixed_salt_16byt"[:16]
        key = self.service.derive_key_from_password(password, salt)
        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_key_derivation_different_password(self):
        salt = b"fixed_salt_16byt"[:16]
        key1 = self.service.derive_key_from_password("password1", salt)
        key2 = self.service.derive_key_from_password("password2", salt)
        assert key1 != key2

    def test_key_derivation_different_salt(self):
        key1 = self.service.derive_key_from_password(
            "password", b"salt_16_bytes_1"
        )
        key2 = self.service.derive_key_from_password(
            "password", b"salt_16_bytes_2"
        )
        assert key1 != key2

    def test_derive_then_encrypt(self):
        password = "MyPa$$w0rd!"
        salt = b"test_salt_123456"
        key = self.service.derive_key_from_password(password, salt)

        original = b"Encrypted with derived key"
        ciphertext, nonce = self.service.encrypt_aesgcm(original, key)
        decrypted = self.service.decrypt_aesgcm(ciphertext, key, nonce)
        assert decrypted == original

    def test_hash_sha256(self):
        result = self.service.hash_sha256("test")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_hash_sha256_consistency(self):
        assert self.service.hash_sha256("test") == self.service.hash_sha256("test")
        assert self.service.hash_sha256("test") != self.service.hash_sha256("different")

    def test_compute_audit_hash(self):
        result = self.service.compute_audit_hash(
            "0" * 64, '{"action":"LOGIN"}', "2024-01-01T00:00:00"
        )
        assert isinstance(result, str)
        assert len(result) == 64

    def test_compute_audit_hash_chain(self):
        prev = "0" * 64
        h1 = self.service.compute_audit_hash(prev, "LOGIN", "t1")
        h2 = self.service.compute_audit_hash(h1, "LOGOUT", "t2")
        assert h1 != h2
        assert h1 != prev

    def test_video_chunk_roundtrip(self):
        key = self.service.generate_aes_key()
        chunk = b"video frame data " * 1000
        encrypted, nonce = self.service.encrypt_video_chunk(chunk, key)
        decrypted = self.service.decrypt_video_chunk(encrypted, key, nonce)
        assert decrypted == chunk

    def test_base64_encode_decode(self):
        key = self.service.generate_aes_key()
        encoded = self.service.encode_key_base64(key)
        assert isinstance(encoded, str)
        decoded = self.service.decode_key_base64(encoded)
        assert decoded == key

    def test_constants(self):
        from backend.services.encryption_service import EncryptionService

        assert EncryptionService.AES_KEY_SIZE == 32
        assert EncryptionService.NONCE_SIZE == 12
