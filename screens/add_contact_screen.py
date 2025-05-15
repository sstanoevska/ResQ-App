from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivymd.toast import toast
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
            toast("Please fill in all required fields")
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
                toast(response.json().get("message", "Contact added!"))
                self.manager.current = "patient_dashboard"
            else:
                toast(response.json().get("message", "Failed to add contact"))
        except Exception as e:
            toast(f"Error: {str(e)}")


    def go_back(self, *args):
        self.manager.current = "patient_dashboard"

