import hashlib

from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
import requests

class PatientDashboardScreen(MDScreen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load_dashboard(), 0.5)

    def load_dashboard(self):
        username = App.get_running_app().logged_in_username

        try:
            response = requests.get("http://127.0.0.1:5000/patient-dashboard", params={
                "username": username,
            })

            data = response.json()
            if response.status_code != 200:
                toast(data.get("message", "Error loading dashboard"))
                return

            self.contacts = data.get("emergency_contacts", [])
            self.patient_info = data.get("patient_info", {})

            print("Contacts loaded from backend:", self.contacts)  # NEW DEBUG

            self.show_contacts()
            self.show_patient_info()

            name = self.patient_info.get("name")
            if name:
                self.ids.greeting_label.text = f" Welcome back, {name}!"
                print(f"Loaded name: {name}")
            else:
                self.ids.greeting_label.text = "Hi, User"
                print("❌ No name loaded from patient_info")

        except Exception as e:
            toast(f"Error: {str(e)}")

    def load_contact_data(self, contact_id, on_success=lambda: None):
        from kivymd.toast import toast
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
                    on_success()
                else:
                    toast("Contact not found.")
            else:
                toast("Failed to load contact data.")
        except Exception as e:
            toast(f"Error: {str(e)}")

    def open_add_contact_popup(self):
        self.manager.get_screen("add_contact").open_add_contact_popup()

    def show_contacts(self):
        self.ids.contacts_list.clear_widgets()
        print("🔵 Showing contacts:", self.contacts)

        for contact in self.contacts:
            print("Adding contact:", contact)

            contact_icon = "stethoscope" if contact['contact_type'] == 'doctor' else "account"

            contact_box = BoxLayout(orientation="horizontal", size_hint_y=None, height="48dp", padding="5dp", spacing="10dp")

            avatar = IconLeftWidget(
                icon=contact_icon,
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1)  # Black icon
            )
            contact_box.add_widget(avatar)

            contact_name_label = MDLabel(
                text=f"{contact['name']} - {contact['phone']}",
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1),  # Black text
                size_hint_x=0.7  # Ensure the label takes up the majority of the space
            )
            contact_box.add_widget(contact_name_label)

            trash_icon = MDIconButton(
                icon="trash-can",
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1),  # Set trash can color
                size_hint=(None, None),
                size=("48dp", "48dp")  # Optional: Set the size of the trash icon
            )

            # Bind the trash icon to the delete contact function
            trash_icon.bind(on_release=self.make_confirm_delete(contact))

            # Add the trash icon to the contact box, aligned to the right side
            contact_box.add_widget(trash_icon)

            pencil_icon = MDIconButton(
                icon="pencil",
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1),  # Set trash can color
                size_hint=(None, None),
                size=("48dp", "48dp")  # Optional: Set the size of the trash icon
            )

            pencil_icon.bind(on_release=self.make_edit_contact(contact))

            contact_box.add_widget(pencil_icon)

            self.ids.contacts_list.add_widget(contact_box)

    def update_contact(self):
        # Get updated values from input fields
        name = self.ids.name_field.text.strip()
        phone = self.ids.phone_field.text.strip()
        email = self.ids.email_field.text.strip()
        contact_type = self.ids.contact_type_field.text.strip()

        contact_id = App.get_running_app().selected_contact_id

        updates = {}

        if name:
            updates["name"] = name
        if phone:
            updates["phone"] = phone
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

    def make_confirm_delete(self, contact):
        def confirm_delete_wrapper(instance):
            self.confirm_delete(contact)

        return confirm_delete_wrapper

    def make_edit_contact(self, contact):
        def edit_contact_wrapper(instance):
            App.get_running_app().selected_contact_id = contact["id"]

            # Switch screen first
            self.manager.current = "update_emergency_contact"

            # Load data on the correct screen
            edit_screen = self.manager.get_screen("update_emergency_contact")
            edit_screen.load_contact_data(contact["id"])

        return edit_contact_wrapper

    def show_patient_info(self):
        self.ids.patient_info_box.clear_widgets()

        fields = [
            ("account", "Name", self.patient_info.get("name")),
            ("calendar", "Date of Birth", self.patient_info.get("date_of_birth")),
            ("phone", "Phone", self.patient_info.get("phone")),
            ("map-marker", "Address", self.patient_info.get("address")),
            ("alert", "Allergies", self.patient_info.get("allergies")),
            ("clipboard-text", "Diagnosis", self.patient_info.get("diagnosis")),
            ("pill", "Medications", self.patient_info.get("medications")),
        ]
        print("Patient info loaded:", self.patient_info)

        for icon_name, label, value in fields:
            if value is not None and value != "":
                item = OneLineAvatarIconListItem(text=f"{label}: {value}")
                item.add_widget(IconLeftWidget(icon=icon_name))
                self.ids.patient_info_box.add_widget(item)

    def confirm_delete(self, contact):
        self.dialog = MDDialog(
            title="Delete Contact?",
            text=f"Are you sure you want to delete {contact['name']}?",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="Delete", on_release=lambda x: self.delete_contact(contact))
            ]
        )
        self.dialog.open()

    def delete_contact(self, contact):
        self.dialog.dismiss()  # Close the dialog after confirmation

        try:
            response = requests.delete("http://127.0.0.1:5000/delete-contact", json={
                "EGN": App.get_running_app().logged_in_egn,  # Already hashed! NO hashing again
                "id": contact["id"],
            })
            if response.status_code == 200:
                toast("Contact deleted!")
                self.load_dashboard()  # Reload the dashboard after deletion
            else:
                toast(response.json().get("message", "Failed to delete."))
        except Exception as e:
            toast(f"Error: {str(e)}")

    def send_alert(self, alert_type):
        from kivymd.toast import toast
        import requests
        from kivy.app import App

        app = App.get_running_app()
        egn = app.logged_in_egn

        data = {
            "patient_egn": egn,
            "alert_type": alert_type,
        }

        try:
            response = requests.post("http://127.0.0.1:5000/send-alert", json=data)
            msg = response.json().get("message", "Alert sent.")

            # Optional: handle if messages list is returned for 'others'
            if "messages" in response.json():
                msg = "Alert sent to all verified contacts."

            toast(msg)
        except Exception as e:
            toast(f"Error: {str(e)}")

    def verify_contact(self, contact_id, code):
        import requests
        try:
            response = requests.post("http://127.0.0.1:5000/verify-contact", json={
                "contact_id": contact_id,
                "code": code.strip()
            })
            msg = response.json().get("message", "No response.")
            from kivymd.toast import toast
            toast(msg)
            if response.status_code == 200:
                self.reload_contacts()
        except Exception as e:
            toast(f"Error: {str(e)}")


    def open_edit_profile_screen(self):
        self.manager.current = 'edit_profile'

    def logout(self):
        self.manager.current = "login"

    def open_profile(self):
        self.manager.current = "patient_profile"
