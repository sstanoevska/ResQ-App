from kivymd.icon_definitions import md_icons
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

from kivy.utils import platform
from os.path import join
from config import remember_file_path


ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FONT_PATH = os.path.join(ASSETS_DIR, "Quintessential-Regular.ttf")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo1.png")


class ResQApp(MDApp):
    def build(self):
        from kivymd.icon_definitions import md_icons
        from kivymd.font_definitions import theme_font_styles
        self.title = "ResQ App"
        self.theme_cls.primary_palette = "Slategrey"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.font_styles.update(theme_font_styles)

        self.selected_contact_id = None
        self.logged_in_username = None
        self.lang = "en"

        # Load all KV files
        Builder.load_file(os.path.join("UI", "login.kv"))
        Builder.load_file(os.path.join("UI", "register.kv"))
        Builder.load_file(os.path.join("UI", "forgot_pw.kv"))
        Builder.load_file(os.path.join("UI", "patient_dashboard.kv"))
        Builder.load_file(os.path.join("UI", "add_contact.kv"))
        Builder.load_file(os.path.join("UI", "edit_profile.kv"))
        Builder.load_file(os.path.join("UI", "reset_pw.kv"))
        Builder.load_file(os.path.join("UI", "update_contacts.kv"))
        Builder.load_file(os.path.join("UI", "doctor_dashboard.kv"))
        Builder.load_file(os.path.join("UI", "edit_patient.kv"))

        self.sm = MDScreenManager()
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(RegisterScreen(name="register"))
        self.sm.add_widget(ForgotPasswordScreen(name="forgot_pw"))
        self.sm.add_widget(PatientDashboardScreen(name="patient_dashboard"))
        self.sm.add_widget(AddContactScreen(name="add_contact"))
        self.sm.add_widget(EditProfileScreen(name="edit_profile"))
        self.sm.add_widget(ResetPasswordScreen(name="reset_pw"))
        self.sm.add_widget(EditEmergencyContactScreen(name="update_emergency_contact"))
        self.sm.add_widget(DoctorDashboardScreen(name="doctor_dashboard"))
        self.sm.add_widget(EditPatientInfoScreen(name="edit_patient_info"))

        # Always start at login screen while debugging
        self.sm.current = "login"

        return self.sm

    # Temporarily disabled auto-login to avoid redirect crash
    # def on_start(self):
    #     role = self.try_auto_login()
    #     if role == "patient":
    #         self.sm.current = "patient_dashboard"
    #     elif role == "doctor":
    #         self.sm.current = "doctor_dashboard"
    #     else:
    #         self.sm.current = "login"

    def try_auto_login(self):
        if os.path.exists(remember_file_path):
            with open(remember_file_path, "r") as file:
                token = file.read().strip()
                try:
                    import certifi
                    response = requests.post(
                        "https://resq-backend-iau8.onrender.com/auto-login",
                        json={"token": token},
                        verify=certifi.where()
                    )
                    if response.status_code == 200:
                        data = response.json()
                        self.logged_in_username = data.get("username")
                        self.logged_in_egn = data.get("EGN")
                        self.logged_in_role = data.get("role")
                        return data.get("role")
                except Exception as e:
                    print("Auto-login failed:", e)
        return None

    def change_screen(self, screen_name):
        self.sm.current = screen_name

    def get_font_path(self):
        return FONT_PATH

    def get_logo_path(self):
        return LOGO_PATH


if __name__ == '__main__':
    ResQApp().run()
