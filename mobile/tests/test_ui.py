import pytest
from kivy.clock import Clock


class TestBaseScreen:
    def test_show_loading(self):
        from mobile.screens.base_screen import BaseScreen
        screen = BaseScreen()
        screen.show_loading()
        assert screen._loading_layout is not None
        screen.hide_loading()
        assert screen._loading_layout is None

    def test_hide_loading(self):
        from mobile.screens.base_screen import BaseScreen
        screen = BaseScreen()
        screen.show_loading()
        screen.hide_loading()
        assert screen._loading_layout is None

    def test_hide_loading_when_not_shown(self):
        from mobile.screens.base_screen import BaseScreen
        screen = BaseScreen()
        screen.hide_loading()
        assert screen._loading_layout is None

    def test_show_toast(self):
        from mobile.screens.base_screen import BaseScreen
        screen = BaseScreen()
        screen.show_toast("Test message")
        assert screen._snackbar is not None

    def test_show_error(self):
        from mobile.screens.base_screen import BaseScreen
        screen = BaseScreen()
        screen.show_error("Test error")
        assert screen._snackbar is not None

    def test_show_offline_banner(self):
        from mobile.screens.base_screen import BaseScreen
        screen = BaseScreen()
        screen.show_offline_banner()
        assert screen._offline_banner is not None
        screen.hide_offline_banner()
        assert screen._offline_banner is None


class TestLoginScreenValidation:
    def test_name_property(self):
        from mobile.screens.auth.login_screen import LoginScreen
        screen = LoginScreen()
        assert screen.name == "login"

    def test_empty_phone(self):
        from mobile.screens.auth.login_screen import LoginScreen
        screen = LoginScreen()
        screen.phone_input.text = ""
        screen.password_input.text = "password123"
        screen.do_login(None)
        assert "requis" in screen.error_label.text.lower() or screen.error_label.text != ""

    def test_empty_password(self):
        from mobile.screens.auth.login_screen import LoginScreen
        screen = LoginScreen()
        screen.phone_input.text = "+24112345678"
        screen.password_input.text = ""
        screen.do_login(None)
        assert "requis" in screen.error_label.text.lower() or screen.error_label.text != ""

    def test_both_empty(self):
        from mobile.screens.auth.login_screen import LoginScreen
        screen = LoginScreen()
        screen.phone_input.text = ""
        screen.password_input.text = ""
        screen.do_login(None)
        assert screen.error_label.text != ""

    def test_password_min_length_not_in_login(self):
        from mobile.screens.auth.login_screen import LoginScreen
        screen = LoginScreen()
        screen.phone_input.text = "+24112345678"
        screen.password_input.text = "short"
        screen.do_login(None)
        assert "requis" not in screen.error_label.text


class TestRegisterScreenValidation:
    def test_name_property(self):
        from mobile.screens.auth.register_screen import RegisterScreen
        screen = RegisterScreen()
        assert screen.name == "register"

    def test_empty_phone(self):
        from mobile.screens.auth.register_screen import RegisterScreen
        screen = RegisterScreen()
        screen.first_name_input.text = "John"
        screen.last_name_input.text = "Doe"
        screen.phone_input.text = ""
        screen.password_input.text = "password123"
        screen.confirm_password_input.text = "password123"
        screen.do_register(None)
        assert "requis" in screen.error_label.text.lower()

    def test_empty_password(self):
        from mobile.screens.auth.register_screen import RegisterScreen
        screen = RegisterScreen()
        screen.first_name_input.text = "John"
        screen.last_name_input.text = "Doe"
        screen.phone_input.text = "+24112345678"
        screen.password_input.text = ""
        screen.confirm_password_input.text = ""
        screen.do_register(None)
        assert "requis" in screen.error_label.text.lower()

    def test_short_password(self):
        from mobile.screens.auth.register_screen import RegisterScreen
        screen = RegisterScreen()
        screen.first_name_input.text = "John"
        screen.last_name_input.text = "Doe"
        screen.phone_input.text = "+24112345678"
        screen.password_input.text = "short"
        screen.confirm_password_input.text = "short"
        screen.do_register(None)
        assert "caract" in screen.error_label.text.lower() or "min" in screen.error_label.text.lower()

    def test_password_mismatch(self):
        from mobile.screens.auth.register_screen import RegisterScreen
        screen = RegisterScreen()
        screen.first_name_input.text = "John"
        screen.last_name_input.text = "Doe"
        screen.phone_input.text = "+24112345678"
        screen.password_input.text = "password123"
        screen.confirm_password_input.text = "different"
        screen.do_register(None)
        assert "diff" in screen.error_label.text.lower() or "différent" in screen.error_label.text.lower()


class TestVoiceScreen:
    def test_name_property(self):
        from mobile.screens.client.voice_screen import VoiceScreen
        screen = VoiceScreen()
        assert screen.name == "voice"

    def test_initial_not_recording(self):
        from mobile.screens.client.voice_screen import VoiceScreen
        screen = VoiceScreen()
        assert screen._is_recording is False
        assert screen.record_btn.text == "🎤  Enregistrer"
        assert screen.send_btn.disabled is True

    def test_toggle_recording_starts(self):
        from mobile.screens.client.voice_screen import VoiceScreen
        screen = VoiceScreen()
        screen.toggle_recording(None)
        assert screen._is_recording is True
        assert "Arrêter" in screen.record_btn.text

    def test_toggle_recording_stops(self):
        from mobile.screens.client.voice_screen import VoiceScreen
        screen = VoiceScreen()
        screen.toggle_recording(None)
        assert screen._is_recording is True
        screen.toggle_recording(None)
        assert screen._is_recording is False

    def test_after_recording_disabled(self):
        from mobile.screens.client.voice_screen import VoiceScreen
        screen = VoiceScreen()
        screen.toggle_recording(None)
        screen.toggle_recording(None)
        assert screen.record_btn.disabled is True

    def test_reset_state(self):
        from mobile.screens.client.voice_screen import VoiceScreen
        screen = VoiceScreen()
        screen.toggle_recording(None)
        screen.toggle_recording(None)
        screen._reset()
        assert screen._is_recording is False
        assert screen.record_btn.disabled is False
        assert screen.send_btn.disabled is True


class TestRatingScreen:
    def test_name_property(self):
        from mobile.screens.client.rating_screen import RatingScreen
        screen = RatingScreen()
        assert screen.name == "rating"

    def test_default_rating(self):
        from mobile.screens.client.rating_screen import RatingScreen
        screen = RatingScreen()
        assert screen._rating == 5

    def test_rating_1_output(self):
        from mobile.screens.client.rating_screen import RatingScreen
        screen = RatingScreen()
        screen._rating = 1
        screen._update_stars()
        assert screen._star_labels[0].text == "★"
        for i in range(1, 5):
            assert screen._star_labels[i].text == "☆"
        assert "1/5" in screen.rating_label.text

    def test_rating_2_output(self):
        from mobile.screens.client.rating_screen import RatingScreen
        screen = RatingScreen()
        screen._rating = 2
        screen._update_stars()
        assert screen._star_labels[0].text == "★"
        assert screen._star_labels[1].text == "★"
        for i in range(2, 5):
            assert screen._star_labels[i].text == "☆"
        assert "2/5" in screen.rating_label.text

    def test_rating_3_output(self):
        from mobile.screens.client.rating_screen import RatingScreen
        screen = RatingScreen()
        screen._rating = 3
        screen._update_stars()
        for i in range(3):
            assert screen._star_labels[i].text == "★"
        for i in range(3, 5):
            assert screen._star_labels[i].text == "☆"
        assert "3/5" in screen.rating_label.text

    def test_rating_4_output(self):
        from mobile.screens.client.rating_screen import RatingScreen
        screen = RatingScreen()
        screen._rating = 4
        screen._update_stars()
        for i in range(4):
            assert screen._star_labels[i].text == "★"
        assert screen._star_labels[4].text == "☆"
        assert "4/5" in screen.rating_label.text

    def test_rating_5_output(self):
        from mobile.screens.client.rating_screen import RatingScreen
        screen = RatingScreen()
        screen._rating = 5
        screen._update_stars()
        for i in range(5):
            assert screen._star_labels[i].text == "★"
        assert "5/5" in screen.rating_label.text


class TestCacheService:
    def test_set_and_get(self, cache_service):
        cache_service.set("test_key", {"foo": "bar"}, ttl=60)
        data = cache_service.get("test_key")
        assert data == {"foo": "bar"}

    def test_get_nonexistent(self, cache_service):
        data = cache_service.get("nonexistent")
        assert data is None

    def test_get_expired(self, cache_service):
        cache_service.set("test_key", "value", ttl=0)
        import time
        time.sleep(0.01)
        data = cache_service.get("test_key")
        assert data is None

    def test_clear(self, cache_service):
        cache_service.set("key1", "val1")
        cache_service.set("key2", "val2")
        cache_service.clear()
        assert cache_service.get("key1") is None
        assert cache_service.get("key2") is None

    def test_clear_expired(self, cache_service):
        cache_service.set("fresh", "fresh_val", ttl=60)
        cache_service.set("stale", "stale_val", ttl=0)
        import time
        time.sleep(0.01)
        cache_service.clear_expired()
        assert cache_service.get("fresh") == "fresh_val"
        assert cache_service.get("stale") is None

    def test_get_stale(self, cache_service):
        cache_service.set("stale_key", "stale_val", ttl=0)
        import time
        time.sleep(0.01)
        stale = cache_service.get_stale("stale_key")
        assert stale == "stale_val"
        assert cache_service.get("stale_key") is None


class TestScreenNames:
    def test_login_screen_name(self):
        from mobile.screens.auth.login_screen import LoginScreen
        screen = LoginScreen()
        assert screen.name == "login"

    def test_register_screen_name(self):
        from mobile.screens.auth.register_screen import RegisterScreen
        screen = RegisterScreen()
        assert screen.name == "register"

    def test_home_screen_name(self):
        from mobile.screens.client.home_screen import HomeScreen
        screen = HomeScreen()
        assert screen.name == "home"

    def test_voice_screen_name(self):
        from mobile.screens.client.voice_screen import VoiceScreen
        screen = VoiceScreen()
        assert screen.name == "voice"

    def test_qr_scanner_screen_name(self):
        from mobile.screens.client.qr_scanner_screen import QRScannerScreen
        screen = QRScannerScreen()
        assert screen.name == "qr_scanner"

    def test_payment_screen_name(self):
        from mobile.screens.client.payment_screen import PaymentScreen
        screen = PaymentScreen()
        assert screen.name == "payment"

    def test_trip_active_screen_name(self):
        from mobile.screens.client.trip_active_screen import TripActiveScreen
        screen = TripActiveScreen()
        assert screen.name == "trip_active"

    def test_trip_history_screen_name(self):
        from mobile.screens.client.trip_history_screen import TripHistoryScreen
        screen = TripHistoryScreen()
        assert screen.name == "trip_history"

    def test_profile_screen_name(self):
        from mobile.screens.client.profile_screen import ProfileScreen
        screen = ProfileScreen()
        assert screen.name == "profile"

    def test_chat_screen_name(self):
        from mobile.screens.client.chat_screen import ChatScreen
        screen = ChatScreen()
        assert screen.name == "chat"

    def test_rating_screen_name(self):
        from mobile.screens.client.rating_screen import RatingScreen
        screen = RatingScreen()
        assert screen.name == "rating"

    def test_notifications_screen_name(self):
        from mobile.screens.client.notifications_screen import NotificationsScreen
        screen = NotificationsScreen()
        assert screen.name == "notifications"

    def test_sos_history_screen_name(self):
        from mobile.screens.client.sos_history_screen import SOSHistoryScreen
        screen = SOSHistoryScreen()
        assert screen.name == "sos_history"

    def test_settings_screen_name(self):
        from mobile.screens.client.settings_screen import SettingsScreen
        screen = SettingsScreen()
        assert screen.name == "settings"

    def test_map_screen_name(self):
        from mobile.screens.client.map_screen import MapScreen
        screen = MapScreen()
        assert screen.name == "map"

    def test_driver_home_screen_name(self):
        from mobile.screens.driver.driver_home_screen import DriverHomeScreen
        screen = DriverHomeScreen()
        assert screen.name == "driver_home"

    def test_trip_active_driver_screen_name(self):
        from mobile.screens.driver.trip_active_driver import TripActiveDriverScreen
        screen = TripActiveDriverScreen()
        assert screen.name == "trip_active_driver"

    def test_earnings_screen_name(self):
        from mobile.screens.driver.earnings_screen import EarningsScreen
        screen = EarningsScreen()
        assert screen.name == "earnings"

    def test_wallet_screen_name(self):
        from mobile.screens.driver.wallet_screen import WalletScreen
        screen = WalletScreen()
        assert screen.name == "wallet"


class TestNavigationFlow:
    def test_login_to_home(self):
        from kivy.uix.screenmanager import ScreenManager
        from mobile.screens.auth.login_screen import LoginScreen
        from mobile.screens.client.home_screen import HomeScreen
        from mobile.screens.client.voice_screen import VoiceScreen

        sm = ScreenManager()
        login = LoginScreen(name="login")
        home = HomeScreen(name="home")
        voice = VoiceScreen(name="voice")
        sm.add_widget(login)
        sm.add_widget(home)
        sm.add_widget(voice)

        assert sm.current == "login"
        sm.current = "home"
        assert sm.current == "home"
        sm.current = "voice"
        assert sm.current == "voice"
        sm.current = "home"
        assert sm.current == "home"
