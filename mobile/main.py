from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from mobile.theme.theme import MobiTranzTheme
from mobile.services.auth_service import auth_service
from mobile.services.api_client import api_client

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
from mobile.screens.driver.wallet_screen import WalletScreen
from mobile.screens.client.chat_screen import ChatScreen
from mobile.screens.client.rating_screen import RatingScreen
from mobile.screens.client.notifications_screen import NotificationsScreen
from mobile.screens.client.sos_history_screen import SOSHistoryScreen
from mobile.screens.client.settings_screen import SettingsScreen
from mobile.screens.client.map_screen import MapScreen


class MobiTranzApp(MDApp):
    def build(self):
        Window.softinput_mode = "below_target"
        MobiTranzTheme.apply()

        sm = ScreenManager(transition=SlideTransition())

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))

        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(VoiceScreen(name="voice"))
        sm.add_widget(QRScannerScreen(name="qr_scanner"))
        sm.add_widget(PaymentScreen(name="payment"))
        sm.add_widget(TripActiveScreen(name="trip_active"))
        sm.add_widget(TripHistoryScreen(name="trip_history"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(ChatScreen(name="chat"))
        sm.add_widget(RatingScreen(name="rating"))
        sm.add_widget(NotificationsScreen(name="notifications"))
        sm.add_widget(SOSHistoryScreen(name="sos_history"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(MapScreen(name="map"))

        sm.add_widget(DriverHomeScreen(name="driver_home"))
        sm.add_widget(TripActiveDriverScreen(name="trip_active_driver"))
        sm.add_widget(EarningsScreen(name="earnings"))
        sm.add_widget(WalletScreen(name="wallet"))

        return sm

    def on_start(self):
        Window.bind(on_keyboard=self.on_keyboard)
        token = auth_service.get_access_token()
        if token:
            api_client.set_token(token)

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            sm = self.root
            if sm.current == "login":
                return False
            back_map = {
                "register": "login",
                "home": "login",
                "voice": "home",
                "qr_scanner": "home",
                "payment": "home",
                "trip_active": "home",
                "trip_history": "home",
                "profile": "home",
                "chat": "home",
                "rating": "home",
                "notifications": "home",
                "sos_history": "home",
                "settings": "home",
                "map": "home",
                "driver_home": "login",
                "trip_active_driver": "driver_home",
                "earnings": "driver_home",
                "wallet": "driver_home",
            }
            if sm.current in back_map:
                sm.current = back_map[sm.current]
            return True
        return False

    def on_stop(self):
        import asyncio
        try:
            asyncio.get_event_loop().run_until_complete(api_client.close())
        except Exception:
            pass


if __name__ == "__main__":
    MobiTranzApp().run()
