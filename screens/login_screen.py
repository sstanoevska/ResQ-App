from kivy import Config
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView


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
            scroll = ScrollView(
                do_scroll_x=False,
                bar_width=5,
                size_hint=(1, None),
                size=(Window.width * 0.8, Window.height * 0.6)
            )

            help_text = (
                "ResQ is your emergency companion — here to help when it matters most.\n\n"
                "For Patients:\n"
                "1. Register as a patient with your name, phone, and EGN.\n"
                "2. Use the '+' button to add emergency contacts.\n"
                "3. Edit your profile to update medical info.\n"
                "4. Use the red button to alert your doctor, or the blue button to alert other contacts.\n"
                "Messages are sent via SMS under the name InfoSys.\n\n"
                "For Doctors:\n"
                "You can assign patients via EGN, edit their info, or remove them from your care list.\n\n"
                "Data Policy:\n"
                "If you wish to delete your profile, please contact us at support@resqapp.com.\n"
                "Your data will be permanently removed from our system within 1–3 business days.\n\n"
                "By using this app, you consent to the use of your data solely for purposes essential to the functionality of ResQ."
            )

            content = Label(
                text=help_text,
                font_size="15sp",
                size_hint_y=None,
                text_size=(Window.width * 0.8, None),
                halign="left",
                valign="top"
            )
            content.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1]))
            scroll.add_widget(content)

            self.help_dialog = MDDialog(
                title="How to Use ResQ?",
                type="custom",
                content_cls=scroll,
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.help_dialog.dismiss())],
                size_hint=(0.9, None),
                radius=[20, 20, 20, 20],
            )
        self.help_dialog.open()
