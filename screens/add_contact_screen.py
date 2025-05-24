from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
import requests

from normalize_phone import normalize_phone


class AddContactScreen(MDScreen):
    def add_contact(self, instance):
        name = self.ids.name_input.text
        phone = self.ids.phone_input.text
        contact_type = self.ids.contact_type_input.text
        email = self.ids.email_input.text if self.ids.email_input.text else None

        phone = normalize_phone(phone)
        if not name or not phone or not contact_type:
            MDSnackbar(
                MDLabel(
                    text="Please fill in all required fields",
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1)
                )
            ).open()
            return

        user_egn = App.get_running_app().logged_in_egn
        print("[DEBUG] Raw user EGN from app:", user_egn)

        try:
            response = requests.post("https://resq-backend-iau8.onrender.com/add-emergency-contact", json={
                "user_egn": user_egn,
                "name": name,
                "phone": phone,
                "contact_type": contact_type,
                "email": email,
            })

            if response.status_code == 200:
                MDSnackbar(
                    MDLabel(
                        text=response.json().get("message", "Contact added!"),
                        theme_text_color="Custom",
                        text_color=(0, 1, 0, 1)
                    )
                ).open()
                self.manager.current = "patient_dashboard"
            else:
                MDSnackbar(
                    MDLabel(
                        text=response.json().get("message", "Failed to add contact"),
                        theme_text_color="Custom",
                        text_color=(1, 0, 0, 1)
                    )
                ).open()
        except Exception as e:
            MDSnackbar(
                MDLabel(
                    text=f"Error: {str(e)}",
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1)
                )
            ).open()

    def go_back(self, *args):
        self.manager.current = "patient_dashboard"
