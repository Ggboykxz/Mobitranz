# ============================================================
# Theme Admin Desktop
# Fichier : desktop_admin/theme/style.py
# Description : Style ttkbootstrap customisé MobiTranz
# ============================================================

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


def setup_theme():
    """Configure le thème MobiTranz pour l'interface admin.
    
    Utilise le thème "darkly" avec les couleurs MobiTranz.
    """
    style = ttk.Style("darkly")
    
    colors = {
        "primary": "#1A3A6C",
        "accent": "#009E60",
        "warning": "#FCD116",
        "danger": "#E53E3E",
    }
    
    return style, colors


def create_kpi_card(parent, title: str, value: str) -> ttk.Frame:
    """Crée une carte KPI.
    
    Args:
        parent: Widget parent
        title: Titre du KPI
        value: Valeur du KPI
        
    Returns:
        ttk.Frame: Carte KPI
    """
    frame = ttk.Frame(parent, bootstyle="secondary", padding=20)
    
    title_label = ttk.Label(
        frame,
        text=title.upper(),
        font=("Segoe UI", 10),
        bootstyle="secondary"
    )
    
    value_label = ttk.Label(
        frame,
        text=value,
        font=("Segoe UI", 24, "bold"),
        bootstyle="light"
    )
    
    title_label.pack()
    value_label.pack()
    
    return frame