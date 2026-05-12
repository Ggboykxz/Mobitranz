from kivymd.app import MDApp


class MobiTranzTheme:
    PRIMARY = "#1A3A6C"
    ACCENT = "#009E60"
    WARNING = "#FCD116"
    DANGER = "#E53E3E"
    BG = "#F7F9FC"

    @staticmethod
    def apply():
        app = MDApp.get_running_app()
        app.theme_cls.primary_palette = "Indigo"
        app.theme_cls.accent_palette = "Green"
        app.theme_cls.theme_style = "Light"
