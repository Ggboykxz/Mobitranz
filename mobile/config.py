import os

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.mobitranz.ga")
API_PREFIX = "/api/v1"
API_TIMEOUT = 30

SESSION_EXPIRY = 3600

QR_SCAN_TIMEOUT = 5

VOICE_RECORDING_DURATION = 10

MAP_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

DEFAULT_LOCATION = {"lat": 0.3921, "lon": 9.4543}
