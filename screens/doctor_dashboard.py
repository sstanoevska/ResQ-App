import json
import os

from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import requests


class DoctorDashboardScreen(MDScreen):
    def on_enter(self):
        print("Logo exists?", os.path.exists("assets/logo1.png"))
        Clock.schedule_once(lambda dt: self.load_dashboard(), 0.5)

    def load_dashboard(self):
        username = App.get_running_app().logged_in_username

        try:
            response = requests.get("https://resq-backend-iau8.onrender.com/doctor-dashboard", params={
                "doctor_egn": username,
            })

            data = response.json()
            print(json.dumps(data, indent=2))
            if response.status_code != 200:
                self.show_error(data.get("message", "Error loading dashboard"))
                return

            self.doctor_info = data.get("doctor_info", {})
            self.patients = data.get("patients", [])
            print(f"✅ Loaded {len(self.patients)} patients from backend")

            name = self.doctor_info.get("name")
            self.ids.greeting_label.text = f" Welcome back, Dr. {name}!" if name else "Hi, Doctor"

            self.show_doctor_info()
            self.show_patients()

        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def show_doctor_info(self):
        self.ids.doctor_info_box.clear_widgets()

        fields = [
            ("account", "Name", self.doctor_info.get("name")),
            ("calendar", "Date of Birth", self.doctor_info.get("date_of_birth")),
            ("phone", "Phone", self.doctor_info.get("phone")),
            ("map-marker", "Address", self.doctor_info.get("address")),
        ]

        for icon_name, label, value in fields:
            if value:
                item_box = BoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height="48dp",
                    spacing="10dp",
                    padding=("5dp", "0dp")
                )
                icon = MDIconButton(
                    icon=icon_name,
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    size_hint=(None, None),
                    size=("40dp", "40dp")
                )
                label_widget = MDLabel(
                    text=f"{label}: {value}",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    halign="left",
                    valign="middle"
                )
                item_box.add_widget(icon)
                item_box.add_widget(label_widget)
                self.ids.doctor_info_box.add_widget(item_box)

    def show_patients(self):
        self.ids.patients_list.clear_widgets()
        print("🔄 Refreshing patient list")

        for patient in self.patients:
            try:
                patient_box = BoxLayout(
                    orientation="horizontal", size_hint_y=None, height="48dp", padding="5dp", spacing="10dp"
                )

                patient_box.add_widget(MDIconButton(icon="account", theme_text_color="Custom", text_color=(0, 0, 0, 1)))

                patient_box.add_widget(MDLabel(
                    text=f"{patient['name']} - {patient['phone']}",
                    theme_text_color="Custom",
                    text_color=(0, 0, 0, 1),
                    size_hint_x=0.6
                ))

                pencil_icon = MDIconButton(icon="pencil", theme_text_color="Custom", text_color=(0, 0, 0, 1))
                pencil_icon.bind(on_release=lambda x, p=patient: self.open_edit_patient_screen(p))
                patient_box.add_widget(pencil_icon)

                trash_icon = MDIconButton(icon="trash-can", theme_text_color="Custom", text_color=(0, 0, 0, 1))
                trash_icon.bind(on_release=lambda x, e=patient["EGN"]: self.confirm_delete_patient(e))
                patient_box.add_widget(trash_icon)

                self.ids.patients_list.add_widget(patient_box)

            except Exception as e:
                print(f"Error displaying patient: {e}")

    def open_assign_patient_dialog(self):
        self.patient_input = MDTextField(
            hint_text="Enter patient EGN",
            helper_text="Patient must already exist",
            size_hint_x=0.9
        )

        self.dialog = MDDialog(
            title="Assign Patient",
            type="custom",
            content_cls=self.patient_input,
            buttons=[
                MDButton(text="Assign", style="outlined", on_release=self.assign_patient_to_doctor),
                MDButton(text="Cancel", style="outlined", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()

    def assign_patient_to_doctor(self, instance):
        patient_egn = self.patient_input.text.strip()
        doctor_egn = App.get_running_app().logged_in_egn

        if not patient_egn:
            self.show_error("Please enter a patient EGN.")
            return

        try:
            response = requests.post("https://resq-backend-iau8.onrender.com/assign-patient", json={
                "doctor_egn": doctor_egn,
                "patient_egn": patient_egn,
            })

            if response.status_code == 200:
                self.dialog.dismiss()
                self.load_dashboard()
                MDSnackbar(MDLabel(text="Patient successfully assigned.",
                                   theme_text_color="Custom", text_color=(0, 1, 0, 1))).open()
            else:
                self.show_error(response.json().get("message", "Failed to assign patient."))
        except Exception as e:
            self.show_error(str(e))

    def delete_patient(self, patient_egn):
        doctor_egn = App.get_running_app().logged_in_egn
        try:
            if hasattr(self, "delete_dialog"):
                self.delete_dialog.dismiss()

            res = requests.post("https://resq-backend-iau8.onrender.com/delete-patient", json={
                "doctor_egn": doctor_egn,
                "patient_egn": patient_egn,
            })
            if res.status_code == 200:
                self.load_dashboard()
                MDSnackbar(
                    MDLabel(
                        text="Patient removed.",
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1),
                    )
                ).open()
            else:
                self.show_error(res.json().get("message", "Deletion failed."))
        except Exception as e:
            self.show_error(str(e))

    def confirm_delete_patient(self, patient_egn):
        self.delete_dialog = MDDialog(
            title="Delete Patient?",
            text="Are you sure you want to remove this patient?",
            buttons=[
                MDButton(text="Cancel", style="outlined", on_release=lambda x: self.delete_dialog.dismiss()),
                MDButton(text="Delete", style="outlined", on_release=lambda x: self.delete_patient(patient_egn))
            ]
        )
        self.delete_dialog.open()

    def show_error(self, message):
        dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[MDButton(text="OK", style="outlined", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def open_edit_profile_screen(self):
        self.manager.current = "edit_profile"

    def open_edit_patient_screen(self, patient):
        App.get_running_app().selected_patient = patient
        self.manager.current = "edit_patient_info"

    def view_patient_details(self, patient):
        App.get_running_app().selected_patient = patient
        self.manager.current = "view_patient_info"

    def logout(self):
        self.manager.current = "login"
