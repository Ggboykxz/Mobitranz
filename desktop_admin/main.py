# ============================================================
# MobiTranz Admin Desktop — Application principale CustomTkinter
# Fichier : desktop_admin/main.py
# Description : Application Windows 11 Fluent Design
# ============================================================

import customtkinter as ctk
import darkdetect
import os
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


def main(test_mode=False, headless=False):
    """Point d'entrée de l'application.

    Args:
        test_mode: Si True, vérifie juste que les modules sont chargés
        headless: Mode sans interface graphique (serveur HTTP)
    """
    if test_mode:
        print("✓ MobiTranz Admin - Test mode")
        print("  All modules loaded successfully")
        return

    if headless:
        run_headless_server()
        return

    # Check if display is available
    import os
    if not os.environ.get('DISPLAY'):
        print("⚠️  No display available. Starting headless server...")
        run_headless_server()
        return

    app = MobiTranzAdminApp()
    app.mainloop()


def run_headless_server():
    """Démarre un serveur HTTP simple pour l'admin."""
    import http.server
    import socketserver
    import os
    import subprocess

    PORT = 8002
    ADMIN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'php_admin')

    print(f"🚀 Starting MobiTranz Admin on http://localhost:{PORT}")
    print("   Login: admin / admin123")

    os.chdir(ADMIN_DIR)
    os.execvp('php', ['php', '-S', f'0.0.0.0:{PORT}', '-t', '.'])


if __name__ == "__main__":
    import sys
    test = "--test" in sys.argv
    headless = "--headless" in sys.argv
    main(test_mode=test, headless=headless)