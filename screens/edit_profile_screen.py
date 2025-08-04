from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.app import App
from kivymd.uix.snackbar import MDSnackbar
import requests

from normalize_phone import normalize_phone


class EditProfileScreen(MDScreen):
    def on_enter(self):
        role = App.get_running_app().logged_in_role
        address_container = self.ids.get("address_container")

        if address_container:
            if role == "doctor":
                address_container.height = 0
                address_container.opacity = 0
                address_container.disabled = True
            else:  # role is patient
                address_container.height = "70dp"
                address_container.opacity = 1
                address_container.disabled = False

    def update_profile(self):
        name = self.ids.name_field.text.strip()
        username = self.ids.username_field.text.strip()
        phone = self.ids.phone_field.text.strip()
        egn = App.get_running_app().logged_in_egn
        role = App.get_running_app().logged_in_role

        phone = normalize_phone(phone)

        updates = {}
        if name:
            updates["name"] = name
        if username:
            updates["username"] = username
        if phone:
            updates["phone"] = phone

        # Address only for patients
        if role == "patient":
            address = self.ids.address_field.text.strip()
            if address:
                updates["address"] = address

        if not updates:
            self.ids.message_label.text = "[b][color=ff0000]Nothing to update.[/color][/b]"
            return

        try:
            response = requests.put("https://resq-backend-iau8.onrender.com/edit-profile", json={
                "EGN": egn,
                **updates
            })

            if response.status_code == 200:
                self.ids.message_label.text = "[b][color=00AA00]Profile updated successfully![/color][/b]"
                Clock.schedule_once(self.refresh_dashboard, 1.5)
            else:
                self.ids.message_label.text = f"[b][color=ff0000]{response.json().get('message', 'Error updating profile')}[/color][/b]"
        except Exception as e:
            self.ids.message_label.text = f"[b][color=ff0000]Error: {str(e)}[/color][/b]"

        Clock.schedule_once(self.clear_message, 5)

    def refresh_dashboard(self, *args):
        role = App.get_running_app().logged_in_role
        if role == "doctor":
            self.manager.get_screen("doctor_dashboard").load_dashboard()
            self.manager.current = "doctor_dashboard"
        else:
            self.manager.get_screen("patient_dashboard").load_dashboard()
            self.manager.current = "patient_dashboard"

    def clear_message(self, dt):
        self.ids.message_label.text = ""

    def go_back(self, *args):
        self.refresh_dashboard()

    def on_leave(self, *args):
        self.ids.name_field.text = ''
        self.ids.username_field.text = ''
        self.ids.phone_field.text = ''
        self.ids.address_field.text = ''
