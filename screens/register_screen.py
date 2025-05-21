from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.metrics import dp
import requests

class RegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.role_menu = None
        Clock.schedule_once(self.setup_menus, 1)

    def setup_menus(self, *args):
        role_items = [
            {
                "text": "patient",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="patient": self.set_role(x),
                "text_color": (0, 0, 0, 1)
            },
            {
                "text": "doctor",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="doctor": self.set_role(x),
                "text_color": (0, 0, 0, 1)
            }
        ]

        self.role_menu = MDDropdownMenu(
            caller=self.ids.role_input,
            items=role_items,
            width_mult=4
        )

    def open_role_menu(self):
        if self.role_menu:
            self.role_menu.open()

    def set_role_visibility(self, value):
        show = value == "patient"
        for box in [
            self.ids.dob_box, self.ids.address_box,
            self.ids.allergies_box, self.ids.diagnosis_box, self.ids.medications_box
        ]:
            box.height = dp(60) if show else 0
            box.opacity = 1 if show else 0
            box.disabled = not show

    def set_role(self, value):
        self.ids.role_input.text = value
        self.role_menu.dismiss()
        self.set_role_visibility(value)

    def clear_fields(self):
        self.ids.egn_input.text = ""
        self.ids.name_input.text = ""
        self.ids.username_input.text = ""
        self.ids.password_input.text = ""
        self.ids.confirm_password.text = ""
        self.ids.phone_input.text = ""
        self.ids.dob_input.text = ""
        self.ids.address_input.text = ""
        self.ids.allergies_input.text = ""
        self.ids.diagnosis_input.text = ""
        self.ids.medications_input.text = ""
        self.ids.role_input.text = "patient"
        self.set_role_visibility("patient")

    def register(self):
        role = self.ids.role_input.text.strip()
        egn = self.ids.egn_input.text.strip()

        if not (egn.isdigit() and len(egn) == 10):
            MDSnackbar(MDLabel(text="Please enter a valid EGN!", theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()
            return

        name = self.ids.name_input.text.strip()
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        confirm_password = self.ids.confirm_password.text.strip()
        phone = self.ids.phone_input.text.strip()

        if password != confirm_password:
            MDSnackbar(MDLabel(text="Passwords don't match!", theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()
            return

        if not all([name, username, password, confirm_password, phone, role]):
            MDSnackbar(MDLabel(text="Please fill out all required fields.", theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()
            return

        if role == "patient":
            data = {
                "EGN": egn,
                "name": name,
                "username": username,
                "password": password,
                "date_of_birth": self.ids.dob_input.text.strip() or None,
                "phone": phone,
                "address": self.ids.address_input.text.strip() or None,
                "allergies": self.ids.allergies_input.text.strip() or None,
                "diagnosis": self.ids.diagnosis_input.text.strip() or None,
                "medications": self.ids.medications_input.text.strip() or None,
                "role": "patient",
            }
        elif role == "doctor":
            data = {
                "EGN": egn,
                "name": name,
                "username": username,
                "password": password,
                "phone": phone,
                "role": "doctor",
            }
        else:
            MDSnackbar(MDLabel(text="Select role!", theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()
            return

        try:
            response = requests.post("https://resq-backend-iau8.onrender.com/register", json=data)
            res = response.json()
            MDSnackbar(MDLabel(text=res.get("message", "Registration done."), theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()
            self.clear_fields()
        except requests.exceptions.JSONDecodeError:
            MDSnackbar(MDLabel(text="Server returned invalid response.", theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()
        except Exception as e:
            MDSnackbar(MDLabel(text=f"Error: {e}", theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()
