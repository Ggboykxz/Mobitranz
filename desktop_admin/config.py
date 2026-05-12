# ============================================================
# Configuration Admin Desktop
# Fichier : desktop_admin/config.py
# Description : Configuration de l'application admin
# ============================================================

import os

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

SESSION_TIMEOUT = 3600

DATE_FORMAT = "%Y-%m-%d"

COLORS = {
    "primary": "#1A3A6C",
    "accent": "#009E60",
    "warning": "#FCD116",
    "danger": "#E53E3E",
    "background": "#F3F3F3",
    "surface": "#FFFFFF",
}

THEME = "light"