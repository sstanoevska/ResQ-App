from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
import requests

from normalize_phone import normalize_phone


class ForgotPasswordScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_reset_code(self):
        phone = self.ids.phone_input.text.strip()

        if not phone:
            MDSnackbar(
                MDLabel(
                    text="Please enter your phone number",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1)
                )
            ).open()
            return

        phone = normalize_phone(phone)

        try:
            response = requests.post("https://resq-backend-iau8.onrender.com/send-sms-reset", json={
                "phone": phone,
            })
            data = response.json()
            MDSnackbar(
                MDLabel(
                    text=data.get("message", "Code sent!"),
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1)
                )
            ).open()

            if response.status_code == 200:
                reset_screen = self.manager.get_screen("reset_pw")
                reset_screen.ids.phone_input.text = phone
                self.manager.current = "reset_pw"

        except Exception as e:
            MDSnackbar(
                MDLabel(
                    text=f"Error: {str(e)}",
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1)
                )
            ).open()

    def go_back(self, *args):
        self.manager.current = "login"
