# ============================================================
# UI Theme System - Design System for MobiTranz
# Fichier : desktop_admin/windows/theme/ui_theme.py
# Description : Centralized color palettes, fonts, and helpers
# ============================================================

import customtkinter as ctk
from typing import Dict, Tuple, Optional
import os


class UITheme:
    """Centralized theme management for MobiTranz CustomTkinter app."""
    
    class Palette:
        """Color palettes for light and dark modes."""
        
        LIGHT = {
            "bg": "#F8FAFC",
            "surface": "#FFFFFF",
            "surface_hover": "#F1F5F9",
            "text": "#1F2937",
            "text_secondary": "#6B7280",
            "text_muted": "#9CA3AF",
            "primary": "#1A3A6C",
            "primary_hover": "#142E57",
            "primary_light": "#3B5EA8",
            "secondary": "#6366F1",
            "success": "#10B981",
            "success_bg": "#ECFDF5",
            "warning": "#F59E0B",
            "warning_bg": "#FFFBEB",
            "danger": "#EF4444",
            "danger_bg": "#FEF2F2",
            "card_bg": "#FFFFFF",
            "card_border": "#E5E7EB",
            "input_bg": "#F9FAFB",
            "input_border": "#D1D5DB",
            "divider": "#E5E7EB",
            "overlay": "rgba(0,0,0,0.5)",
            "accent_blue": "#1A3A6C",
            "accent_green": "#10B981",
            "accent_yellow": "#FCD116",
            "accent_red": "#EF4444",
            "accent_purple": "#8B5CF6",
        }
        
        DARK = {
            "bg": "#0F111A",
            "surface": "#111827",
            "surface_hover": "#1F2937",
            "text": "#F9FAFB",
            "text_secondary": "#9CA3AF",
            "text_muted": "#6B7280",
            "primary": "#4F9CF7",
            "primary_hover": "#3B82F6",
            "primary_light": "#60A5FA",
            "secondary": "#818CF8",
            "success": "#34D399",
            "success_bg": "#064E3B",
            "warning": "#FBBF24",
            "warning_bg": "#78350F",
            "danger": "#F87171",
            "danger_bg": "#7F1D1D",
            "card_bg": "#1F2937",
            "card_border": "#374151",
            "input_bg": "#1F2937",
            "input_border": "#374151",
            "divider": "#374151",
            "overlay": "rgba(0,0,0,0.7)",
            "accent_blue": "#4F9CF7",
            "accent_green": "#34D399",
            "accent_yellow": "#FCD116",
            "accent_red": "#F87171",
            "accent_purple": "#A78BFA",
        }
    
    _appearance_mode = "Dark"
    _color_scheme = "dark-blue"
    
    @classmethod
    def get_mode(cls) -> str:
        """Get current appearance mode."""
        try:
            return ctk.get_appearance_mode()
        except Exception:
            return cls._appearance_mode
    
    @classmethod
    def set_mode(cls, mode: str):
        """Set appearance mode."""
        try:
            ctk.set_appearance_mode(mode)
            cls._appearance_mode = mode
        except Exception:
            cls._appearance_mode = mode
    
    @classmethod
    def toggle_mode(cls):
        """Toggle between light and dark mode."""
        current = cls.get_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        cls.set_mode(new_mode)
        return new_mode
    
    @classmethod
    def palette(cls) -> Dict[str, str]:
        """Get current color palette."""
        if cls.get_mode() == "Dark":
            return cls.Palette.DARK
        return cls.Palette.LIGHT
    
    @classmethod
    def colors(cls) -> Tuple[str, str]:
        """Get current (fg_color, text_color) tuple for CTk widgets."""
        p = cls.palette()
        return (p["surface"], p["text"])
    
    @classmethod
    def font(cls, size: int = 14, weight: str = "normal") -> ctk.CTkFont:
        """Get CTkFont with consistent styling."""
        return ctk.CTkFont(
            family="Segoe UI Variable Display",
            size=size,
            weight=weight,
        )
    
    @classmethod
    def title_font(cls, size: int = 24) -> ctk.CTkFont:
        """Get title font."""
        return cls.font(size, "bold")
    
    @classmethod
    def body_font(cls, size: int = 13, weight: str = "normal") -> ctk.CTkFont:
        """Get body font."""
        return cls.font(size, weight)
    
    @classmethod
    def caption_font(cls, size: int = 11) -> ctk.CTkFont:
        """Get caption font."""
        return cls.font(size)
    
    @classmethod
    def spacing(cls) -> Dict[str, int]:
        """Get standard spacing values."""
        return {
            "xs": 4,
            "sm": 8,
            "md": 12,
            "lg": 16,
            "xl": 20,
            "2xl": 24,
            "3xl": 32,
        }


class ThemeManager:
    """Manager for theme-related operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init = False
        return cls._instance
    
    def __init__(self):
        if self._init:
            return
        self._init = True
        self._theme = UITheme()
        self._apply_default_mode()
    
    def _apply_default_mode(self):
        """Apply default dark mode."""
        try:
            ctk.set_appearance_mode("Dark")
            try:
                ctk.set_default_color_theme("dark-blue")
            except Exception:
                pass
        except Exception:
            pass
    
    def get_palette(self) -> Dict[str, str]:
        """Get current color palette."""
        return self._theme.palette()
    
    def get_colors(self) -> Tuple[str, str]:
        """Get current colors for widgets."""
        return self._theme.colors()
    
    def get_font(self, size: int = 14, weight: str = "normal") -> ctk.CTkFont:
        """Get font."""
        return self._theme.font(size, weight)
    
    def toggle(self) -> str:
        """Toggle theme mode."""
        return self._theme.toggle_mode()
    
    def get_mode(self) -> str:
        """Get current mode."""
        return self._theme.get_mode()


def get_palette() -> Dict[str, str]:
    """Quick access to palette."""
    return UITheme.palette()


def colors() -> Tuple[str, str]:
    """Quick access to colors."""
    return UITheme.colors()


def font(size: int = 14, weight: str = "normal") -> ctk.CTkFont:
    """Quick access to font."""
    return UITheme.font(size, weight)


def title_font(size: int = 24) -> ctk.CTkFont:
    """Quick access to title font."""
    return UITheme.title_font(size)


def body_font(size: int = 13, weight: str = "normal") -> ctk.CTkFont:
    """Quick access to body font."""
    return UITheme.body_font(size, weight)


def spacing() -> Dict[str, int]:
    """Quick access to spacing."""
    return UITheme.spacing()


def themed_color(key: str) -> str:
    """Get themed color by key."""
    return get_palette().get(key, "#000000")


def init_theme():
    """Initialize theme manager."""
    return ThemeManager()