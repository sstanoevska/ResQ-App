from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp
import requests

class ResetPasswordScreen(MDScreen):
    def reset_password(self):
        phone = self.ids.phone_input.text.strip()
        code = self.ids.code_input.text.strip()
        new_password = self.ids.new_password_input.text.strip()

        if not all([phone, code, new_password]):
            MDSnackbar(
                MDLabel(
                    text="Please fill in all fields.",
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1)
                )
            ).open()
            return

        try:
            response = requests.post("https://resq-backend-iau8.onrender.com/reset-password-sms", json={
                "phone": phone,
                "code": code,
                "new_password": new_password
            })

            data = response.json()
            message = data.get("message", "Something went wrong.")
            MDSnackbar(
                MDLabel(
                    text=message,
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1)
                )
            ).open()

            if data.get("success"):
                MDApp.get_running_app().change_screen("login")
            elif data.get("locked_out"):
                MDApp.get_running_app().change_screen("login")

        except Exception as e:
            MDSnackbar(
                MDLabel(
                    text=f"Error: {str(e)}",
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1)
                )
            ).open()

    def go_back(self, *args):
        self.manager.current = "forgot_pw"
