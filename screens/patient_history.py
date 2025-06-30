import datetime
from collections import Counter

import garden
import requests
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivymd.color_definitions import colors
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
#from kivy_garden.graph import Graph, BarPlot
#from kivy.graphics import Color, Ellipse
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from kivymd.uix.snackbar import MDSnackbar
from matplotlib.figure import Figure
from datetime import datetime

class LegendItem(BoxLayout):
    color_box_color = ListProperty([1, 1, 1, 1])
    label_text = StringProperty('')


class MDVisitCard(MDCard):
    visit_date = StringProperty('')
    visit_status = StringProperty('')
    visit_disease = StringProperty('')
    visit_details = StringProperty('')
    sidebar_color = ListProperty([0.5, 0.5, 0.5, 1]) # Default grey
    bg_color=ListProperty([.5,.5,.5,.2])

class PatientHistoryScreen(Screen):
    COLOR_RULES = {
        "follow-up": [1,1,0,1],
        "emergency": [1,0,0,1],
        "check-up": [0,1,0,1],
    }

    def on_enter(self, *args):
        today = datetime.today()
        formatted_date = today.strftime("%B %d, %Y")
        self.ids.current_display_date_label.text = f"Date: {formatted_date}"
        self.ids.visit_history_container.clear_widgets()
        # Generate some  demo cards
        self.generate_initial_demo_cards()
        #self.update_visits_graph()
        #self.draw_diagnoses_pie_chart()

    def on_pre_enter(self, *args):
        self.patient_history_list=[]
        self.egn=App.get_running_app().selected_patient['EGN']
        print(self.egn)
        #self.egn=App.get_running_app().logged_in_egn
        data={'EGN': self.egn}
        response = requests.post("https://resq-backend-iau8.onrender.com/get-history-patient", json=data)
        res = response.json()
        print(res)

        try:
            result=res['message']['data']
            for record in result:
                # Convert date string to YYYY-MM-DD
                edate_str = record['edate']
                edate_obj = datetime.strptime(edate_str, "%a, %d %b %Y %H:%M:%S %Z")
                formatted_date = edate_obj.strftime("%Y-%m-%d")

                # Extract and form tuple
                entry = (
                    formatted_date,
                    record['visit_type'],
                    record['symptom'],
                    record['description']
                )
                self.patient_history_list.append(entry)

        except Exception as e:
            print(e)
            self.patient_history_list=[]

        if res['message']['data'] != None:
            try:
                response = requests.get("https://resq-backend-iau8.onrender.com/patient-visits-report", json=data)
                print(response)
                res = response.json()
                print(res)
                if res:
                    months, counts, symptoms, percentage = res['message']
                    self.draw_bar_chart(months, counts)
                    self.draw_pie_chart(symptoms, percentage)
            except Exception as e:
                MDSnackbar(MDLabel(text=f"Error: {e}", theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()



        #pass

    def get_sidebar_color(self, details_text):
        details_lower = details_text.lower()
        for keyword, color_tuple in self.COLOR_RULES.items():
            if keyword in details_lower:
                return color_tuple
        return self.COLOR_RULES.get("normal", [0.5, 0.5, 0.5, 1])


    def add_visit_card(self, date_str, status_str, disease_str,details_str):
        sidebar_color = self.get_sidebar_color(status_str)
        new_card = MDVisitCard(
            visit_date=date_str,
            visit_status=status_str,
            visit_disease=disease_str,
            visit_details=details_str,
            sidebar_color=sidebar_color
        )
        self.ids.visit_history_container.add_widget(new_card)



    def generate_initial_demo_cards(self):

        for date, status, disease, details in self.patient_history_list:
            self.add_visit_card(date, status, disease, details)
        self.ids.visit_history_container.add_widget(Widget())


    def go_back(self, *args):
        self.manager.current = "doctor_dashboard"

    def on_leave(self, *args):
        self.ids.visit_history_container.clear_widgets()
        self.ids.bar_box.clear_widgets()
        self.ids.pie_box.clear_widgets()

    def draw_bar_chart(self, x, y):
        months = x

        patient_visits = y
        colors = ['#0077b6', '#00b4d8', '#90e0ef', '#caf0f8', '#adb5bd', '#6c757d']

        fig = Figure(figsize=(4, 4), dpi=90)
        ax = fig.add_subplot(111)
        ax.bar(months, patient_visits, color=colors)
        ax.set_title('Patient Visits Per Month', fontsize=10)
        ax.set_ylabel('Number of Visits', fontsize=9)
        ax.tick_params(axis='x', labelrotation=0, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        self.ids.bar_box.clear_widgets()
        self.ids.bar_box.add_widget(FigureCanvasKivyAgg(fig))

    def draw_pie_chart(self, label, data):
        issue_data = data
        labels = label
        # Generate colors dynamically (repeat if not enough)
        base_colors = ['#ff6b6b', '#f9c74f', '#90be6d', '#43aa8b']
        colors = (base_colors * ((len(issue_data) // len(base_colors)) + 1))[:len(issue_data)]
        # Explode only the first slice
        explode = [0.1] + [0] * (len(issue_data) - 1)

        fig = Figure(figsize=(6, 4), dpi=90)  # Wider figure for space on left
        ax = fig.add_subplot(111)

        # Create the pie chart
        wedges, texts, autotexts = ax.pie(
            issue_data,
            explode=explode,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            shadow=True,
            startangle=140,
            textprops={'fontsize': 10}
        )

        # Keep aspect ratio of pie chart
        ax.axis('equal')
        # Combine labels with their corresponding values
        legend_labels = [f"{label} - {value}%" for label, value in zip(labels, issue_data)]
        # Add side ledger (legend) to the LEFT
        ax.legend(
            wedges,
            legend_labels,
            title="Common Disease",
            loc="center right",
            bbox_to_anchor=(0.12, 0.8),  # Move legend to the left of pie
            fontsize=10
        )

        # Display in Kivy
        self.ids.pie_box.clear_widgets()
        self.ids.pie_box.add_widget(FigureCanvasKivyAgg(fig))