from kivy.lang import Builder
import os
import requests
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from flask import json
from screens.add_contact_screen import AddContactScreen
from screens.doctor_dashboard import DoctorDashboardScreen
from screens.edit_patient_info_screen import EditPatientInfoScreen
from screens.forgot_pw_screen import ForgotPasswordScreen
from screens.login_screen import LoginScreen
from screens.patient_dashboard_screen import PatientDashboardScreen
from screens.register_screen import RegisterScreen
from screens.edit_profile_screen import EditProfileScreen
from screens.reset_pw_screen import ResetPasswordScreen
from screens.update_emergency_contact_screen import EditEmergencyContactScreen


class ResQApp(MDApp):
    def build(self):
        self.title = "ResQ App"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Dark"
        self.selected_contact_id = None

        self.logged_in_username = None
        self.lang = "en"

        Builder.load_file(os.path.join("ui", "login.kv"))
        Builder.load_file(os.path.join("ui", "register.kv"))
        Builder.load_file(os.path.join("ui", "forgot_pw.kv"))
        Builder.load_file(os.path.join("ui", "patient_dashboard.kv"))
        Builder.load_file(os.path.join("ui", "add_contact.kv"))
        Builder.load_file(os.path.join("ui", "edit_profile.kv"))
        Builder.load_file(os.path.join("ui","reset_pw.kv"))
        Builder.load_file(os.path.join("ui","update_contacts.kv"))
        Builder.load_file(os.path.join("ui","doctor_dashboard.kv"))
        Builder.load_file(os.path.join("ui","edit_patient.kv"))

        self.sm = MDScreenManager()
        self.sm.add_widget(LoginScreen(name="login"))  # ✅ IMPORTANT
        self.sm.add_widget(RegisterScreen(name="register"))
        self.sm.add_widget(ForgotPasswordScreen(name="forgot_pw"))
        self.sm.add_widget(PatientDashboardScreen(name="patient_dashboard"))
        self.sm.add_widget(AddContactScreen(name="add_contact"))
        self.sm.add_widget(EditProfileScreen(name="edit_profile"))
        self.sm.add_widget(ResetPasswordScreen(name="reset_pw"))
        self.sm.add_widget(EditEmergencyContactScreen(name="update_emergency_contact"))
        self.sm.add_widget(DoctorDashboardScreen(name="doctor_dashboard"))
        self.sm.add_widget(EditPatientInfoScreen(name="edit_patient_info"))

        return self.sm

    def on_start(self):
        # ✅ SET SCREEN SAFELY HERE
        role = self.try_auto_login()
        if role == "patient":
            self.sm.current = "patient_dashboard"
        elif role == "doctor":
            self.sm.current = "doctor_dashboard"
        else:
            self.sm.current = "login"

    def try_auto_login(self):
        if os.path.exists("remember_me.txt"):
            with open("remember_me.txt", "r") as file:
                token = file.read().strip()
                try:
                    response = requests.post("https://resq-backend-iau8.onrender.com/auto-login", json={"token": token})
                    if response.status_code == 200:
                        data = response.json()
                        self.logged_in_username = data.get("username")
                        self.logged_in_egn = data.get("EGN")  # Needed for loading data
                        self.logged_in_role = data.get("role")
                        return data.get("role")
                except Exception as e:
                    print("Auto-login failed:", e)
        return None

    def load_translations(self):
        """Load translations from a JSON file."""
        with open("translations.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def translate(self, key):
        """Translate the key based on the current language."""
        return self.translations.get(self.lang, self.translations["en"]).get(key, key)

    def change_screen(self, screen_name):
        self.sm.current = screen_name

if __name__ == '__main__':
    ResQApp().run()
