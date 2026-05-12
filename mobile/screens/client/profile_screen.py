from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
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


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "profile"
        self._user_data = {}
        self._edit_dialog = None
        self._build_ui()

    def _build_ui(self):
        self.root = MDBoxLayout(orientation="vertical", md_bg_color="#F7F9FC")

        self.top_bar = MDTopAppBar(
            title="Profil",
            md_bg_color="#1A3A6C",
            specific_text_color="#FFFFFF",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
        )
        self.root.add_widget(self.top_bar)

        body = MDBoxLayout(orientation="vertical", padding=[20, 16], spacing=16)

        self.avatar_card = MDCard(
            orientation="vertical",
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            md_bg_color="#1A3A6C",
            radius=[50],
            pos_hint={"center_x": 0.5},
        )
        self.avatar_label = MDLabel(
            text="--",
            font_style="H4",
            theme_text_color="Custom",
            text_color="#FFFFFF",
            halign="center",
            valign="middle",
        )
        self.avatar_card.add_widget(self.avatar_label)
        body.add_widget(self.avatar_card)

        self.name_label = MDLabel(
            text="--",
            font_style="H5",
            theme_text_color="Primary",
            halign="center",
            size_hint_y=None,
            height=dp(32),
        )
        body.add_widget(self.name_label)

        self.phone_label = MDLabel(
            text="--",
            font_style="Body1",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(24),
        )
        body.add_widget(self.phone_label)

        self.email_label = MDLabel(
            text="--",
            font_style="Body1",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(24),
        )
        body.add_widget(self.email_label)

        self.stats_card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(80),
            padding=12,
            spacing=8,
            md_bg_color="#FFFFFF",
            radius=[12],
        )
        self.stats_container = MDBoxLayout(
            orientation="horizontal",
            spacing=8,
        )
        self.stats_card.add_widget(self.stats_container)
        body.add_widget(self.stats_card)

        menu_items = [
            ("account-edit", "Modifier le profil", self.show_edit_dialog),
            ("bell", "Notifications", self.go_to_notifications),
            ("credit-card", "Moyens de paiement", self.go_to_payment),
            ("shield-key", "Securite", self.show_security),
            ("help-circle", "Aide", self.show_help),
            ("logout", "Deconnexion", self.logout),
        ]

        for icon, label_text, action in menu_items:
            item = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(48),
                padding=[12, 8],
                spacing=12,
                md_bg_color="#FFFFFF",
                radius=[8],
                ripple_behavior=True,
            )
            ico = MDIconButton(icon=icon, icon_color="#1A3A6C", theme_icon_size="Custom", icon_size=dp(24))
            lbl = MDLabel(
                text=label_text,
                font_style="Body1",
                theme_text_color="Primary",
            )
            item.add_widget(ico)
            item.add_widget(lbl)
            item.bind(on_release=lambda x, a=action: a())
            body.add_widget(item)

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
        self.manager.current = "home"

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load_profile())

    async def load_profile(self):
        self.spinner.active = True
        try:
            data = await api_client.get("/api/v1/profile")
            self._user_data = data.get("user", data)
            Clock.schedule_once(lambda dt: self.update_ui())
        except Exception as e:
            MDSnackbar(text=f"Erreur: {str(e)}", snackbar_x=10, snackbar_y=10).open()
        finally:
            Clock.schedule_once(lambda dt: setattr(self.spinner, "active", False))

    def update_ui(self):
        user = self._user_data
        first_name = user.get("first_name", "")
        last_name = user.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip() or "Utilisateur"
        phone = user.get("phone", "--")
        email = user.get("email", "--")
        initials = f"{first_name[0] if first_name else ''}{last_name[0] if last_name else ''}" or "U"

        self.avatar_label.text = initials.upper()
        self.name_label.text = full_name
        self.phone_label.text = phone
        self.email_label.text = email

        stats = user.get("stats", user.get("statistics", {}))
        trips_count = stats.get("trips_count", stats.get("total_trips", 0))
        total_spent = stats.get("total_spent", 0)
        rating = stats.get("rating", 0)

        self.stats_container.clear_widgets()
        for label_text, value in [("Trajets", str(trips_count)), ("Depense", f"{total_spent}K"), ("Note", f"{rating}/5")]:
            col = MDBoxLayout(orientation="vertical", adaptive_size=True, pos_hint={"center_x": 0.5})
            col.add_widget(MDLabel(
                text=value,
                font_style="Subtitle1",
                theme_text_color="Custom",
                text_color="#1A3A6C",
                halign="center",
                bold=True,
            ))
            col.add_widget(MDLabel(
                text=label_text,
                font_style="Caption",
                theme_text_color="Secondary",
                halign="center",
            ))
            self.stats_container.add_widget(col)

    def show_edit_dialog(self):
        if not self._edit_dialog:
            user = self._user_data
            content = MDBoxLayout(
                orientation="vertical",
                spacing=12,
                size_hint_y=None,
                height=dp(280),
            )
            self.first_name_input = MDTextField(
                text=user.get("first_name", ""),
                hint_text="Prenom",
                mode="round",
            )
            self.last_name_input = MDTextField(
                text=user.get("last_name", ""),
                hint_text="Nom",
                mode="round",
            )
            self.email_input = MDTextField(
                text=user.get("email", ""),
                hint_text="Email",
                mode="round",
            )
            self.phone_input = MDTextField(
                text=user.get("phone", ""),
                hint_text="Telephone",
                mode="round",
            )
            content.add_widget(self.first_name_input)
            content.add_widget(self.last_name_input)
            content.add_widget(self.email_input)
            content.add_widget(self.phone_input)

            self._edit_dialog = MDDialog(
                title="Modifier le profil",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(text="ANNULER", on_release=lambda x: self._edit_dialog.dismiss()),
                    MDRaisedButton(
                        text="ENREGISTRER",
                        md_bg_color="#009E60",
                        on_release=self.save_profile,
                    ),
                ],
            )
        self._edit_dialog.open()

    def save_profile(self, instance):
        data = {
            "first_name": self.first_name_input.text,
            "last_name": self.last_name_input.text,
            "email": self.email_input.text,
            "phone": self.phone_input.text,
        }
        self._edit_dialog.dismiss()
        Clock.schedule_once(lambda dt: self.update_profile_api(data))

    async def update_profile_api(self, data):
        self.spinner.active = True
        try:
            result = await api_client.post("/api/v1/profile/update", data)
            self._user_data = result.get("user", result)
            Clock.schedule_once(lambda dt: self.update_ui())
            MDSnackbar(text="Profil mis a jour", snackbar_x=10, snackbar_y=10).open()
        except Exception as e:
            MDSnackbar(text=f"Erreur: {str(e)}", snackbar_x=10, snackbar_y=10).open()
        finally:
            Clock.schedule_once(lambda dt: setattr(self.spinner, "active", False))

    def go_to_notifications(self):
        self.manager.current = "notifications"

    def go_to_payment(self):
        self.manager.current = "payment"

    def show_security(self):
        MDSnackbar(text="Securite - fonctionnalite a venir", snackbar_x=10, snackbar_y=10).open()

    def show_help(self):
        MDSnackbar(text="Aide - Contactez le support", snackbar_x=10, snackbar_y=10).open()

    def logout(self):
        api_client._access_token = None
        self.manager.current = "login"
