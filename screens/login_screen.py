from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivy.properties import BooleanProperty
import requests
import os
from kivy.app import App


class LoginScreen(MDScreen):
    remember_me = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def login(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        remember = self.ids.remember_checkbox.active


        if not username or not password:
            toast("Please enter both username and password")
            return

        try:
            response = requests.post("http://127.0.0.1:5000/login", json={
                "username": username,
                "password": password,
                "remember_me": remember
            })

            data = response.json()
            message = str(data.get("message", "Login successful!"))
            self.ids.status_label.text = message

            if response.status_code == 200:
                self.ids.status_label.text_color = (0, 1, 0, 1)
                toast(message)

                token = data.get("token")
                if remember and token:
                    self.save_token(token)

                App.get_running_app().logged_in_username = username
                App.get_running_app().logged_in_egn = data.get("egn")
                App.get_running_app().logged_in_role=data.get("role")# 🛠 corrected here

                role = data.get("role")
                if role == "patient":
                    self.manager.current = "patient_dashboard"
                elif role == "doctor":
                    self.manager.current = "doctor_dashboard"
            else:
                self.ids.status_label.text_color = (1, 0, 0, 1)
                toast(message)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.ids.status_label.text = error_msg
            self.ids.status_label.text_color = (1, 0, 0, 1)
            toast(error_msg)

    def save_token(self, token):
        try:
            with open("remember_me.txt", "w") as file:
                file.write(token)
            print("Token saved for auto-login")
        except Exception as e:
            print(f" Failed to save token: {e}")

