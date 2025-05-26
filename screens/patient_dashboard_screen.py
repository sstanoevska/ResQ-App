from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import requests


class PatientDashboardScreen(MDScreen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load_dashboard(), 0.5)

    def load_dashboard(self):
        username = App.get_running_app().logged_in_username

        try:
            response = requests.get("https://resq-backend-iau8.onrender.com/patient-dashboard", params={
                "username": username,
            })

            data = response.json()
            if response.status_code != 200:
                MDSnackbar(MDLabel(text=data.get("message", "Error loading dashboard"),
                                   theme_text_color="Custom", text_color=(1, 0, 0, 1))).open()
                return

            self.contacts = data.get("emergency_contacts", [])
            self.patient_info = data.get("patient_info", {})

            self.show_contacts()
            self.show_patient_info()

            name = self.patient_info.get("name")
            self.ids.greeting_label.text = f" Welcome back, {name}!" if name else "Hi, User"

        except Exception as e:
            MDSnackbar(MDLabel(text=f"Error: {str(e)}",
                               theme_text_color="Custom", text_color=(1, 0, 0, 1))).open()

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

        for icon_name, label, value in fields:
            if value:
                try:
                    item_box = BoxLayout(
                        orientation="horizontal",
                        size_hint_y=None,
                        height="48dp",
                        spacing="10dp",
                        padding=("5dp", "0dp")
                    )
                    icon = MDIconButton(
                        icon=icon_name,
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1),
                        size_hint=(None, None),
                        size=("40dp", "40dp")
                    )
                    label_widget = MDLabel(
                        text=f"{label}: {value}",
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1),
                        halign="left",
                        valign="middle"
                    )
                    item_box.add_widget(icon)
                    item_box.add_widget(label_widget)
                    self.ids.patient_info_box.add_widget(item_box)
                except Exception as e:
                    print(f"❌ Error in {label}: {e}")

    def show_contacts(self):
        self.ids.contacts_list.clear_widgets()

        for contact in self.contacts:
            contact_box = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                spacing="10dp",
                padding=("5dp", "0dp")
            )

            name = contact.get("name", "Unknown")
            phone = contact.get("phone", "N/A")
            icon_name = "stethoscope" if contact.get('contact_type') == 'doctor' else "account"

            icon = MDIconButton(
                icon=icon_name,
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1),
                size_hint=(None, None),
                size=("40dp", "40dp")
            )
            contact_box.add_widget(icon)

            label = MDLabel(
                text=f"{name} - {phone}",
                shorten=True,
                max_lines=1,
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1),
                size_hint_x=0.6,
                halign="left",
                valign="middle"
            )
            contact_box.add_widget(label)

            trash = MDIconButton(
                icon="trash-can",
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1),
                size_hint=(None, None),
                size=("40dp", "40dp")
            )
            trash.bind(on_release=self.make_confirm_delete(contact))
            contact_box.add_widget(trash)

            edit = MDIconButton(
                icon="pencil",
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1),
                size_hint=(None, None),
                size=("40dp", "40dp")
            )
            edit.bind(on_release=self.make_edit_contact(contact))
            contact_box.add_widget(edit)

            self.ids.contacts_list.add_widget(contact_box)

    def make_confirm_delete(self, contact):
        def confirm_delete_wrapper(instance):
            self.confirm_delete(contact)
        return confirm_delete_wrapper

    def make_edit_contact(self, contact):
        def edit_contact_wrapper(instance):
            App.get_running_app().selected_contact_id = contact["id"]
            self.manager.current = "update_emergency_contact"
            self.manager.get_screen("update_emergency_contact").load_contact_data(contact["id"])
        return edit_contact_wrapper

    def confirm_delete(self, contact):
        self.dialog = MDDialog(
            title="Delete Contact?",
            text=f"Are you sure you want to delete {contact['name']}?",
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Delete", on_release=lambda x: self.delete_contact(contact))
            ]
        )
        self.dialog.open()

    def delete_contact(self, contact):
        self.dialog.dismiss()
        try:
            response = requests.delete("https://resq-backend-iau8.onrender.com/delete-contact", json={
                "EGN": App.get_running_app().logged_in_egn,
                "id": contact["id"],
            })
            if response.status_code == 200:
                MDSnackbar(MDLabel(text="Contact deleted!", theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()
                self.load_dashboard()
            else:
                MDSnackbar(MDLabel(text=response.json().get("message", "Failed to delete."),
                                   theme_text_color="Custom", text_color=(1, 0, 0, 1))).open()
        except Exception as e:
            MDSnackbar(MDLabel(text=f"Error: {str(e)}", theme_text_color="Custom", text_color=(1, 0, 0, 1))).open()

    def open_add_contact_popup(self):
        self.manager.get_screen("add_contact").open_add_contact_popup()

    def update_contact(self):
        pass

    def send_alert(self, alert_type):
        from kivy.clock import Clock
        app = App.get_running_app()
        egn = app.logged_in_egn

        try:
            response = requests.post("https://resq-backend-iau8.onrender.com/send-alert", json={
                "patient_egn": egn,
                "alert_type": alert_type,
            })

            data = response.json()
            if response.status_code == 200:
                if alert_type == "doctor":
                    msg = "Alert sent to your doctor."
                else:
                    msg = "Alert sent to all other emergency contacts."
            else:
                msg = data.get("message", "Failed to send alert.")

            MDSnackbar(MDLabel(
                text=msg,
                theme_text_color="Custom", text_color=(1, 1, 1, 1)
            )).open()

            self.ids.custom_alert_box.opacity = 1
            Clock.schedule_once(self.hide_custom_alert, 3)

        except Exception as e:
            MDSnackbar(MDLabel(
                text=f"Error: {str(e)}",
                theme_text_color="Custom", text_color=(1, 1, 1, 1)
            )).open()
    #         Clock.schedule_once(self.hide_custom_alert, 4)
    #
    # def hide_custom_alert(self, dt):
    #     self.ids.custom_alert_box.opacity = 0

    def verify_contact(self, contact_id, code):
        try:
            response = requests.post("https://resq-backend-iau8.onrender.com/verify-contact", json={
                "contact_id": contact_id,
                "code": code.strip()
            })
            msg = response.json().get("message", "No response.")
            MDSnackbar(MDLabel(text=msg, theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()
            if response.status_code == 200:
                self.reload_contacts()
        except Exception as e:
            MDSnackbar(MDLabel(text=f"Error: {str(e)}", theme_text_color="Custom", text_color=(1, 0, 0, 1))).open()

    def clear_message(self, dt):
        self.ids.message_label.text = ""

    def open_edit_profile_screen(self):
        self.manager.current = "edit_profile"

    def open_profile(self):
        self.manager.current = "patient_profile"

    def logout(self):
        self.manager.current = "login"
