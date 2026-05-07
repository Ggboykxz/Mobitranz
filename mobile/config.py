# ============================================================
# Configuration Mobile MobiTranz
# Fichier : mobile/config.py
# Description : Configuration de l'application mobile
# ============================================================

API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30

REDIS_HOST = "localhost"
REDIS_PORT = 6379

SESSION_EXPIRY = 3600

QR_SCAN_TIMEOUT = 5

VOICE_RECORDING_DURATION = 10

MAP_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

DEFAULT_LOCATION = {"lat": 0.3921, "lon": 9.4543}  # Libreville

COLORS = {
    "primary": "#1A3A6C",
    "accent": "#009E60",
    "warning": "#FCD116",
    "danger": "#E53E3E",
    "background": "#F7F9FC",
    "surface": "#FFFFFF",
    "text_primary": "#1A202C",
    "text_secondary": "#718096",
}