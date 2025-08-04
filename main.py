from kivy.clock import Clock
from kivy.lang import Builder
import os
import requests
from kivy.properties import StringProperty
from kivy.uix.modalview import ModalView
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.screenmanager import MDScreenManager
#from flask import json
from kivymd.uix.snackbar import MDSnackbar

from screens.add_contact_screen import AddContactScreen
from screens.doctor_dashboard import DoctorDashboardScreen
from screens.edit_patient_info_screen import EditPatientInfoScreen
from screens.forgot_pw_screen import ForgotPasswordScreen
from screens.login_screen import LoginScreen
from screens.patient_dashboard_screen import PatientDashboardScreen
from screens.register_screen import RegisterScreen
from screens.edit_profile_screen import EditProfileScreen
from screens.reset_pw_screen import ResetPasswordScreen
from screens.splash import SplashScreen
from screens.update_emergency_contact_screen import EditEmergencyContactScreen
from screens.patient_history import PatientHistoryScreen
from kivy.utils import platform
from os.path import join
from config import remember_file_path
from kivy.core.window import Window
#Window.size=(390, 844)
from screens.visit_screen import AddVisitScreen
from kivy.storage.jsonstore import JsonStore

# Store token
store = JsonStore('user_data.json')



ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FONT_PATH = os.path.join(ASSETS_DIR, "Quintessential-Regular.ttf")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo1.png")


class Loading_View(ModalView):
    status = StringProperty('Processing...')
    kv=Builder.load_string("""<Loading_View>:
    size_hint: (None, None)
    size: dp(150), dp(150)
    auto_dismiss: False
    background_color: (0, 0, 0, 0)  # Transparent background

    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(10)
        padding: dp(10)
        size_hint: None, None
        size: dp(120), dp(120)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}

        MDSpinner:
            id: loading
            size_hint: None, None
            size: dp(46), dp(46)
            pos_hint: {'center_x': .5, 'center_y': .5}
            active: True

        Label:
            text: root.status #"Processing..."
            color: 1, 1, 1, 1  # White text
            font_size: dp(14)
            halign: "center"
    """)


class ResQApp(MDApp):
    def build(self):
        from kivymd.icon_definitions import md_icons
        from kivymd.font_definitions import theme_font_styles
        self.x, self.y=Window.size
        self.title = "ResQ App"
        self.theme_cls.primary_palette = "BlueGray"
        #self.theme_cls.theme_style = "Dark"

        self.selected_contact_id = None
        self.logged_in_username = None
        self.lang = "en"
        #store.put('auth', token=None)
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
        Builder.load_file(os.path.join("UI", "patient_history.kv"))
        Builder.load_file(os.path.join("UI", "visit.kv"))
        Builder.load_file(os.path.join("UI", "splash.kv"))

        self.sm = MDScreenManager()
        self.sm.add_widget(SplashScreen(name="splash"))
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
        self.sm.add_widget(PatientHistoryScreen(name="patient_history"))
        self.sm.add_widget(AddVisitScreen(name="visit"))


        # Always start at login screen while debugging
        self.sm.current = "splash"

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



    def change_screen(self, screen_name):
        self.sm.current = screen_name

    def get_font_path(self):
        return FONT_PATH

    def get_logo_path(self):
        return LOGO_PATH

    def show_loading(self, status, *args):
        print('open')
        self.loading = Loading_View(status=status)
        self.loading.open()

    def hide_loading(self):
        self.loading.dismiss()

    def show_snackbar(self, msg, color=(1,0,0,1)):
        def _show_snackbar(dt):  # dt is required for Clock callback
            MDSnackbar(
                MDLabel(
                    text=msg,
                    theme_text_color="Custom",
                    text_color=color
                )
            ).open()

        Clock.schedule_once(_show_snackbar)

if __name__ == '__main__':
    ResQApp().run()

