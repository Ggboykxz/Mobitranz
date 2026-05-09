# ============================================================
# Security Utils
# Fichier : backend/utils/security.py
# ============================================================

import hmac
import hashlib
import secrets
import time
from typing import Optional
from functools import wraps
from fastapi import HTTPException, Request, status


def generate_csrf_token() -> str:
    """Génère un token CSRF."""
    return secrets.token_hex(32)


def verify_csrf_token(token: str, secret: str) -> bool:
    """Vérifie un token CSRF."""
    expected = hmac.new(
        secret.encode(),
        token.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(token, expected)


def generate_api_key(prefix: str = "mtk") -> str:
    """Génère une clé API."""
    timestamp = str(int(time.time()))
    random_part = secrets.token_hex(16)
    return f"{prefix}_{timestamp}_{random_part}"


def hash_api_key(key: str) -> str:
    """Hache une clé API pour stockage."""
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(key: str, hashed: str) -> bool:
    """Vérifie une clé API."""
    return hmac.compare_digest(hash_api_key(key), hashed)


def rate_limit_key(identifier: str, endpoint: str) -> str:
    """Génère une clé pour le rate limiting."""
    return f"rate:{identifier}:{endpoint}"


class IPBlocker:
    """Gestionnaire de blocage d'IPs."""

    def __init__(self):
        self._blocked_ips = set()
        self._temp_blocks = {}

    def block_ip(self, ip: str):
        """Bloque une IP définitivement."""
        self._blocked_ips.add(ip)

    def temp_block(self, ip: str, duration: int = 300):
        """Bloque temporairement une IP."""
        self._temp_blocks[ip] = time.time() + duration

    def is_blocked(self, ip: str) -> bool:
        """Vérifie si une IP est bloquée."""
        if ip in self._blocked_ips:
            return True
        if ip in self._temp_blocks:
            if time.time() > self._temp_blocks[ip]:
                del self._temp_blocks[ip]
                return False
            return True
        return False

    def unblock_ip(self, ip: str):
        """Débloque une IP."""
        self._blocked_ips.discard(ip)
        self._temp_blocks.pop(ip, None)


# Instance globale
ip_blocker = IPBlocker()


def check_ip_blocked(ip: str):
    """Vérifie et lève une exception si IP bloquée."""
    if ip_blocker.is_blocked(ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="IP bloquée"
        )


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize une entrée utilisateur."""
    if not text:
        return ""
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    return text


def validate_phone_gabon(phone: str) -> bool:
    """Valide un numéro de téléphone gabonais."""
    import re
    patterns = [
        r'^\+241[0-9]{8}$',
        r'^241[0-9]{8}$',
        r'^0[6-7][0-9]{7}$',
    ]
    return any(re.match(p, phone) for p in patterns)


# Injection SQL prevention (basic)
SQL_KEYWORDS = [
    'DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER',
    'UNION', 'EXEC', 'EXECUTE', 'TRUNCATE'
]

def contains_sql_injection(text: str) -> bool:
    """Détecte une injection SQL potentielle."""
    text_upper = text.upper()
    return any(keyword in text_upper for keyword in SQL_KEYWORDS)


def detect_xss(text: str) -> bool:
    """Détecte du XSS potentiel."""
    xss_patterns = ['<script', 'javascript:', 'onerror=', 'onload=']
    text_lower = text.lower()
    return any(pattern in text_lower for pattern in xss_patterns)