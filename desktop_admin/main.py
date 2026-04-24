# ============================================================
# MobiTranz Admin Desktop — Application principale CustomTkinter
# Fichier : desktop_admin/main.py
# Description : Application Windows 11 Fluent Design
# ============================================================

import customtkinter as ctk
import darkdetect
from desktop_admin.windows.login_window import LoginWindow


class MobiTranzAdminApp(ctk.CTk):
    """Application principale MobiTranz Admin.
    
    Fenêtre racine CTk avec détection automatique du thème Windows.
    Gère la navigation entre LoginWindow et MainWindow.
    """
    
    def __init__(self):
        super().__init__()
        
        # Configuration fenêtre principale
        self.title("MobiTranz — Administration")
        self.geometry("1440x900")
        self.minsize(1280, 720)
        
        # Thème automatique selon Windows
        try:
            if darkdetect.isDark():
                ctk.set_appearance_mode("dark")
            else:
                ctk.set_appearance_mode("light")
        except Exception:
            ctk.set_appearance_mode("light")
        
        # Démarrer avec l'écran de login
        self._show_login()
    
    def _show_login(self):
        """Affiche la fenêtre de connexion plein écran."""
        self._login_window = LoginWindow(self, on_success=self._on_login_success)
        self._login_window.place(relx=0, rely=0, relwidth=1, relheight=1)
    
    def _on_login_success(self, user_data: dict):
        """Callback appelé après connexion réussie."""
        self._login_window.place_forget()
        
        from desktop_admin.windows.dashboard_window import MainWindow
        self._main_window = MainWindow(self, user_data=user_data)
        self._main_window.place(relx=0, rely=0, relwidth=1, relheight=1)


def main():
    """Point d'entrée de l'application."""
    app = MobiTranzAdminApp()
    app.mainloop()


if __name__ == "__main__":
    main()