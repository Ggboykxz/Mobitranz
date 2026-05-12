# ============================================================
# Security Headers Middleware
# Fichier : backend/middleware/security.py
# Description : En-têtes de sécurité HTTP
# ============================================================

import asyncio
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import structlog

logger = structlog.get_logger()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware pour les en-têtes de sécurité.

    Ajoute des headers de sécurité pour protéger l'application
    contre les attaques courantes (XSS, CSRF, clickjacking, etc.)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Traitement de la requête avec headers de sécurité."""

        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss: https:; "
            "font-src 'self'; "
            "frame-ancestors 'none';"
        )

        return response


class RedisRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60, redis_client=None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.redis_client = redis_client

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
            if client_ip:
                return client_ip
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = self._get_client_ip(request)
        minute_window = int(time.time() / 60)
        key = f"ratelimit:{client_ip}:{minute_window}"

        if self.redis_client and self.redis_client.redis:
            try:
                current = await self.redis_client.redis.incr(key)
                if current == 1:
                    await self.redis_client.redis.expire(key, 60)
                if current > self.requests_per_minute:
                    logger.warning("Rate limit exceeded (Redis)", ip=client_ip)
                    from fastapi.responses import JSONResponse
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many requests. Please try again later."},
                        headers={"Retry-After": "60"},
                    )
            except Exception:
                pass

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        return response
