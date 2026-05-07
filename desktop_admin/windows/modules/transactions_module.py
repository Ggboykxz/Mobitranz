# ============================================================
# Module Transactions — Gestion financière MobiTranz
# Fichier : desktop_admin/windows/modules/transactions_module.py
# Description : Suivi des transactions et remboursements
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, FluentButton


class TransactionsModule(ctk.CTkFrame):
    """Module de gestion des transactions."""
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._transactions = self._generate_mock_transactions()
        
        self._build_header()
        self._build_stats()
        self._build_filters()
        self._build_table()
    
    def _generate_mock_transactions(self):
        transactions = []
        methods = ["moovmoney", "airtelmoney", "card", "cash"]
        statuses = ["completed", "pending", "failed", "refunded"]
        
        for i in range(50):
            transactions.append({
                "id": f"TXN{i:08d}",
                "created_at": f"2026-05-07 {10+i%12:02d}:{i%60:02d}",
                "client": f"+24107{i:06d}",
                "driver": f"Driver {i % 15}",
                "trip_id": f"TR{i:05d}",
                "amount": [2500, 3000, 3500, 4000, 5000, 7500, 10000][i % 7],
                "method": methods[i % 4],
                "status": statuses[i % 4],
                "phone": f"+24107{i:06d}",
            })
        return transactions
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(header, text="Transactions financières",
                    font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        FluentButton(header, text="📊 Export Excel", variant="secondary").pack(side="right", padx=8)
        FluentButton(header, text="📄 Export PDF", variant="secondary").pack(side="right")
    
    def _build_stats(self):
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 16))
        
        items = [
            ("today", "2.5M", "Aujourd'hui", "#009E60"),
            ("week", "15.2M", "Cette semaine", "#1A3A6C"),
            ("month", "62.8M", "Ce mois", "#7C3AED"),
            ("failed", "125K", "Échoués", "#E53E3E"),
        ]
        
        for _, value, label, color in items:
            card = FluentCard(stats, padding=16)
            card.pack(side="left", padx=(0, 12), fill="both", expand=True)
            
            ctk.CTkLabel(card, text=f"{value} XAF", font=ctk.CTkFont(size=24, weight="bold"),
                        text_color=color).pack()
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12),
                        text_color="#6B7280").pack()
    
    def _build_filters(self):
        filters = FluentCard(self, padding=16)
        filters.pack(fill="x", pady=(0, 16))
        
        ctk.CTkEntry(filters, placeholder="Rechercher transaction...", width=250).pack(side="left", padx=(0, 16))
        ctk.CTkOptionMenu(filters, values=["Toutes méthodes", "moovmoney", "airtelmoney", "card"],
                         width=150).pack(side="left", padx=(0, 16))
        ctk.CTkOptionMenu(filters, values=["Tous statuts", "completed", "pending", "failed"],
                         width=150).pack(side="left")
        FluentButton(filters, text="Filtrer", variant="primary").pack(side="right")
    
    def _build_table(self):
        table_card = FluentCard(self, padding=0)
        table_card.pack(fill="both", expand=True)
        
        headers = ["Transaction", "Date", "Client", "Chauffeur", "Montant", "Méthode", "Statut", "Actions"]
        
        header_frame = ctk.CTkFrame(table_card, fg_color="#F5F5F5", corner_radius=0)
        header_frame.pack(fill="x")
        
        for h in headers:
            width = 130 if h == "Actions" else 140
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#6B7280", width=width).pack(side="left", padx=8, pady=12)
        
        body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        body.pack(fill="both", expand=True)
        
        method_icons = {"moovmoney": "📱", "airtelmoney": "📲", "card": "💳", "cash": "💵"}
        
        for t in self._transactions:
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x")
            
            colors = {"completed": "#009E60", "pending": "#FCD116", "failed": "#E53E3E", "refunded": "#7C3AED"}
            
            ctk.CTkLabel(row, text=t["id"], font=ctk.CTkFont(size=10, weight="bold"),
                        width=140).pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=t["created_at"], width=140, font=ctk.CTkFont(size=10)).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=t["client"], width=140).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=t["driver"], width=140).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=f"{t['amount']} XAF", font=ctk.CTkFont(weight="bold"),
                        width=140, text_color="#009E60").pack(side="left", padx=8)
            ctk.CTkLabel(row, text=f"{method_icons.get(t['method'], '')} {t['method']}", width=140).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=t["status"].upper(), fg_color=colors.get(t["status"]),
                        text_color="white", corner_radius=4, font=ctk.CTkFont(size=10, weight="bold"),
                        padx=8, pady=2).pack(side="left", padx=8)
            
            actions = ctk.CTkFrame(row, fg_color="transparent", width=130)
            actions.pack(side="left", padx=8)
            
            FluentButton(actions, text="👁️", width=28, height=24, fg_color="transparent",
                        command=lambda x=t: self._view_transaction(x)).pack(side="left", padx=2)
            
            if t["status"] == "failed":
                FluentButton(actions, text="↩️", width=28, height=24, fg_color="transparent",
                            command=lambda x=t: self._refund_transaction(x)).pack(side="left", padx=2)
    
    def _view_transaction(self, txn):
        pass
    
    def _refund_transaction(self, txn):
        txn["status"] = "refunded"
        self._build_table()


import random