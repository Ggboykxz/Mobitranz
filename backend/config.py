# ============================================================
# Configuration Pydantic du projet MobiTranz
# Fichier : backend/config.py
# Description : Paramètres globaux chargés depuis .env
# ============================================================

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Paramètres globaux de l'application MobiTranz.

    Configure tous les paramètres via variables d'environnement.
    Utilise pydantic-settings pour la validation automatique.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Configuration Serveur
    app_name: str = Field(default="MobiTranz", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    secret_key: str = Field(default=None, alias="SECRET_KEY")

    # Configuration Base de Données
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/mobitranz",
        alias="DATABASE_URL",
    )

    # Configuration Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Configuration JWT
    access_token_expire_minutes: int = Field(
        default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")

    # Configuration MoovMoney (API Gabon)
    moovmoney_api_url: Optional[str] = Field(default=None, alias="MOOVMONEY_API_URL")
    moovmoney_api_key: Optional[str] = Field(default=None, alias="MOOVMONEY_API_KEY")
    moovmoney_api_secret: Optional[str] = Field(
        default=None, alias="MOOVMONEY_API_SECRET"
    )

    # Configuration Airtel Money (API Gabon)
    airtelmoney_api_url: Optional[str] = Field(
        default=None, alias="AIRTELMONEY_API_URL"
    )
    airtelmoney_api_key: Optional[str] = Field(
        default=None, alias="AIRTELMONEY_API_KEY"
    )
    airtelmoney_api_secret: Optional[str] = Field(
        default=None, alias="AIRTELMONEY_API_SECRET"
    )

    # Configuration Firebase (Push Notifications)
    firebase_credentials_path: Optional[str] = Field(
        default=None, alias="FIREBASE_CREDENTIALS_PATH"
    )

    # Configuration Cloudinary (Stockage fichiers)
    cloudinary_cloud_name: Optional[str] = Field(
        default=None, alias="CLOUDINARY_CLOUD_NAME"
    )
    cloudinary_api_key: Optional[str] = Field(default=None, alias="CLOUDINARY_API_KEY")
    cloudinary_api_secret: Optional[str] = Field(
        default=None, alias="CLOUDINARY_API_SECRET"
    )

    # Configuration Sentry (Monitoring)
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")

    # Configuration Rate Limiting
    rate_limit_auth_requests: int = Field(default=5, alias="RATE_LIMIT_AUTH_REQUESTS")
    rate_limit_auth_window: int = Field(default=900, alias="RATE_LIMIT_AUTH_WINDOW")
    rate_limit_payment_requests: int = Field(
        default=10, alias="RATE_LIMIT_PAYMENT_REQUESTS"
    )
    rate_limit_payment_window: int = Field(
        default=60, alias="RATE_LIMIT_PAYMENT_WINDOW"
    )
    rate_limit_general_requests: int = Field(
        default=100, alias="RATE_LIMIT_GENERAL_REQUESTS"
    )
    rate_limit_general_window: int = Field(
        default=60, alias="RATE_LIMIT_GENERAL_WINDOW"
    )

    # Configuration Fuseau Horaire
    tz: str = Field(default="Africa/Libreville", alias="TZ")

    # Configuration Ministères (Webhooks sortants)
    ministry_transport_webhook: Optional[str] = Field(
        default=None, alias="MINISTRY_TRANSPORT_WEBHOOK"
    )
    ministry_interior_webhook: Optional[str] = Field(
        default=None, alias="MINISTRY_INTERIOR_WEBHOOK"
    )
    ministry_api_key: Optional[str] = Field(default=None, alias="MINISTRY_API_KEY")

    # Configuration MinIO (Stockage médias)
    minio_endpoint: Optional[str] = Field(default=None, alias="MINIO_ENDPOINT")
    minio_access_key: Optional[str] = Field(default=None, alias="MINIO_ACCESS_KEY")
    minio_secret_key: Optional[str] = Field(default=None, alias="MINIO_SECRET_KEY")
    minio_bucket_videos: str = Field(
        default="trip-recordings", alias="MINIO_BUCKET_VIDEOS"
    )
    minio_bucket_kyc: str = Field(default="kyc-documents", alias="MINIO_BUCKET_KYC")

    # Configuration AES Master Key (32 bytes hex)
    aes_master_key: Optional[str] = Field(default=None, alias="AES_MASTER_KEY")


# Instance globale des paramètres
settings = Settings()
