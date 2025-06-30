from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivymd.uix.snackbar import MDSnackbar
import requests


class EditPatientInfoScreen(MDScreen):
    def on_pre_enter(self):
        patient = App.get_running_app().selected_patient
        self.ids.name_field.text = patient.get('name', '')
        self.ids.phone_field.text = str(patient.get('phone', '') or '')
        self.ids.address_field.text = str(patient.get('address', '') or '')
        self.ids.diagnosis_field.text = patient.get('diagnosis', '')
        self.ids.medications_field.text = patient.get('medications', '')
        self.ids.allergies_field.text = patient.get('allergies', '')

    def save_changes(self):
        patient = App.get_running_app().selected_patient
        data = {
            "egn": patient["EGN"],
            "name": self.ids.name_field.text,
            "phone": self.ids.phone_field.text,
            "address": self.ids.address_field.text,
            "diagnosis": self.ids.diagnosis_field.text,
            "medications": self.ids.medications_field.text,
            "allergies": self.ids.allergies_field.text,
        }

        try:
            res = requests.post("https://resq-backend-iau8.onrender.com/edit-patient", json=data)
            if res.status_code == 200:
                MDSnackbar(MDLabel(
                    text="✅ Patient info updated.",
                    theme_text_color="Custom",
                    text_color=(0, 1, 0, 1)
                )).open()
                self.manager.current = "doctor_dashboard"
            else:
                MDSnackbar(MDLabel(
                    text=res.json().get("message", "Update failed."),
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1)
                )).open()
        except Exception as e:
            MDSnackbar(MDLabel(
                text=f"Error: {str(e)}",
                theme_text_color="Custom",
                text_color=(1, 0, 0, 1)
            )).open()

    def go_back(self, *args):
        self.manager.current = "doctor_dashboard"
