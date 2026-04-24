# ============================================================
# Point d'entrée Mobile Kivy
# Fichier : mobile/main.py
# Description : Application Kivy principale MobiTranz
# ============================================================

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition

from mobile.screens.auth.login_screen import LoginScreen
from mobile.screens.auth.register_screen import RegisterScreen
from mobile.screens.client.home_screen import HomeScreen
from mobile.screens.client.voice_screen import VoiceScreen
from mobile.screens.client.qr_scanner_screen import QRScannerScreen
from mobile.screens.client.payment_screen import PaymentScreen
from mobile.screens.client.trip_active_screen import TripActiveScreen
from mobile.screens.client.trip_history_screen import TripHistoryScreen
from mobile.screens.client.profile_screen import ProfileScreen
from mobile.screens.driver.driver_home_screen import DriverHomeScreen
from mobile.screens.driver.trip_active_driver import TripActiveDriverScreen
from mobile.screens.driver.earnings_screen import EarningsScreen


class MobiTranzApp(App):
    """Application mobile MobiTranz."""
    
    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        
        # Auth
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        
        # Client screens
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(VoiceScreen(name="voice"))
        sm.add_widget(QRScannerScreen(name="qr_scanner"))
        sm.add_widget(PaymentScreen(name="payment"))
        sm.add_widget(TripActiveScreen(name="trip_active"))
        sm.add_widget(TripHistoryScreen(name="trip_history"))
        sm.add_widget(ProfileScreen(name="profile"))
        
        # Driver screens
        sm.add_widget(DriverHomeScreen(name="driver_home"))
        sm.add_widget(TripActiveDriverScreen(name="trip_active_driver"))
        sm.add_widget(EarningsScreen(name="earnings"))
        
        return sm


if __name__ == "__main__":
    MobiTranzApp().run()