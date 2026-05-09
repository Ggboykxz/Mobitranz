# ============================================================
# Theme Mobile MobiTranz
# Fichier : mobile/theme/colors.py
# Description : Palette de couleurs MobiTranz
# ============================================================


def _hex_to_rgba(hex_color: str) -> tuple:
    """Convertit une couleur hex en tuple RGBA (0-1)."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return (r, g, b, 1)


class Colors:
    """Palette de couleurs MobiTranz.

    Inspiré du drapeau gabonais : bleu #1A3A6C, vert #009E60.
    """

    # Couleurs principales (hex pour text, RGBA pour background)
    PRIMARY = "#1A3A6C"
    PRIMARY_BG = _hex_to_rgba("#1A3A6C")
    ACCENT = "#009E60"
    ACCENT_BG = _hex_to_rgba("#009E60")
    WARNING = "#FCD116"
    DANGER = "#E53E3E"

    # Couleurs de fond
    BACKGROUND = "#F7F9FC"
    BACKGROUND_BG = _hex_to_rgba("#F7F9FC")
    SURFACE = "#FFFFFF"
    SURFACE_BG = _hex_to_rgba("#FFFFFF")
    CARD = "#FFFFFF"
    CARD_BG = _hex_to_rgba("#FFFFFF")

    # Couleurs texte
    TEXT_PRIMARY = "#1A202C"
    TEXT_SECONDARY = "#718096"
    TEXT_ON_PRIMARY = "#FFFFFF"

    # Couleurs utilitaires
    BORDER = "#E2E8F0"
    DIVIDER = "#E2E8F0"
    DISABLED = "#A0AEC0"

    # Statuts
    SUCCESS = "#009E60"
    ERROR = "#E53E3E"
    INFO = "#3182CE"

    # Grisés
    GREY_50 = "#F7FAFC"
    GREY_100 = "#EDF2F7"
    GREY_100_BG = _hex_to_rgba("#EDF2F7")
    GREY_200 = "#E2E8F0"
    GREY_300 = "#CBD5E0"
    GREY_400 = "#A0AEC0"
    GREY_500 = "#718096"
    GREY_600 = "#4A5568"
    GREY_700 = "#2D3748"
    GREY_800 = "#1A202C"
    GREY_900 = "#171923"