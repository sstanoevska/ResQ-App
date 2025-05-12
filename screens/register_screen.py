from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivymd.uix.menu import MDDropdownMenu
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

        show = value == "patient"
        for box in [
            self.ids.dob_box, self.ids.address_box,
            self.ids.allergies_box, self.ids.diagnosis_box, self.ids.medications_box
        ]:
            box.height = dp(60) if show else 0
            box.opacity = 1 if show else 0
            box.disabled = not show


    def register(self):
        role = self.ids.role_input.text.strip()
        egn = self.ids.egn_input.text.strip()

        if not (egn.isdigit() and len(egn) == 10):
            toast("Please enter a valid EGN!")
            return

        name = self.ids.name_input.text.strip()
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        confirm_password = self.ids.confirm_password.text.strip()
        phone = self.ids.phone_input.text.strip()

        if password != confirm_password:
            toast("Passwords don't match!")
            return

        if not all([name, username, password, confirm_password, phone, role]):
            toast("Please fill out all required fields.")
            return

        if role == "patient":
            data = {
                "EGN": egn,
                "name": name,
                "username": username,
                "password": password,
                "date_of_birth": self.ids.dob_input.text.strip(),
                "phone": phone,
                "address": self.ids.address_input.text.strip(),
                "allergies": self.ids.allergies_input.text.strip(),
                "diagnosis": self.ids.diagnosis_input.text.strip(),
                "medications": self.ids.medications_input.text.strip(),
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
            toast("Select role!")
            return

        try:
            response = requests.post("http://127.0.0.1:5000/register", json=data)
            res = response.json()
            toast(res.get("message", "Registration done."))
        except requests.exceptions.JSONDecodeError:
            toast("Server returned invalid response.")
        except Exception as e:
            toast(f"Error: {e}")
