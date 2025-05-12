from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivymd.toast import toast
import requests


class EditPatientInfoScreen(MDScreen):
    def on_pre_enter(self):
        patient = App.get_running_app().selected_patient
        self.ids.name_field.text = patient.get('name', '')
        self.ids.phone_field.text = patient.get('phone', '')
        self.ids.address_field.text = patient.get('address', '')
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
            res = requests.post("http://127.0.0.1:5000/edit-patient", json=data)
            if res.status_code == 200:
                toast("✅ Patient info updated.")
                self.manager.current = "doctor_dashboard"
            else:
                toast(res.json().get("message", "Update failed."))
        except Exception as e:
            toast(f"Error: {str(e)}")

    def go_back(self, *args):
        self.manager.current = "doctor_dashboard"
