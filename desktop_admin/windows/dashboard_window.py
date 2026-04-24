# ============================================================
# Fenêtre Tableau de Bord Admin
# Fichier : desktop_admin/windows/dashboard_window.py
# Description : Fenêtre principale avec menu latéral
# ============================================================

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk


class DashboardWindow:
    """Fenêtre principale de l'interface admin MobiTranz.
    
    Affiche le tableau de bord avec KPIs et navigation.
    """
    
    def __init__(self, root):
        """Initialise le tableau de bord."""
        self.root = root
        self.root.title("MobiTranz Admin")
        self.root.geometry("1400x900")
        
        self.create_layout()
    
    def create_layout(self):
        """Crée la mise en page."""
        main_container = ttk.PanedWindow(self.root, orient=HORIZONTAL)
        main_container.pack(fill=BOTH, expand=True)
        
        sidebar = ttk.Frame(main_container, bootstyle="dark", width=250)
        main_container.add(sidebar, weight=0)
        
        self.create_sidebar(sidebar)
        
        content = ttk.Frame(main_container)
        main_container.add(content, weight=1)
        
        self.content = content
        self.show_overview()
    
    def create_sidebar(self, parent):
        """Crée le menu latéral."""
        title = ttk.Label(
            parent,
            text="MobiTranz",
            font=("Segoe UI", 20, "bold"),
            bootstyle="light",
            padding=20
        )
        title.pack(fill=X)
        
        nav_items = [
            ("Vue d'ensemble", self.show_overview),
            ("Utilisateurs", self.show_users),
            ("Conducteurs", self.show_drivers),
            ("Véhicules", self.show_vehicles),
            ("Trajets", self.show_trips),
            ("Transactions", self.show_transactions),
            ("Incidents", self.show_incidents),
            ("Vidéos", self.show_recordings),
            ("Rapports", self.show_reports),
            ("Paramètres", self.show_settings),
        ]
        
        for text, command in nav_items:
            btn = ttk.Button(
                parent,
                text=text,
                bootstyle="dark",
                command=command,
                sticky="ew"
            )
            btn.pack(fill=X, padx=10, pady=2)
    
    def clear_content(self):
        """Efface le contenu."""
        for widget in self.content.winfo_children():
            widget.destroy()
    
    def show_overview(self):
        """Affiche la vue d'ensemble."""
        self.clear_content()
        
        title = ttk.Label(
            self.content,
            text="Tableau de bord",
            font=("Segoe UI", 18),
            bootstyle="light",
            padding=20
        )
        title.pack(anchor=W)
        
        kpi_frame = ttk.Frame(self.content)
        kpi_frame.pack(fill=X, padx=20, pady=20)
        
        kpis = [
            ("Trajets du jour", "145"),
            ("transactions", "1,234,000 XAF"),
            ("Conducteurs actifs", "42"),
            ("Incidents", "2"),
        ]
        
        for title, value in kpis:
            card = ttk.LabelFrame(
                kpi_frame,
                text=title,
                bootstyle="secondary",
                padding=20
            )
            card.pack(side=LEFT, padx=10)
            
            ttk.Label(
                card,
                text=value,
                font=("Segoe UI", 18, "bold"),
                bootstyle="light"
            ).pack()
    
    def show_users(self):
        """Affiche les utilisateurs."""
        self.clear_content()
        ttk.Label(
            self.content,
            text="Gestion des utilisateurs",
            font=("Segoe UI", 18),
            bootstyle="light",
            padding=20
        ).pack(anchor=W)
    
    def show_drivers(self):
        """Affiche les conducteurs."""
        self.clear_content()
        ttk.Label(
            self.content,
            text="Gestion des conducteurs",
            font=("Segoe UI", 18),
            bootstyle="light",
            padding=20
        ).pack(anchor=W)
    
    def show_vehicles(self):
        """Affiche les véhicules."""
        self.clear_content()
        ttk.Label(
            self.content,
            text="Gestion des véhicules",
            font=("Segoe UI", 18),
            bootstyle="light",
            padding=20
        ).pack(anchor=W)
    
    def show_trips(self):
        """Affiche les trajets."""
        self.clear_content()
        ttk.Label(
            self.content,
            text="Suivi des trajets",
            font=("Segoe UI", 18),
            bootstyle="light",
            padding=20
        ).pack(anchor=W)
    
    def show_transactions(self):
        """Affiche les transactions."""
        self.clear_content()
        ttk.Label(
            self.content,
            text="Transactions",
            font=("Segoe UI", 18),
            bootstyle="light",
            padding=20
        ).pack(anchor=W)
    
    def show_incidents(self):
        """Affiche les incidents."""
        self.clear_content()
        ttk.Label(
            self.content,
            text="Incidents SOS",
            font=("Segoe UI", 18),
            bootstyle="light",
            padding=20
        ).pack(anchor=W)
    
    def show_recordings(self):
        """Affiche les enregistrements."""
        self.clear_content()
        ttk.Label(
            self.content,
            text="Vidéos",
            font=("Segoe UI", 18),
            bootstyle="light",
            padding=20
        ).pack(anchor=W)
    
    def show_reports(self):
        """Affiche les rapports."""
        self.clear_content()
        ttk.Label(
            self.content,
            text="Rapports ministériels",
            font=("Segoe UI", 18),
            bootstyle="light",
            padding=20
        ).pack(anchor=W)
    
    def show_settings(self):
        """Affiche les paramètres."""
        self.clear_content()
        ttk.Label(
            self.content,
            text="Paramètres système",
            font=("Segoe UI", 18),
            bootstyle="light",
            padding=20
        ).pack(anchor=W)