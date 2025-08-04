

from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
import requests

from normalize_phone import normalize_phone
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
from datetime import datetime, timedelta
import os
try:
    if platform == "android":
        from android.storage import app_storage_path
        base_path = app_storage_path()
    else:
        base_path = os.getcwd()
except ImportError:
    base_path = os.getcwd()

remember_file_path = os.path.join(base_path, "user_data.json")

class ForgotPasswordScreen(MDScreen):
    try_remaining = 2
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_reset_code(self):
        store = JsonStore(remember_file_path)
        if store.exists('too_many_attempts'):
            time = store.get('too_many_attempts')['time']
            stored_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            now=datetime.now()
            if now < stored_time:
                print("Too early, wait until:", stored_time)
                MDSnackbar(
                    MDLabel(
                        text=f"Error: Too early, wait until: {stored_time}!",
                        theme_text_color="Custom",
                        text_color=(1, 0, 0, 1)
                    )
                ).open()
                self.manager.current = 'login'
                return  # or handle accordingly
            else:
                store.delete('too_many_attempts')
        if self.try_remaining >= 0:
            self.try_remaining -= 1
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

                if response.status_code == 200 and data.get("message") != 'User not found!':
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
        else:
            MDSnackbar(
                MDLabel(
                    text="Error: To Many Attempts. Try again after an hour!",
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1)
                )
            ).open()
            self.try_remaining=2
            date = datetime.now() + timedelta(hours=1)
            date_str = date.strftime("%Y-%m-%d %H:%M:%S")  # convert to string
            store.put('too_many_attempts', time=date_str)
    def go_back(self, *args):
        self.manager.current = "login"
