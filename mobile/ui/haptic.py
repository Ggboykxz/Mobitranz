from plyer import vibrator
from kivy.utils import platform


class Haptic:
    @staticmethod
    def light():
        if platform == 'android':
            try:
                vibrator.vibrate(0.02)
            except Exception:
                pass

    @staticmethod
    def medium():
        if platform == 'android':
            try:
                vibrator.vibrate(0.05)
            except Exception:
                pass

    @staticmethod
    def heavy():
        if platform == 'android':
            try:
                vibrator.vibrate(0.1)
            except Exception:
                pass

    @staticmethod
    def selection():
        if platform == 'android':
            try:
                vibrator.vibrate(0.03)
            except Exception:
                pass
