# ============================================================
# Point d'entrée Admin Desktop
# Fichier : desktop_admin/main.py
# Description : Application Tkinter/TtkBootstrap MobiTranz Admin
# ============================================================

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from desktop_admin.windows.dashboard_window import DashboardWindow
from desktop_admin.theme.style import setup_theme


def main():
    """Point d'entrée de l'application admin."""
    root = tk.Tk()
    
    setup_theme()
    
    app = DashboardWindow(root)
    
    root.mainloop()


if __name__ == "__main__":
    main()