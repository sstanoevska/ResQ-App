from kivy import Config
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'vsync', '0')
Config.set('kivy', 'window', 'sdl2')



from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivy.properties import BooleanProperty
import requests
import os
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform
from os.path import join

# 🔹 Avoid circular import by defining path here
try:
    if platform == "android":
        from android.storage import app_storage_path
        base_path = app_storage_path()
    else:
        base_path = os.getcwd()
except ImportError:
    base_path = os.getcwd()

remember_file_path = join(base_path, "remember_me.txt")


class HelpContent(BoxLayout):
    pass


class LoginScreen(MDScreen):
    remember_me = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clear_fields(self):
        self.ids.username_input.text = ""
        self.ids.password_input.text = ""
        self.ids.remember_checkbox.active = False
        self.ids.status_label.text = ""

    def login(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        remember = self.ids.remember_checkbox.active

        if not username or not password:
            MDSnackbar(MDLabel(
                text="Please enter both username and password",
                theme_text_color="Custom", text_color=(1, 1, 1, 1)
            )).open()
            return

        try:
            response = requests.post("https://resq-backend-iau8.onrender.com/login", json={
                "username": username,
                "password": password,
                "remember_me": remember
            })

            data = response.json()
            message = str(data.get("message", "Login successful!"))
            self.ids.status_label.text = message

            if response.status_code == 200:
                self.ids.status_label.text_color = (0, 1, 0, 1)
                MDSnackbar(MDLabel(
                    text=message,
                    theme_text_color="Custom", text_color=(1, 1, 1, 1)
                )).open()

                token = data.get("token")
                if remember and token:
                    self.save_token(token)

                App.get_running_app().logged_in_username = username
                App.get_running_app().logged_in_egn = data.get("egn")
                App.get_running_app().logged_in_role = data.get("role")

                self.clear_fields()

                role = data.get("role")
                if role == "patient":
                    self.manager.current = "patient_dashboard"
                elif role == "doctor":
                    self.manager.current = "doctor_dashboard"
            else:
                self.ids.status_label.text_color = (1, 0, 0, 1)
                MDSnackbar(MDLabel(
                    text=message,
                    theme_text_color="Custom", text_color=(1, 0, 0, 1)
                )).open()

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.ids.status_label.text = error_msg
            self.ids.status_label.text_color = (1, 0, 0, 1)
            MDSnackbar(MDLabel(
                text=error_msg,
                theme_text_color="Custom", text_color=(1, 0, 0, 1)
            )).open()

    def save_token(self, token):
        try:
            with open(remember_file_path, "w") as file:
                file.write(token)
            print("Token saved for auto-login")
        except Exception as e:
            print(f" Failed to save token: {e}")

    help_dialog = None

    def show_help_dialog(self):
        if not self.help_dialog:
            self.help_dialog = MDDialog(
                title="[b]How to Use ResQ?[/b]",
                text=(
                    "ResQ is your emergency companion — here to help when it matters most.\n"
                    "[b]For Patients:[/b]\n\n"
                    "[b]Step 1: Create Your Profile[/b]\n"
                    "Register as a [b]patient[/b] by entering your full name, phone number, and EGN (Personal ID Number).\n"
                    "[b]Step 2: Once logged in, use the [b]Add Contact[/b] button (plus sign [+] on the right side of the dashboard) to add trusted people — your doctor, family, friends, or neighbors — who should be notified in an emergency.\n"
                    "[b]Step 3: Tap the [b]Edit Profile[/b] button (pencil icon) to update your personal information, including allergies, medications, address, and phone number.\n"
                    "[b]Step 4: Use the Panic Buttons[/b]\n"
                    "In case of emergency:\n"
                    "- Press the [b]Doctor[/b] button (red button) to alert your doctor.\n"
                    "- Press the [b]Others[/b] button (blue button) to alert all your other emergency contacts.\n"
                    "- Your emergency contacts will receive your SMS for help under the name InfoSys.\n"
                    "[b]Pro Tip:[/b] After adding a new contact, send a test alert using the buttons to make sure they receive your messages and their number is reachable.\n\n"
                    "[b]For Doctors:[/b]\n"
                    "Once registered as a [b]doctor[/b], you'll see a list of assigned patients.\n"
                    "- Use the [b]+[/b] button to assign new patients by entering their EGN. They have to be users of the app in order to be assigned.\n"
                    "- Tap the [b]Edit[/b] icon to update patient details if needed. You can also use it to see a patient's information.\n"
                    "- Use the [b]Delete[/b] icon to remove patients who are no longer under your care.\n"
                ),
                buttons=[
                    MDFlatButton(text="Got it!", on_release=lambda x: self.help_dialog.dismiss())
                ],
                size_hint=(0.9, None),
                md_bg_color=(0.8, 0.4, 0.5, 1)
            )
        self.help_dialog.open()

