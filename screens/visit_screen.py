import requests
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
import datetime
from kivy.app import App
from kivymd.uix.snackbar import MDSnackbar


class AddVisitScreen(MDScreen):
    priority_menu = None

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.setup_dropdown()
        self.setup_symptom_dropdown()


    def on_enter(self, *args):
        #self.populate_date()
        self.user_egn = App.get_running_app().selected_patient['EGN']
        self.clear_form_inputs()

    def go_back(self, *args):
        self.manager.current = "patient_history"


    def setup_dropdown(self):

        visit_input_field = self.ids.visit_type

        menu_items = [
            {
                "text": "Emergency",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Emergency": self.set_priority_text(x),
            },
            {
                "text": "Follow-up",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Follow-up": self.set_priority_text(x),
            },
            {
                "text": "Check-up",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Check-up": self.set_priority_text(x),
            },
        ]

        self.priority_menu = MDDropdownMenu(
            caller=visit_input_field, # The MDTextField is the caller
            items=menu_items,
            width_mult=4,
        )

    def show_priority_menu(self):

        #if focus and self.priority_menu:
        self.priority_menu.open()
        # else:
            # print("Menu not opened. Focus is False or menu not initialized.")

    def set_priority_text(self, text_item):
        # Update the text of the MDTextField usidjkas jklng its ID
        self.ids.visit_type.text = text_item
        if self.priority_menu:
            self.priority_menu.dismiss()

    def setup_symptom_dropdown(self):
        symptom_input_field = self.ids.symptoms  # Replace with your actual TextField ID

        symptom_items = [

            # 🌡️ General Symptoms
            {"text": "Normal", "viewclass": "OneLineListItem", "on_release": lambda x="Normal": self.set_symptom_text(x)},

            {"text": "Fever", "viewclass": "OneLineListItem", "on_release": lambda x="Fever": self.set_symptom_text(x)},
            {"text": "Fatigue", "viewclass": "OneLineListItem",
             "on_release": lambda x="Fatigue": self.set_symptom_text(x)},
            {"text": "Headache", "viewclass": "OneLineListItem",
             "on_release": lambda x="Headache": self.set_symptom_text(x)},
            {"text": "Dizziness", "viewclass": "OneLineListItem",
             "on_release": lambda x="Dizziness": self.set_symptom_text(x)},
            {"text": "Nausea", "viewclass": "OneLineListItem",
             "on_release": lambda x="Nausea": self.set_symptom_text(x)},
            {"text": "Vomiting", "viewclass": "OneLineListItem",
             "on_release": lambda x="Vomiting": self.set_symptom_text(x)},
            {"text": "Chills", "viewclass": "OneLineListItem",
             "on_release": lambda x="Chills": self.set_symptom_text(x)},
            {"text": "Sweating", "viewclass": "OneLineListItem",
             "on_release": lambda x="Sweating": self.set_symptom_text(x)},
            {"text": "Weight loss", "viewclass": "OneLineListItem",
             "on_release": lambda x="Weight loss": self.set_symptom_text(x)},
            {"text": "Loss of appetite", "viewclass": "OneLineListItem",
             "on_release": lambda x="Loss of appetite": self.set_symptom_text(x)},

            # 🫀 Cardiovascular & Respiratory
            {"text": "Chest pain", "viewclass": "OneLineListItem",
             "on_release": lambda x="Chest pain": self.set_symptom_text(x)},
            {"text": "Shortness of breath", "viewclass": "OneLineListItem",
             "on_release": lambda x="Shortness of breath": self.set_symptom_text(x)},
            {"text": "Palpitations", "viewclass": "OneLineListItem",
             "on_release": lambda x="Palpitations": self.set_symptom_text(x)},
            {"text": "Cough", "viewclass": "OneLineListItem", "on_release": lambda x="Cough": self.set_symptom_text(x)},
            {"text": "Wheezing", "viewclass": "OneLineListItem",
             "on_release": lambda x="Wheezing": self.set_symptom_text(x)},
            {"text": "Rapid heartbeat", "viewclass": "OneLineListItem",
             "on_release": lambda x="Rapid heartbeat": self.set_symptom_text(x)},
            {"text": "High blood pressure", "viewclass": "OneLineListItem",
             "on_release": lambda x="High blood pressure": self.set_symptom_text(x)},
            {"text": "Swelling in legs", "viewclass": "OneLineListItem",
             "on_release": lambda x="Swelling in legs": self.set_symptom_text(x)},

            # 🤒 Infectious Symptoms
            {"text": "Sore throat", "viewclass": "OneLineListItem",
             "on_release": lambda x="Sore throat": self.set_symptom_text(x)},
            {"text": "Runny nose", "viewclass": "OneLineListItem",
             "on_release": lambda x="Runny nose": self.set_symptom_text(x)},
            {"text": "Sneezing", "viewclass": "OneLineListItem",
             "on_release": lambda x="Sneezing": self.set_symptom_text(x)},
            {"text": "Ear pain", "viewclass": "OneLineListItem",
             "on_release": lambda x="Ear pain": self.set_symptom_text(x)},
            {"text": "Diarrhea", "viewclass": "OneLineListItem",
             "on_release": lambda x="Diarrhea": self.set_symptom_text(x)},
            {"text": "Body aches", "viewclass": "OneLineListItem",
             "on_release": lambda x="Body aches": self.set_symptom_text(x)},
            {"text": "Rash", "viewclass": "OneLineListItem", "on_release": lambda x="Rash": self.set_symptom_text(x)},
            {"text": "Enlarged lymph nodes", "viewclass": "OneLineListItem",
             "on_release": lambda x="Enlarged lymph nodes": self.set_symptom_text(x)},

            # 🧠 Neurological & Psychological
            {"text": "Anxiety", "viewclass": "OneLineListItem",
             "on_release": lambda x="Anxiety": self.set_symptom_text(x)},
            {"text": "Depression", "viewclass": "OneLineListItem",
             "on_release": lambda x="Depression": self.set_symptom_text(x)},
            {"text": "Confusion", "viewclass": "OneLineListItem",
             "on_release": lambda x="Confusion": self.set_symptom_text(x)},
            {"text": "Memory loss", "viewclass": "OneLineListItem",
             "on_release": lambda x="Memory loss": self.set_symptom_text(x)},
            {"text": "Insomnia", "viewclass": "OneLineListItem",
             "on_release": lambda x="Insomnia": self.set_symptom_text(x)},
            {"text": "Seizures", "viewclass": "OneLineListItem",
             "on_release": lambda x="Seizures": self.set_symptom_text(x)},
            {"text": "Numbness or tingling", "viewclass": "OneLineListItem",
             "on_release": lambda x="Numbness or tingling": self.set_symptom_text(x)},
            {"text": "Tremors", "viewclass": "OneLineListItem",
             "on_release": lambda x="Tremors": self.set_symptom_text(x)},

            # 🦴 Musculoskeletal
            {"text": "Joint pain", "viewclass": "OneLineListItem",
             "on_release": lambda x="Joint pain": self.set_symptom_text(x)},
            {"text": "Muscle cramps", "viewclass": "OneLineListItem",
             "on_release": lambda x="Muscle cramps": self.set_symptom_text(x)},
            {"text": "Back pain", "viewclass": "OneLineListItem",
             "on_release": lambda x="Back pain": self.set_symptom_text(x)},
            {"text": "Stiffness", "viewclass": "OneLineListItem",
             "on_release": lambda x="Stiffness": self.set_symptom_text(x)},
            {"text": "Weakness", "viewclass": "OneLineListItem",
             "on_release": lambda x="Weakness": self.set_symptom_text(x)},

            # 🩸 Urinary & Reproductive
            {"text": "Painful urination", "viewclass": "OneLineListItem",
             "on_release": lambda x="Painful urination": self.set_symptom_text(x)},
            {"text": "Frequent urination", "viewclass": "OneLineListItem",
             "on_release": lambda x="Frequent urination": self.set_symptom_text(x)},
            {"text": "Blood in urine", "viewclass": "OneLineListItem",
             "on_release": lambda x="Blood in urine": self.set_symptom_text(x)},
            {"text": "Menstrual irregularities", "viewclass": "OneLineListItem",
             "on_release": lambda x="Menstrual irregularities": self.set_symptom_text(x)},
            {"text": "Pelvic pain", "viewclass": "OneLineListItem",
             "on_release": lambda x="Pelvic pain": self.set_symptom_text(x)},
            {"text": "Erectile dysfunction", "viewclass": "OneLineListItem",
             "on_release": lambda x="Erectile dysfunction": self.set_symptom_text(x)},
        ]

        self.symptom_menu = MDDropdownMenu(
            caller=symptom_input_field,
            items=symptom_items,
            width_mult=4,
        )

    def show_symptom_menu(self):
        self.symptom_menu.open()

    def set_symptom_text(self, text_item):
        self.ids.symptoms.text = text_item  # Replace with actual ID
        if self.symptom_menu:
            self.symptom_menu.dismiss()

    def on_pre_enter(self, *args):
        today = datetime.date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        self.ids.date.text = formatted_date

    def submit(self):
        #print(self.user_egn)
        date = self.ids.date.text
        visit_type = self.ids.visit_type.text
        symptoms = self.ids.symptoms.text
        description = self.ids.description.text
        if date != '' and visit_type != '' and symptoms != '':
            print( date, visit_type, symptoms, description)
            data={'EGN': self.user_egn,
                  'edate': date,
                  'visit_type': visit_type,
                  'symptoms': symptoms,
                  'description': description}
            try:
                response = requests.post("https://resq-backend-iau8.onrender.com/add_history-patient", json=data)
                res = response.json()
                print(res)
                MDSnackbar(MDLabel(text=res.get("message", "Record Added."), theme_text_color="Custom",
                                   text_color=(1, 1, 1, 1))).open()
                self.clear_form_inputs()
            except requests.exceptions.JSONDecodeError:
                MDSnackbar(MDLabel(text="Server returned invalid response.", theme_text_color="Custom",
                                   text_color=(1, 1, 1, 1))).open()
            except Exception as e:
                MDSnackbar(MDLabel(text=f"Error: {e}", theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()

        else:
            MDSnackbar(MDLabel(text="Fill Fields!", theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()


    def clear_form_inputs(self):
        self.ids.visit_type.text=""
        self.ids.symptoms.text = ""
        self.ids.description.text = ""


    def on_leave(self, *args):
        self.clear_form_inputs()
