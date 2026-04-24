# ============================================================
# Écran d'Attente Véhicule
# Fichier : vehicle_device/screens/idle_screen.py
# Description : Écran attente (revenus du jour, connexion)
# ============================================================

import tkinter as tk
from tkinter import ttk


class IdleScreen:
    """Écran d'attente de l'interface véhicule.
    
    Affiche les revenus du jour et le statut de connexion.
    """
    
    def __init__(self, parent):
        """Initialise l'écran d'attente."""
        self.frame = ttk.Frame(parent)
        
        self.create_content()
    
    def create_content(self):
        """Crée le contenu."""
        title = ttk.Label(
            self.frame,
            text="MobiTranz Véhicule",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=50)
        
        status_frame = ttk.LabelFrame(
            self.frame,
            text="Statut",
            padding=20
        )
        status_frame.pack(pady=20)
        
        self.status_label = ttk.Label(
            status_frame,
            text="En attente",
            font=("Arial", 16)
        )
        self.status_label.pack()
        
        stats_frame = ttk.LabelFrame(
            self.frame,
            text="Revenus du jour",
            padding=20
        )
        stats_frame.pack(pady=20)
        
        self.revenue_label = ttk.Label(
            stats_frame,
            text="0 XAF",
            font=("Arial", 32, "bold")
        )
        self.revenue_label.pack()
    
    def get_frame(self) -> ttk.Frame:
        """Retourne le frame."""
        return self.frame


idle_screen = IdleScreen(None)