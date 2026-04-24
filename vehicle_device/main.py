# ============================================================
# Point d'entrée Vehicle Device
# Fichier : vehicle_device/main.py
# Description : Interface embarquée véhicule (Raspberry Pi)
# ============================================================

import tkinter as tk
from tkinter import ttk

from vehicle_device.screens.idle_screen import IdleScreen


def main():
    """Point d'entrée de l'interface véhicule."""
    root = tk.Tk()
    root.title("MobiTranz Véhicule")
    root.attributes("-fullscreen", True)
    
    idle = IdleScreen(root)
    idle.get_frame().pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    main()