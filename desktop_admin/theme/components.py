# ============================================================
# Composants CustomTkinter — Fluent Design Windows 11
# Fichier : desktop_admin/theme/components.py
# Description : Bibliothèque de composants réutilisables
# ============================================================

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter
import threading
import time

# Configuration globale CustomTkinter
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


# ============================================================
# COMPOSANT : CARTE FLUENT
# ============================================================
class FluentCard(ctk.CTkFrame):
    """Carte avec élévation et coins arrondis — style Windows 11.
    
    Implémente un effet de révélation au survol (Reveal Highlight)
    et une ombre douce (Fluent Elevation Level 2).
    """
    
    def __init__(self, master, title=None, padding=20, hover_effect=True, **kwargs):
        kwargs.setdefault("corner_radius", 12)
        kwargs.setdefault("fg_color", ("white", "#2C2C2C"))
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", ("#E5E5E5", "#3D3D3D"))
        super().__init__(master, **kwargs)
        
        self._padding = padding
        self._hover_effect = hover_effect
        self._original_border = kwargs.get("border_color", ("#E5E5E5", "#3D3D3D"))
        
        # Titre optionnel de la carte
        if title:
            self._title_label = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(family="Segoe UI Variable Display", size=14, weight="bold"),
                text_color=("#1A1A1A", "#FFFFFF"),
                anchor="w"
            )
            self._title_label.pack(anchor="w", padx=padding, pady=(padding, 0))
        
        # Bind hover events pour Reveal Highlight
        if hover_effect:
            self.bind("<Enter>", self._on_hover_enter)
            self.bind("<Leave>", self._on_hover_leave)
    
    def _on_hover_enter(self, event):
        """Active l'effet Reveal Highlight au survol."""
        self.configure(border_color=("#1A3A6C", "#5B85CC"))
    
    def _on_hover_leave(self, event):
        """Désactive l'effet Reveal Highlight."""
        self.configure(border_color=self._original_border)


# ============================================================
# COMPOSANT : BOUTON FLUENT PRIMAIRE
# ============================================================
class FluentButton(ctk.CTkButton):
    """Bouton primaire style Windows 11 avec animation de chargement.
    
    Supporte l'état de chargement (spinner intégré) et les variantes.
    """
    
    VARIANTS = {
        "primary":   {"fg_color": ("#1A3A6C", "#3B5EA8"), "hover_color": ("#142E57", "#2E5CB8"), "text_color": "white"},
        "secondary": {"fg_color": ("white", "#3D3D3D"), "hover_color": ("#F5F5F5", "#4A4A4A"), "text_color": ("#1A1A1A", "white"), "border_width": 1, "border_color": ("#E5E5E5", "#5A5A5A")},
        "ghost":     {"fg_color": "transparent", "hover_color": ("#F0F0F0", "#FFFFFF"), "text_color": ("#1A3A6C", "#A8C4E8")},
        "danger":    {"fg_color": ("#E53E3E", "#C53030"), "hover_color": ("#C53030", "#9B2C2C"), "text_color": "white"},
        "success":   {"fg_color": ("#009E60", "#007A4A"), "hover_color": ("#007A4A", "#006B41"), "text_color": "white"},
        "warning":   {"fg_color": ("#FCD116", "#E6BC00"), "hover_color": ("#E6BC00", "#C9A400"), "text_color": "#1A1A1A"},
    }
    
    def __init__(self, master, text="", variant="primary", loading=False, icon=None, **kwargs):
        style = self.VARIANTS.get(variant, self.VARIANTS["primary"]).copy()
        
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("height", 38)
        kwargs.setdefault("font", ctk.CTkFont(family="Segoe UI Variable Text", size=14, weight="bold"))
        
        for key, val in style.items():
            kwargs.setdefault(key, val)
        
        self._original_text = text
        self._loading = loading
        self._loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._loading_idx = 0
        
        super().__init__(master, text=text if not loading else "⠋  Chargement...", **kwargs)
        
        if loading:
            self._start_loading_animation()
    
    def set_loading(self, is_loading: bool):
        """Active/désactive l'animation de chargement."""
        self._loading = is_loading
        if is_loading:
            self.configure(state="disabled")
            self._start_loading_animation()
        else:
            self.configure(state="normal", text=self._original_text)
    
    def _start_loading_animation(self):
        """Lance l'animation spinner dans un thread séparé."""
        def animate():
            while self._loading:
                char = self._loading_chars[self._loading_idx % len(self._loading_chars)]
                try:
                    self.configure(text=f"{char}  Chargement...")
                except Exception:
                    break
                self._loading_idx += 1
                time.sleep(0.08)
        threading.Thread(target=animate, daemon=True).start()


# ============================================================
# COMPOSANT : CHAMP DE SAISIE FLUENT
# ============================================================
class FluentEntry(ctk.CTkFrame):
    """Champ de saisie avec label flottant et validation visuelle.
    
    Implémente le pattern "Floating Label" avec animation,
    indication d'état (normal/focus/error/success).
    """
    
    def __init__(self, master, label="", placeholder="", field_type="text",
                 required=False, helper_text="", **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        
        self._label_text  = label + (" *" if required else "")
        self._field_type  = field_type
        self._state_color = {
            "normal":  ("#E5E5E5", "#5A5A5A"),
            "focus":   ("#1A3A6C", "#5B85CC"),
            "error":   ("#E53E3E", "#FC8181"),
            "success": ("#009E60", "#4DC882"),
        }
        
        # Label au-dessus du champ
        self._label = ctk.CTkLabel(
            self,
            text=self._label_text,
            font=ctk.CTkFont(family="Segoe UI Variable Text", size=12),
            text_color=("#5C5C5C", "#ABABAB"),
            anchor="w"
        )
        self._label.pack(fill="x", pady=(0, 4))
        
        # Conteneur du champ avec bordure custom
        self._entry_frame = ctk.CTkFrame(
            self,
            corner_radius=8,
            border_width=1,
            border_color=self._state_color["normal"],
            fg_color=("white", "#2C2C2C"),
            height=42
        )
        self._entry_frame.pack(fill="x")
        self._entry_frame.pack_propagate(False)
        
        # Champ de saisie réel
        show_char = "●" if field_type == "password" else ""
        self._entry = ctk.CTkEntry(
            self._entry_frame,
            placeholder_text=placeholder,
            border_width=0,
            corner_radius=8,
            fg_color="transparent",
            show=show_char,
            font=ctk.CTkFont(family="Segoe UI Variable Text", size=14),
            text_color=("#1A1A1A", "#FFFFFF"),
            placeholder_text_color=("#9A9A9A", "#6D6D6D"),
        )
        self._entry.pack(fill="both", expand=True, padx=12, pady=2)
        
        # Message d'aide / erreur
        self._helper = ctk.CTkLabel(
            self,
            text=helper_text,
            font=ctk.CTkFont(family="Segoe UI Variable Text", size=11),
            text_color=("#9A9A9A", "#6D6D6D"),
            anchor="w"
        )
        if helper_text:
            self._helper.pack(fill="x", pady=(4, 0))
        
        # Bind focus events
        self._entry.bind("<FocusIn>",  self._on_focus)
        self._entry.bind("<FocusOut>", self._on_blur)
    
    def _on_focus(self, event):
        """Effet focus : bordure bleue + label coloré."""
        self._entry_frame.configure(border_color=self._state_color["focus"])
        self._label.configure(text_color=("#1A3A6C", "#5B85CC"))
    
    def _on_blur(self, event):
        """Retour à l'état normal au blur."""
        self._entry_frame.configure(border_color=self._state_color["normal"])
        self._label.configure(text_color=("#5C5C5C", "#ABABAB"))
    
    def set_error(self, message: str):
        """Affiche l'état d'erreur avec message."""
        self._entry_frame.configure(border_color=self._state_color["error"])
        self._helper.configure(text=f"⚠ {message}", text_color=("#E53E3E", "#FC8181"))
        self._helper.pack(fill="x", pady=(4, 0))
    
    def set_success(self, message: str = ""):
        """Affiche l'état de succès."""
        self._entry_frame.configure(border_color=self._state_color["success"])
        if message:
            self._helper.configure(text=f"✓ {message}", text_color=("#009E60", "#4DC882"))
    
    def get(self) -> str:
        """Retourne la valeur du champ."""
        return self._entry.get()
    
    def set(self, value: str):
        """Définit la valeur du champ."""
        self._entry.delete(0, "end")
        self._entry.insert(0, value)


# ============================================================
# COMPOSANT : KPI CARD
# ============================================================
class KPICard(ctk.CTkFrame):
    """Carte KPI animée avec tendance — style Windows 11 dashboard.
    
    Affiche une métrique principale avec son titre, icône, valeur,
    et indicateur de tendance (hausse/baisse/stable).
    """
    
    def __init__(self, master, title="", value="0", unit="", trend=None,
                 icon="📊", accent_color=None, **kwargs):
        kwargs.setdefault("corner_radius", 16)
        kwargs.setdefault("fg_color", ("white", "#2C2C2C"))
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", ("#E5E5E5", "#3D3D3D"))
        super().__init__(master, **kwargs)
        
        accent = accent_color or "#1A3A6C"
        
        # Ligne 1 : Icône + Titre
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        icon_badge = ctk.CTkLabel(
            top_frame,
            text=icon,
            font=ctk.CTkFont(size=20),
            width=44, height=44,
            fg_color=accent,
            corner_radius=12,
        )
        icon_badge.pack(side="left")
        
        ctk.CTkLabel(
            top_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI Variable Text", size=12),
            text_color=("#6B7280", "#9CA3AF"),
            anchor="w"
        ).pack(side="left", padx=(12, 0))
        
        # Ligne 2 : Valeur principale
        value_frame = ctk.CTkFrame(self, fg_color="transparent")
        value_frame.pack(fill="x", padx=20, pady=(12, 0))
        
        self._value_label = ctk.CTkLabel(
            value_frame,
            text=value,
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=32, weight="bold"),
            text_color=("#1A1A1A", "#FFFFFF"),
            anchor="w"
        )
        self._value_label.pack(side="left")
        
        if unit:
            ctk.CTkLabel(
                value_frame,
                text=f" {unit}",
                font=ctk.CTkFont(family="Segoe UI Variable Text", size=14),
                text_color=("#9A9A9A", "#6D6D6D"),
            ).pack(side="left", anchor="s", pady=(0, 6))
        
        # Ligne 3 : Tendance
        if trend is not None:
            trend_frame = ctk.CTkFrame(self, fg_color="transparent")
            trend_frame.pack(fill="x", padx=20, pady=(8, 20))
            
            if trend > 0:
                t_color = ("#009E60", "#4DC882")
                t_text = f"↑ +{trend}%"
                t_bg = ("#E6F8EF", "#1A4A2E")
            elif trend < 0:
                t_color = ("#E53E3E", "#FC8181")
                t_text = f"↓ {trend}%"
                t_bg = ("#FEF2F2", "#4A1A1A")
            else:
                t_color = ("#6B7280", "#9CA3AF")
                t_text = "→ Stable"
                t_bg = ("#F3F4F6", "#374151")
            
            trend_badge = ctk.CTkLabel(
                trend_frame,
                text=t_text,
                font=ctk.CTkFont(family="Segoe UI Variable Text", size=12, weight="bold"),
                text_color=t_color,
                fg_color=t_bg,
                corner_radius=6,
                padx=8, pady=3
            )
            trend_badge.pack(side="left")
            
            ctk.CTkLabel(
                trend_frame,
                text=" vs hier",
                font=ctk.CTkFont(size=11),
                text_color=("#9A9A9A", "#6D6D6D"),
            ).pack(side="left")
        else:
            ctk.CTkFrame(self, fg_color="transparent", height=20).pack()
    
    def update_value(self, new_value: str):
        """Met à jour la valeur affichée."""
        self._value_label.configure(text=new_value)


# ============================================================
# COMPOSANT : SIDEBAR ACRYLIC
# ============================================================
class FluentSidebar(ctk.CTkFrame):
    """Sidebar navigation avec effet Acrylic Windows 11.
    
    Navigation principale avec logo, items cliquables avec indicateur actif.
    """
    
    def __init__(self, master, items=None, logo_text="MobiTranz", collapsed=False, **kwargs):
        kwargs.setdefault("fg_color", ("#E8EEF9", "#1A2844"))
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("border_width", 0)
        super().__init__(master, **kwargs)
        
        self._items = items or []
        self._active_item = None
        self._collapsed = collapsed
        self._buttons = []
        self._width_expanded = 240
        self._width_collapsed = 64
        
        # Logo / Header
        logo_frame = ctk.CTkFrame(self, fg_color="transparent", height=72)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        
        self._toggle_btn = ctk.CTkButton(
            logo_frame,
            text="☰",
            width=40, height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=("#1A3A6C", "#FFFFFF"),
            font=ctk.CTkFont(size=18),
            text_color=("#1A3A6C", "#A8C4E8"),
            command=self._toggle_collapse
        )
        self._toggle_btn.pack(side="left", padx=12, pady=16)
        
        self._logo_label = ctk.CTkLabel(
            logo_frame,
            text=f"🚕 {logo_text}",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=16, weight="bold"),
            text_color=("#1A3A6C", "#A8C4E8"),
        )
        if not collapsed:
            self._logo_label.pack(side="left")
        
        # Divider sous le logo
        ctk.CTkFrame(self, height=1, fg_color=("#D0D8F0", "#2A3A5C")).pack(fill="x", padx=12)
        
        # Items de navigation
        self._nav_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=("#E5E5E5", "#5A5A5A"),
        )
        self._nav_frame.pack(fill="both", expand=True, pady=8)
        
        for icon, label, callback in self._items:
            self._add_nav_item(icon, label, callback)
    
    def _add_nav_item(self, icon: str, label: str, callback):
        """Ajoute un item de navigation avec effet de survol."""
        btn = ctk.CTkButton(
            self._nav_frame,
            text=f"  {icon}   {label}" if not self._collapsed else f"  {icon}",
            anchor="w",
            height=44,
            corner_radius=10,
            fg_color="transparent",
            hover_color=("#1A3A6C", "#FFFFFF"),
            font=ctk.CTkFont(family="Segoe UI Variable Text", size=14),
            text_color=("#1A3A6C", "#A8C4E8"),
            command=lambda l=label, c=callback: self._on_item_click(l, c)
        )
        btn.pack(fill="x", padx=8, pady=2)
        btn.icon = icon
        btn.label_text = label
        self._buttons.append(btn)
        return btn
    
    def _on_item_click(self, label: str, callback):
        """Gère le clic sur un item."""
        for btn in self._buttons:
            btn.configure(fg_color="transparent")
        
        for btn in self._buttons:
            if btn.label_text == label:
                btn.configure(fg_color=("#1A3A6C", "#FFFFFF"))
                self._active_item = label
        
        if callback:
            callback()
    
    def _toggle_collapse(self):
        """Toggle le mode effondré/étendu."""
        self._collapsed = not self._collapsed
        new_width = self._width_collapsed if self._collapsed else self._width_expanded
        
        for btn in self._buttons:
            new_text = f"  {btn.icon}" if self._collapsed else f"  {btn.icon}   {btn.label_text}"
            btn.configure(text=new_text)
        
        if self._collapsed:
            self._logo_label.pack_forget()
        else:
            self._logo_label.pack(side="left")
        
        self.configure(width=new_width)
    
    def set_active(self, label: str):
        """Active programmatiquement un item."""
        self._on_item_click(label, None)