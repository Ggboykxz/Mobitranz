# ============================================================
# Composant Modal Détail - Fenêtre popup détaillée
# Fichier : desktop_admin/theme/components_detail.py
# Description : Fenêtre popup pour afficher les détails complets
# ============================================================

import customtkinter as ctk
from datetime import datetime


class DetailModal(ctk.CTkToplevel):
    """Modal de détail pour afficher toutes les informations.
    
    Crée une fenêtre popup avec onglets pour chaque catégorie
    d'information détaillée.
    """
    
    def __init__(self, parent, title: str = "Détails", data: dict = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title(title)
        self.geometry("900x700")
        self.resizable(True, True)
        
        self._data = data or {}
        self._fields = []
        
        # Centrer la fenêtre
        self.transient(parent)
        self.grab_set()
        
        self._build_ui()
    
    def _build_ui(self):
        """Construit l'interface."""
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main,
            text=self._data.get("title", "Détails"),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1A1A1A", "white")
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        tabs = ctk.CTkTabview(main)
        tabs.pack(fill="both", expand=True)
        
        self._add_general_tab(tabs)
        self._add_history_tab(tabs)
        self._add_documents_tab(tabs)
        self._add_analytics_tab(tabs)
        self._add_actions_tab(tabs)
        
        close_btn = ctk.CTkButton(
            main,
            text="Fermer",
            command=self.destroy,
            width=200
        )
        close_btn.pack(pady=(20, 0))
    
    def _add_general_tab(self, tabs):
        """Onglet informations générales."""
        tab = tabs.add("Général")
        
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._add_field(scroll, "ID", self._data.get("id", "N/A"))
        self._add_field(scroll, "Statut", self._data.get("status", "N/A"))
        self._add_field(scroll, "Créé le", self._data.get("created_at", "N/A"))
        self._add_field(scroll, "Dernière activité", self._data.get("last_active", "N/A"))
        
        for key, value in self._data.items():
            if key not in ["title", "id", "status", "created_at", "last_active"]:
                if not key.startswith("_"):
                    self._add_field(scroll, key.replace("_", " ").title(), str(value))
    
    def _add_history_tab(self, tabs):
        """Onglet historique."""
        tab = tabs.add("Historique")
        
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        history = self._data.get("history", [])
        if not history:
            history = [
                {"date": "2026-05-07 10:30", "action": "Connexion", "details": "Via API"},
                {"date": "2026-05-07 09:15", "action": "Mise à jour profil", "details": "Téléphone vérifié"},
                {"date": "2026-05-06 14:20", "action": "Première connexion", "details": "Inscription validée"},
            ]
        
        for item in history:
            self._add_history_item(scroll, item)
    
    def _add_documents_tab(self, tabs):
        """Onglet documents."""
        tab = tabs.add("Documents")
        
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        docs = self._data.get("documents", [])
        if not docs:
            docs = [
                {"name": "Pièce d'identité", "status": "Vérifié", "date": "2026-05-01"},
                {"name": "Permis de conduire", "status": "En attente", "date": "2026-05-05"},
                {"name": "Photo profil", "status": "Vérifié", "date": "2026-05-01"},
            ]
        
        for doc in docs:
            self._add_document_item(scroll, doc)
    
    def _add_analytics_tab(self, tabs):
        """Onglet analytiques."""
        tab = tabs.add("Analytiques")
        
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        stats = self._data.get("stats", {})
        if not stats:
            stats = {
                "Total connexions": "45",
                "Trajets effectués": "23",
                "Dépenses totales": "125,000 XAF",
                "Note moyenne": "4.8/5",
            }
        
        for key, value in stats.items():
            self._add_field(scroll, key, value)
    
    def _add_actions_tab(self, tabs):
        """Onglet actions."""
        tab = tabs.add("Actions")
        
        actions_frame = ctk.CTkFrame(tab, fg_color="transparent")
        actions_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            actions_frame,
            text="Actions disponibles",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1A1A1A", "white")
        ).pack(anchor="w", pady=(0, 15))
        
        actions = [
            ("Modifier les informations", self._edit_info),
            ("Envoyer un message", self._send_message),
            ("Exporter les données", self._export_data),
            ("Générer un rapport PDF", self._generate_pdf),
            ("Archiver", self._archive),
            ("Supprimer", self._delete),
        ]
        
        for text, cmd in actions:
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                command=cmd,
                width=300,
                height=40
            )
            btn.pack(pady=5)
    
    def _add_field(self, parent, label: str, value: str):
        """Ajoute un champ étiquette-valeur."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            row,
            text=f"{label}:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#6B7280", "#9CA3AF"),
            width=200,
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            row,
            text=str(value),
            font=ctk.CTkFont(size=13),
            text_color=("#1A1A1A", "white"),
            anchor="w"
        ).pack(side="left")
    
    def _add_history_item(self, parent, item: dict):
        """Ajoute un élément d'historique."""
        card = ctk.CTkFrame(parent, fg_color=("#F3F4F6", "#1F2937"))
        card.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            card,
            text=item.get("date", ""),
            font=ctk.CTkFont(size=12),
            text_color=("#6B7280", "#9CA3AF")
        ).pack(anchor="w", padx=10, pady=(5, 0))
        
        ctk.CTkLabel(
            card,
            text=item.get("action", ""),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1A1A1A", "white")
        ).pack(anchor="w", padx=10)
        
        ctk.CTkLabel(
            card,
            text=item.get("details", ""),
            font=ctk.CTkFont(size=12),
            text_color=("#6B7280", "#9CA3AF")
        ).pack(anchor="w", padx=10, pady=(0, 5))
    
    def _add_document_item(self, parent, doc: dict):
        """Ajoute un document."""
        card = ctk.CTkFrame(parent, fg_color=("#F3F4F6", "#1F2937"))
        card.pack(fill="x", pady=5)
        
        name_label = ctk.CTkLabel(
            card,
            text=doc.get("name", ""),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1A1A1A", "white")
        )
        name_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        status = doc.get("status", "")
        status_color = "#22C55E" if status == "Vérifié" else "#F59E0B"
        
        ctk.CTkLabel(
            card,
            text=f"Status: {status}",
            font=ctk.CTkFont(size=12),
            text_color=status_color
        ).pack(anchor="w", padx=10)
        
        ctk.CTkLabel(
            card,
            text=f"Date: {doc.get('date', '')}",
            font=ctk.CTkFont(size=12),
            text_color=("#6B7280", "#9CA3AF")
        ).pack(anchor="w", padx=10, pady=(0, 5))
    
    def _edit_info(self):
        print("Modifier informations")
    
    def _send_message(self):
        print("Envoyer message")
    
    def _export_data(self):
        print("Exporter données")
    
    def _generate_pdf(self):
        print("Générer PDF")
    
    def _archive(self):
        print("Archiver")
    
    def _delete(self):
        print("Supprimer")


class DetailButton(ctk.CTkButton):
    """Bouton pour ouvrir les détails."""
    
    def __init__(self, parent, text: str = "Voir détails", data: dict = None, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self._data = data
        self.bind("<Button-1>", self._open_detail)
    
    def _open_detail(self, event):
        if self._data:
            DetailModal(self.winfo_toplevel(), title="Détails", data=self._data)


def show_detail(parent, title: str, data: dict):
    """Ouvre une fenêtre de détail."""
    DetailModal(parent, title=title, data=data)