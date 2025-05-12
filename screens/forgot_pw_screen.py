from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import Clock
from kivymd.app import MDApp
import requests

from normalize_phone import normalize_phone


class ForgotPasswordScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def send_reset_code(self):
        phone = self.ids.phone_input.text.strip()

        if not phone:
            toast("Please enter your phone number")
            return

        phone = normalize_phone(phone)

        try:
            response = requests.post("http://127.0.0.1:5000/send-sms-reset", json={
                "phone": phone,
            })
            data = response.json()
            toast(data.get("message", "Code sent!"))

            if response.status_code == 200:
                reset_screen = self.manager.get_screen("reset_pw")
                reset_screen.ids.phone_input.text = phone
                self.manager.current = "reset_pw"

        except Exception as e:
            toast(f"Error: {str(e)}")

    def go_back(self, *args):
        self.manager.current = "login"
