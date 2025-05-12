from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.app import App
import requests

from normalize_phone import normalize_phone


class EditEmergencyContactScreen(MDScreen):

    def update_contact(self):

        name = self.ids.name_field.text.strip()
        phone = self.ids.phone_field.text.strip()
        email = self.ids.email_field.text.strip()
        contact_type = self.ids.contact_type_field.text.strip()  # Assuming a text field for contact type (doctor, other)

        contact_id = App.get_running_app().selected_contact_id  # Get the selected contact ID (passed from contact list)

        updates = {}

        if name:
            updates["name"] = name
        if phone:
            updates["phone"] = normalize_phone(phone)
        if email:
            updates["email"] = email
        if contact_type:
            updates["contact_type"] = contact_type

        if not updates:
            self.ids.message_label.text = "[b][color=ff0000]Nothing to update.[/color][/b]"
            return

        try:
            response = requests.put("http://127.0.0.1:5000/edit-emergency-contact", json={
                "contact_id": contact_id,
                **updates
            })

            if response.status_code == 200:
                self.ids.message_label.text = "[b][color=00AA00]Contact updated successfully![/color][/b]"
            else:
                self.ids.message_label.text = f"[b][color=ff0000]{response.json().get('message', 'Error updating contact')}[/color][/b]"

        except Exception as e:
            self.ids.message_label.text = f"[b][color=ff0000]Error: {str(e)}[/color][/b]"

        Clock.schedule_once(self.clear_message, 5)

    def load_contact_data(self, contact_id):
        from kivymd.toast import toast
        import requests
        from kivy.app import App

        try:
            username = App.get_running_app().logged_in_username
            response = requests.get(f"http://127.0.0.1:5000/patient-dashboard?username={username}")
            if response.status_code == 200:
                data = response.json()
                contacts = data.get("emergency_contacts", [])
                matched_contact = next((c for c in contacts if c["id"] == contact_id), None)

                if matched_contact:
                    self.ids.name_field.text = matched_contact.get("name", "")
                    self.ids.phone_field.text = matched_contact.get("phone", "")
                    self.ids.email_field.text = matched_contact.get("email", "")
                    self.ids.contact_type_field.text = matched_contact.get("contact_type", "")
                else:
                    toast("Contact not found.")
            else:
                toast("Failed to load contact data.")
        except Exception as e:
            toast(f"Error: {str(e)}")

    def clear_message(self, dt):
        self.ids.message_label.text = ""

    def go_back(self, *args):
        self.manager.current = "patient_dashboard"