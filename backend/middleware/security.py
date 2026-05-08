# ============================================================
# Security Headers Middleware
# Fichier : backend/middleware/security.py
# Description : En-têtes de sécurité HTTP
# ============================================================

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


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware pour le rate limiting.

    Limite le nombre de requêtes par IP pour éviter les abus.
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        """Traitement de la requête avec rate limiting."""
        client_ip = request.client.host if request.client else "unknown"

        import time

        current_time = int(time.time() / 60)

        key = f"{client_ip}:{current_time}"

        if key in self.request_counts:
            if self.request_counts[key] >= self.requests_per_minute:
                logger.warning("Rate limit exceeded", ip=client_ip)
                from fastapi.responses import JSONResponse

                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."},
                )
            self.request_counts[key] += 1
        else:
            self.request_counts[key] = 1

        self.request_counts = {
            k: v
            for k, v in self.request_counts.items()
            if k.endswith(str(current_time))
        }

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)

        return response
