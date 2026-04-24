# ============================================================
# Système de couleurs MobiTranz — Fluent Design Windows 11
# Fichier : desktop_admin/theme/colors.py
# Description : Palette complète MobiTranz inspired by Windows 11
# ============================================================

"""
Système de couleurs MobiTranz — Fluent Design Windows 11
Inspiré du drapeau gabonais avec un langage visuel premium.
"""

# ─── COULEURS PRINCIPALES ──────────────────────────────────────────────────────
BRAND = {
    # Palette primaire (Bleu Gabon → Accent Windows 11)
    "primary_50":  "#EEF2FF",
    "primary_100": "#C7D4F0",
    "primary_200": "#94ADDE",
    "primary_300": "#5C82CA",
    "primary_400": "#2E5CB8",
    "primary_500": "#1A3A6C",
    "primary_600": "#142E57",
    "primary_700": "#0E2244",
    "primary_800": "#091630",
    "primary_900": "#040B1C",

    # Palette accent (Vert Gabon → Success/Active)
    "accent_50":   "#E6F8EF",
    "accent_300":  "#4DC882",
    "accent_500":  "#009E60",
    "accent_700":  "#006B41",

    # Palette warning (Jaune Gabon)
    "warning_50":  "#FFFAE6",
    "warning_300": "#FFDF70",
    "warning_500": "#FCD116",
    "warning_700": "#C9A400",

    # Danger
    "danger_500":  "#E53E3E",
    "danger_300":  "#FC8181",
}

# ─── THÈME CLAIR ──────────────────────────────────────────────────────────────
LIGHT = {
    # Surfaces (Mica Material)
    "bg_base":          "#F3F3F3",
    "bg_layer_1":       "#FFFFFF",
    "bg_layer_2":       "#F9F9F9",
    "bg_acrylic":       "#F0F0F0CC",
    "bg_smoke":         "#00000033",

    # Contenu
    "text_primary":     "#1A1A1A",
    "text_secondary":   "#5C5C5C",
    "text_tertiary":    "#9A9A9A",
    "text_disabled":    "#BDBDBD",

    # Bordures et dividers
    "border_light":     "#E5E5E5",
    "border_medium":    "#C8C8C8",
    "border_focus":   "#1A3A6C",

    # Contrôles
    "control_bg":       "#FFFFFF",
    "control_hover":    "#F5F5F5",
    "control_pressed":  "#EDEDED",
    "control_disabled": "#F3F3F3",

    # Sidebar (Acrylic)
    "sidebar_bg":       "#E8EEF9CC",
    "sidebar_item_hover":"#1A3A6C18",
    "sidebar_item_active":"#1A3A6C22",
    "sidebar_text":     "#1A3A6C",
}

# ─── THÈME SOMBRE ─────────────────────────────────────────────────────────────
DARK = {
    # Surfaces
    "bg_base":          "#202020",
    "bg_layer_1":       "#2C2C2C",
    "bg_layer_2":       "#383838",
    "bg_acrylic":       "#1F1F1FCC",
    "bg_smoke":         "#00000066",

    # Contenu
    "text_primary":     "#FFFFFF",
    "text_secondary":   "#ABABAB",
    "text_tertiary":    "#6D6D6D",
    "text_disabled":    "#484848",

    # Bordures
    "border_light":     "#3D3D3D",
    "border_medium":    "#5A5A5A",
    "border_focus":    "#5B85CC",

    # Contrôles
    "control_bg":       "#2C2C2C",
    "control_hover":    "#333333",
    "control_pressed": "#1F1F1F",
    "control_disabled": "#272727",

    # Sidebar
    "sidebar_bg":       "#1A2844CC",
    "sidebar_item_hover":"#FFFFFF12",
    "sidebar_item_active":"#FFFFFF1E",
    "sidebar_text":     "#A8C4E8",
}

# ─── TYPOGRAPHIE ──────────────────────────────────────────────────────────────
TYPOGRAPHY = {
    # Tailles (multiples de 2 pour la cohérence)
    "size_xs":      10,
    "size_sm":      12,
    "size_base":    14,
    "size_md":      16,
    "size_lg":      18,
    "size_xl":      24,
    "size_2xl":     32,
    "size_3xl":     40,
}

# ─── ESPACEMENTS (grille 8px) ─────────────────────────────────────────────────
SPACING = {
    "xs":   4,
    "sm":   8,
    "md":   16,
    "lg":   24,
    "xl":   32,
    "2xl":  48,
    "3xl":  64,
}

# ─── RAYONS DE COINS ─────────────────────────────────────────────────────────
RADIUS = {
    "sm":       4,
    "md":       8,
    "lg":       12,
    "xl":       16,
    "2xl":      24,
    "full":     9999,
}

# ─── OMBRES (Fluent Elevation) ────────────────────────────────────────────────
SHADOWS = {
    "sm":   "0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)",
    "md":   "0 4px 12px rgba(0,0,0,0.10), 0 2px 4px rgba(0,0,0,0.06)",
    "lg":   "0 8px 24px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.08)",
    "xl":   "0 20px 40px rgba(0,0,0,0.16), 0 8px 16px rgba(0,0,0,0.10)",
    "focus":"0 0 0 3px rgba(26,58,108,0.30)",
}

# ─── ANIMATIONS ───────────────────────────────────────────────────────────────
MOTION = {
    "duration_fast":    150,
    "duration_std":     250,
    "duration_slow":    350,
    "easing_standard":  "ease-out",
}


def get_color(key: str, theme: str = "auto") -> tuple:
    """Retourne la couleur pour le thème actuel.
    
    Args:
        key: Clé de couleur
        theme: "light", "dark" ou "auto" (détection système)
        
    Returns:
        tuple: (couleur_clair, couleur_sombre)
    """
    if theme == "auto":
        try:
            import darkdetect
            theme = darkdetect.theme().lower()
        except ImportError:
            theme = "light"
    
    return (LIGHT.get(key, "#FFFFFF"), DARK.get(key, "#FFFFFF"))