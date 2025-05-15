from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivymd.app import MDApp
import requests

class ResetPasswordScreen(MDScreen):
    def reset_password(self):
        phone = self.ids.phone_input.text.strip()
        code = self.ids.code_input.text.strip()
        new_password = self.ids.new_password_input.text.strip()

        if not all([phone, code, new_password]):
            toast("Please fill in all fields.")
            return

        try:
            response = requests.post("https://resq-backend-iau8.onrender.com/reset-password-sms", json={
                "phone": phone,
                "code": code,
                "new_password": new_password
            })

            data = response.json()
            message = data.get("message", "Something went wrong.")
            toast(message)

            if data.get("success"):
                MDApp.get_running_app().change_screen("login")
            elif data.get("locked_out"):
                # Go back to login if locked out
                MDApp.get_running_app().change_screen("login")

        except Exception as e:
            toast(f"Error: {str(e)}")

    def go_back(self, *args):
        self.manager.current = "forgot_pw"
