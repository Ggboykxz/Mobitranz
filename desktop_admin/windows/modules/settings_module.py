# ============================================================
# Module Settings — Administration
# Fichier : desktop_admin/windows/modules/settings_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, FluentButton


class SettingsModule(ctk.CTkFrame):
    """Module de paramètres système."""
    
    def __init__(self, master, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="Paramètres système",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=("#1A1A1A", "white")).pack(side="left")
        
        card = FluentCard(self, title="Configuration générale")
        card.pack(fill="x", pady=(0, 16))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        settings = [
            ("App Name", "MobiTranz"),
            ("Version", "1.0.0"),
            ("Environment", "Production"),
            ("Timezone", "Africa/Libreville"),
            ("API URL", "https://api.mobitranz.ga"),
        ]
        
        for label, value in settings:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=13),
                text_color=("#6B7280", "#9CA3AF"), width=150, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#1A1A1A", "white")).pack(side="left")
        
        card2 = FluentCard(self, title="Opérateurs de paiement")
        card2.pack(fill="x", pady=(0, 16))
        
        content2 = ctk.CTkFrame(card2, fg_color="transparent")
        content2.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        operators = [
            ("MoovMoney", "✅ Configuré"),
            ("Airtel Money", "✅ Configuré"),
            ("Firebase FCM", "⚠️ Non configuré"),
            ("Cloudinary", "⚠️ Non configuré"),
        ]
        
        for op, status in operators:
            row = ctk.CTkFrame(content2, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=op, font=ctk.CTkFont(size=13),
                text_color=("#374151", "#D1D5DB"), width=150, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=status, font=ctk.CTkFont(size=13),
                text_color=("#009E60", "#4DC882") if "✅" in status else ("#FCD116", "#E6BC00")).pack(side="left")
        
        card3 = FluentCard(self, title="Actions")
        card3.pack(fill="x")
        
        actions = ctk.CTkFrame(card3, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=20)
        
        FluentButton(actions, text="💾 Sauvegarder", variant="primary", height=40).pack(side="left", padx=(0, 8))
        FluentButton(actions, text="🔄 Recharger config", variant="secondary", height=40).pack(side="left")