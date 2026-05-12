from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.camera import Camera
from kivy.graphics import Color, RoundedRectangle
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.topappbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from mobile.services.api_client import api_client
from mobile.ui.haptic import Haptic
from mobile.ui.ripple import RippleButton


class QRScannerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "qr_scanner"
        self._camera = None
        self._dialog = None
        self._build_ui()

    def _build_ui(self):
        self.root = MDBoxLayout(orientation="vertical", md_bg_color="#F7F9FC")

        self.top_bar = MDTopAppBar(
            title="Scanner QR Code",
            md_bg_color="#1A3A6C",
            specific_text_color="#FFFFFF",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
        )
        self.root.add_widget(self.top_bar)

        self.camera_container = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, 0.5),
            md_bg_color="#2D3748",
            padding=0,
        )

        self.camera_placeholder = MDBoxLayout(
            orientation="vertical",
            adaptive_size=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        placeholder_icon = MDIconButton(
            icon="qrcode-scan",
            icon_color="#718096",
            theme_icon_size="Custom",
            icon_size=dp(64),
            pos_hint={"center_x": 0.5},
        )
        placeholder_label = MDLabel(
            text="Cadrez le QR Code du taxi",
            font_style="Body1",
            theme_text_color="Custom",
            text_color="#A0AEC0",
            halign="center",
        )
        self.camera_placeholder.add_widget(placeholder_icon)
        self.camera_placeholder.add_widget(placeholder_label)
        self.camera_container.add_widget(self.camera_placeholder)

        self.root.add_widget(self.camera_container)

        body = MDBoxLayout(
            orientation="vertical",
            padding=[20, 16],
            spacing=16,
        )

        self.status_label = MDLabel(
            text="Appuyez sur Activer camera pour scanner",
            font_style="Body2",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(30),
        )
        body.add_widget(self.status_label)

        self.result_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            padding=12,
            spacing=8,
            md_bg_color="#EDF2F7",
            radius=[8],
            opacity=0,
        )
        self.result_label = MDLabel(
            text="",
            font_style="Body1",
            theme_text_color="Primary",
        )
        self.result_card.add_widget(self.result_label)
        body.add_widget(self.result_card)

        self.camera_btn = RippleButton(
            text="Activer camera",
            md_bg_color="#1A3A6C",
            size_hint=(1, None),
            height=dp(48),
            on_release=self.toggle_camera,
        )
        body.add_widget(self.camera_btn)

        manual_btn = MDFlatButton(
            text="Saisir manuellement le code",
            md_bg_color="#FFFFFF",
            text_color="#1A3A6C",
            size_hint=(1, None),
            height=dp(44),
            on_release=self.show_manual_dialog,
        )
        body.add_widget(manual_btn)

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={"center_x": 0.5},
            active=False,
        )
        body.add_widget(self.spinner)

        self.root.add_widget(body)
        self.add_widget(self.root)

    def go_back(self):
        self.manager.switch("home")

    def toggle_camera(self, instance):
        if self._camera:
            self.camera_container.remove_widget(self._camera)
            self._camera = None
            self.camera_placeholder.opacity = 1
            self.camera_btn.text = "Activer camera"
            self.status_label.text = "Camera desactivee"
        else:
            try:
                self._camera = Camera(
                    play=True,
                    resolution=(640, 480),
                )
                self._camera.keep_ratio = True
                self._camera.keep_data = True
                self._camera.bind(on_texture=self.on_camera_texture)
                self.camera_container.clear_widgets()
                self.camera_container.add_widget(self._camera)
                self.camera_btn.text = "Desactiver camera"
                self.status_label.text = "Cadrez le QR Code dans le cadre"
            except Exception as e:
                self.status_label.text = "Camera non disponible"
                MDSnackbar(
                    text=f"Erreur camera: {str(e)}",
                    snackbar_x=10,
                    snackbar_y=10,
                ).open()

    def on_camera_texture(self, instance, texture):
        pass

    def parse_qr_result(self, data):
        Haptic.heavy()
        self.status_label.text = "QR Code detecte !"
        self.result_label.text = f"Code: {data}"
        self.result_card.opacity = 1
        Clock.schedule_once(lambda dt: self.verify_qr_code(data))

    async def verify_qr_code(self, code):
        self.spinner.active = True
        try:
            result = await api_client.post("/api/v1/qr/verify", {"code": code})
            trip_id = result.get("trip_id")
            if trip_id:
                Haptic.heavy()
                MDSnackbar(
                    text="QR valide ! Trajet trouve.",
                    snackbar_x=10,
                    snackbar_y=10,
                ).open()
                self.manager.get_screen("trip_active").trip_id = trip_id
                Clock.schedule_once(lambda dt: self.manager.switch("trip_active"))
            else:
                Haptic.light()
                MDSnackbar(
                    text="QR invalide ou deja utilise",
                    snackbar_x=10,
                    snackbar_y=10,
                ).open()
        except Exception as e:
            MDSnackbar(
                text=f"Erreur: {str(e)}",
                snackbar_x=10,
                snackbar_y=10,
            ).open()
        finally:
            self.spinner.active = False

    def show_manual_dialog(self, instance):
        if not self._dialog:
            self._dialog = MDDialog(
                title="Saisie manuelle",
                type="custom",
                content_cls=MDBoxLayout(
                    MDTextField(
                        id="code_input",
                        hint_text="AA-001-AI",
                        helper_text="Entrez la plaque du taxi",
                        mode="round",
                    ),
                    orientation="vertical",
                    spacing=12,
                    size_hint_y=None,
                    height=dp(100),
                ),
                buttons=[
                    MDFlatButton(text="ANNULER", on_release=lambda x: self._dialog.dismiss()),
                    MDRaisedButton(
                        text="VALIDER",
                        md_bg_color="#009E60",
                        on_release=self.submit_manual_code,
                    ),
                ],
            )
        self._dialog.open()

    def submit_manual_code(self, instance):
        code_input = self._dialog.content_cls.ids.get("code_input")
        if code_input and code_input.text.strip():
            code = code_input.text.strip()
            self._dialog.dismiss()
            self.parse_qr_result(code)
