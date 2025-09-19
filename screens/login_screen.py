import threading

from kivy import Config
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from datetime import datetime, timedelta

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
from kivy.storage.jsonstore import JsonStore


# 🔹 Avoid circular import by defining path here
try:
    if platform == "android":
        from android.storage import app_storage_path
        base_path = app_storage_path()
    else:
        base_path = os.getcwd()
except ImportError:
    base_path = os.getcwd()

remember_file_path = join(base_path, "user_data.json")
store = JsonStore(remember_file_path)

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

    def on_pre_enter(self, *args):
        self.app=MDApp.get_running_app()

    def login(self):
        self.username = self.ids.username_input.text.strip()
        self.password = self.ids.password_input.text.strip()
        self.remember = self.ids.remember_checkbox.active

        if not self.username or not self.password:
           MDSnackbar(MDLabel(
               text="Please enter both username and password",
               theme_text_color="Custom", text_color=(1, 1, 1, 1)
           )).open()
           return
        self.app.show_loading('Logging...')
        threading.Thread(target=self.login_process, daemon=True).start()



    def login_process(self, *args):

        try:
            response = requests.post("https://resq-backend-iau8.onrender.com/login", json={
                "username": self.username,
                "password": self.password,
                "remember_me": self.remember
            })

            data = response.json()
            message = str(data.get("message", "Login successful!"))
            self.ids.status_label.text = message

            if response.status_code == 200:
                self.ids.status_label.text_color = (0, 1, 0, 1)
                self.app.show_snackbar(message, (1, 1, 1, 1))
                # MDSnackbar(MDLabel(
                #     text=message,
                #     theme_text_color="Custom", text_color=(1, 1, 1, 1)
                # )).open()

                token = data.get("token")
                if self.remember and token:
                    #self.save_token(token)
                    store.put('auth', token=token)
                    three_days_later = datetime.now() + timedelta(days=30)
                    print(three_days_later)
                    date_str = three_days_later.strftime("%Y-%m-%d %H:%M:%S")  # convert to string
                    store.put('expire_session', date=date_str)

                self.app.logged_in_username = self.username
                self.app.logged_in_egn = data.get("egn")
                self.app.logged_in_role = data.get("role")

                role = data.get("role")
                if role == "patient":
                    #self.manager.current = "patient_dashboard"
                    Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'patient_dashboard'))
                elif role == "doctor":
                    #self.manager.current = "doctor_dashboard"
                    Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'doctor_dashboard'))
            else:
                self.ids.status_label.text_color = (1, 0, 0, 1)
                self.app.show_snackbar(message)
                # MDSnackbar(MDLabel(
                #     text=message,
                #     theme_text_color="Custom", text_color=(1, 0, 0, 1)
                # )).open()

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.ids.status_label.text = error_msg
            self.ids.status_label.text_color = (1, 0, 0, 1)
            # MDSnackbar(MDLabel(
            #     text=error_msg,
            #     theme_text_color="Custom", text_color=(1, 0, 0, 1)
            # )).open()
            self.app.show_snackbar(error_msg)

        Clock.schedule_once(lambda dt: self.app.hide_loading(), 0)

    def on_leave(self, *args):
        self.clear_fields()

    def on_enter(self, *args):
        print('enter')
        store = JsonStore(remember_file_path)
        if store.exists('auth'):
            self.token = store.get('auth')['token']
            print(self.token)
            # if os.path.exists(remember_file_path):
            if self.token is not None:
                self.app.show_loading('Auto Logging')
                Clock.schedule_once(self.auto_login, 1.0)


    def auto_login(self, *args):

        threading.Thread(target=self.try_auto_login, daemon=True).start()
        # role = self.try_auto_login()


    def try_auto_login(self):
        store = JsonStore(remember_file_path)
        expire_date_str = store.get('expire_session')['date']
        expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        # Compare
        if now > expire_date:
            error_msg = "Session expired"
            self.app.show_snackbar(error_msg)
            store.put('auth', token=None)
            Clock.schedule_once(lambda dt: self.app.hide_loading(), 0)
            return
        try:
            import certifi
            response = requests.post(
                "https://resq-backend-iau8.onrender.com/auto-login",
                json={"token": self.token},
                verify=certifi.where()
            )
            if response.status_code == 200:
                data = response.json()
                self.logged_in_username = data.get("username")
                self.logged_in_egn = data.get("EGN")
                self.logged_in_role = data.get("role")
                self.role = data.get("role")
                if self.role == "patient":
                    Clock.schedule_once(lambda dt: setattr(self.manager, "current", "patient_dashboard"))
                elif self.role == "doctor":
                    Clock.schedule_once(lambda dt: setattr(self.manager, "current", "doctor_dashboard"))
                else:
                    Clock.schedule_once(lambda dt: setattr(self.manager, "current", "login"))

        except Exception as e:
            print("Auto-login failed:", e)
        Clock.schedule_once(lambda dt: self.app.hide_loading(), 0)


    # def save_token(self, token):
    #     try:
    #         with open(remember_file_path, "w") as file:
    #             file.write(token)
    #         print("Token saved for auto-login")
    #     except Exception as e:
    #         print(f" Failed to save token: {e}")

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
                "5. On first use, please send a test SOS message to your contacts. This allows you to verify the functionality and the number you have entered.\n\n"

                "All alerts will be sent from +1 380-324-0238. We recommend that your contacts save this number as important.\n\n"

                "For Doctors:\n"
                "You can assign patients via EGN, edit their info, record and review their visits or remove them from your care list.\n\n"

                "Data Policy:\n"
                "If you wish to delete your profile, please contact us at support@resqapp.com.\n"
                "Your data will be permanently removed from our system within 1–3 business days.\n\n"
                "Need help? Our 24/7 assistance phone is available at: +359 89 701 3915"
            )

            content = MDLabel(
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
