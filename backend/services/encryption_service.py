# ============================================================
# Chiffrement MobiTranz
# Fichier : backend/services/encryption_service.py
# Description : AES-256-GCM, hachage bcrypt, RSA-2048
# ============================================================

import secrets
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import structlog
from typing import Tuple


logger = structlog.get_logger()


class EncryptionService:
    """Service de chiffrement MobiTranz.
    
    Gère AES-256-GCM pour le chiffrement vidéo,
    le hachage des mots de passe et données biométriques.
    """
    
    AES_KEY_SIZE = 32  # 256 bits
    NONCE_SIZE = 12   # 96 bits pour AES-GCM
    
    def generate_aes_key(self) -> bytes:
        """Génère une clé AES-256 aléatoire.
        
        Returns:
            bytes: Clé de 32 octets
        """
        return secrets.token_bytes(self.AES_KEY_SIZE)
    
    def generate_nonce(self) -> bytes:
        """Génère un nonce aléatoire pour AES-GCM.
        
        Returns:
            bytes: Nonce de 12 octets
        """
        return secrets.token_bytes(self.NONCE_SIZE)
    
    def encrypt_aesgcm(
        self,
        data: bytes,
        key: bytes
    ) -> Tuple[bytes, bytes]:
        """Chiffre des données avec AES-256-GCM.
        
        Args:
            data: Données à chiffrer
            key: Clé AES-256
            
        Returns:
            Tuple[bytes, bytes]: (données chiffrées, nonce)
        """
        nonce = self.generate_nonce()
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        
        return ciphertext, nonce
    
    def decrypt_aesgcm(
        self,
        ciphertext: bytes,
        key: bytes,
        nonce: bytes
    ) -> bytes:
        """Déchiffre des données avec AES-256-GCM.
        
        Args:
            ciphertext: Données chiffrées
            key: Clé AES-256
            nonce: Nonce utilisé
            
        Returns:
            bytes: Données déchiffrées
        """
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)
    
    def derive_key_from_password(
        self,
        password: str,
        salt: bytes,
        iterations: int = 100000
    ) -> bytes:
        """Dérive une clé depuis un mot de passe via PBKDF2.
        
        Args:
            password: Mot de passe
            salt: Sel aléatoire
            iterations: Nombre d'itérations
            
        Returns:
            bytes: Clé dérivée
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.AES_KEY_SIZE,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        
        return kdf.derive(password.encode())
    
    def hash_sha256(self, data: str) -> str:
        """Calcule le hash SHA-256.
        
        Args:
            data: Données à hasher
            
        Returns:
            str: Hash hexadécimal
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def compute_audit_hash(
        self,
        previous_hash: str,
        data: str,
        timestamp: str
    ) -> str:
        """Calcule le hash pour une entrée d'audit.
        
        Args:
            previous_hash: Hash de l'entrée précédente
            data: Données JSON de l'entrée
            timestamp: Timestamp
            
        Returns:
            str: Hash SHA-256 encodé en hex
        """
        content = f"{previous_hash}:{data}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def encrypt_video_chunk(
        self,
        chunk: bytes,
        trip_key: bytes
    ) -> Tuple[bytes, bytes]:
        """Chiffre un chunk vidéo avec AES-GCM.
        
        Args:
            chunk: Données vidéo (1MB max)
            trip_key: Clé unique par trajet
            
        Returns:
            Tuple[bytes, bytes]: (chunk chiffré, nonce)
        """
        return self.encrypt_aesgcm(chunk, trip_key)
    
    def decrypt_video_chunk(
        self,
        encrypted_chunk: bytes,
        trip_key: bytes,
        nonce: bytes
    ) -> bytes:
        """Déchiffre un chunk vidéo avec AES-GCM.
        
        Args:
            encrypted_chunk: Chunk chiffré
            trip_key: Clé unique par trajet
            nonce: Nonce utilisé
            
        Returns:
            bytes: Chunk déchiffré
        """
        return self.decrypt_aesgcm(encrypted_chunk, trip_key, nonce)
    
    def encode_key_base64(self, key: bytes) -> str:
        """Encode une clé en base64.
        
        Args:
            key: Clé binaire
            
        Returns:
            str: Clé encodée en base64
        """
        return base64.b64encode(key).decode()
    
    def decode_key_base64(self, key_encoded: str) -> bytes:
        """Decode une clé depuis base64.
        
        Args:
            key_encoded: Clé encodée
            
        Returns:
            bytes: Clé binaire
        """
        return base64.b64decode(key_encoded)


encryption_service = EncryptionService()