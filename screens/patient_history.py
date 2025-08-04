import datetime
import requests
from kivy.app import App
from kivy.properties import StringProperty, ListProperty, Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu

from graph import Graph, BarPlot
from kivymd.uix.snackbar import MDSnackbar
from datetime import datetime
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from math import cos, sin, radians
from kivy.uix.label import Label



class LegendItem(BoxLayout):
    color_box_color = ListProperty([1, 1, 1, 1])
    label_text = StringProperty('')


class MDVisitCard(MDCard):
    visit_date = StringProperty('')
    visit_status = StringProperty('')
    visit_disease = StringProperty('')
    visit_details = StringProperty('')
    sidebar_color = ListProperty([0.5, 0.5, 0.5, 1])  # Default grey
    bg_color = ListProperty([.5, .5, .5, .2])
    selected_months=4
    months_menu=None

class PatientHistoryScreen(Screen):
    COLOR_RULES = {
        "follow-up": [1, 1, 0, 1],
        "emergency": [1, 0, 0, 1],
        "check-up": [0, 1, 0, 1],
    }

    def on_enter(self, *args):
        today = datetime.today()
        formatted_date = today.strftime("%B %d, %Y")
        self.ids.current_display_date_label.text = f"Date: {formatted_date}"
        self.ids.visit_history_container.clear_widgets()
        # Generate some  demo cards
        self.generate_initial_demo_cards()
        # self.update_visits_graph()
        # self.draw_diagnoses_pie_chart()

    def months_dropdown(self, caller_widget):

        menu_items = [
            {
                "text": "Upto 4 Months",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=4: self.set_menu_text(x),
            },
            {
                "text": "Upto 5 Months",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=5: self.set_menu_text(x),
            },
            {
                "text": "Upto 6 Months",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=6: self.set_menu_text(x),
            },
            {
                "text": "Upto 7 Months",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=7: self.set_menu_text(x),
            },
            {
                "text": "Upto 8 Months",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=8: self.set_menu_text(x),
            },
            {
                "text": "Upto 9 Months",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=9: self.set_menu_text(x),
            },
            {
                "text": "Upto 10 Months",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=10: self.set_menu_text(x),
            },
        ]

        self.months_menu = MDDropdownMenu(
            caller=caller_widget,
            items=menu_items,
            width_mult=4,
        )

    def show_months_menu(self, caller_widget):
        self.months_dropdown(caller_widget)
        self.months_menu.open()

    def set_menu_text(self, text_item):
        print(text_item)
        self.selected_months = int(text_item)
        data = {'EGN': self.egn,
                'months': int(text_item)}
        try:
            response = requests.get("https://resq-backend-iau8.onrender.com/patient-visits-report", json=data)
            print(response)
            res = response.json()
            print(res)
            if res:
                months, counts, symptoms, percentage = res['message']
                self.draw_bar_chart(months, counts)
                #self.draw_pie_chart(symptoms, percentage)
        except Exception as e:
            MDSnackbar(MDLabel(text=f"Error: {e}", theme_text_color="Custom", text_color=(1, 1, 1, 1))).open()

        if self.months_menu:
            self.months_menu.dismiss()

    def on_pre_enter(self, *args):
        self.patient_history_list = []
        self.egn = App.get_running_app().selected_patient['EGN']
        print(self.egn)
        # self.egn=App.get_running_app().logged_in_egn
        data = {'EGN': self.egn,
                'months': 11}
        response = requests.post("https://resq-backend-iau8.onrender.com/get-history-patient", json=data)
        res = response.json()
        print(res)

        try:
            result = res['message']['data']
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
            self.patient_history_list = []

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

        # pass

    def get_sidebar_color(self, details_text):
        details_lower = details_text.lower()
        for keyword, color_tuple in self.COLOR_RULES.items():
            if keyword in details_lower:
                return color_tuple
        return self.COLOR_RULES.get("normal", [0.5, 0.5, 0.5, 1])

    def add_visit_card(self, date_str, status_str, disease_str, details_str):
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

    # def draw_bar_chart(self, x, y):
    #     months = x
    #
    #     patient_visits = y
    #     colors = ['#0077b6', '#00b4d8', '#90e0ef', '#caf0f8', '#adb5bd', '#6c757d']
    #
    #     fig = Figure(figsize=(4, 4), dpi=90)
    #     ax = fig.add_subplot(111)
    #     ax.bar(months, patient_visits, color=colors)
    #     ax.set_title('Patient Visits Per Month', fontsize=10)
    #     ax.set_ylabel('Number of Visits', fontsize=9)
    #     ax.tick_params(axis='x', labelrotation=0, labelsize=8)
    #     ax.tick_params(axis='y', labelsize=8)
    #     ax.grid(axis='y', linestyle='--', alpha=0.7)
    #
    #     self.ids.bar_box.clear_widgets()
    #     self.ids.bar_box.add_widget(FigureCanvasKivyAgg(fig))

    def draw_bar_chart(self, x, y):
        """
        Generates a bar chart with custom-drawn x-axis labels below it.
        """
        # This main layout holds the title, graph, and our custom x-axis labels
        chart_layout = BoxLayout(orientation='vertical', spacing=dp(5))
        print('months >>>', x)
        print('values >>>', y)
        title = MDLabel(
            text='Patient Visits Per Month',
            font_size='15sp',
            size_hint_y=None,
            height=dp(20),
            color=get_color_from_hex('#333333')
        )
        chart_layout.add_widget(title)

        graph_max_y = (max(y) // 10 + 1) * 10 if y else 10

        graph = Graph(
            background_color=get_color_from_hex('#FFFFFF'),
            border_color=get_color_from_hex('#CCCCCC'),
            tick_color=get_color_from_hex('#CCCCCC'),
            label_options={'color': get_color_from_hex('#333333')},
            font_size='10sp',
            y_ticks_major=10,
            y_grid_label=True,
            padding=dp(5),
            y_grid=True,
            x_grid=False,
            xmin=0,
            xmax=len(x),
            ymin=0,
            ymax=graph_max_y,
            x_ticks_major=1,
            # THE FIX: Turn OFF the graph's default number labels for the x-axis
            x_grid_label=False
        )

        # Add bar plots to the graph
        colors = ['#0077b6', '#00b4d8', '#90e0ef', '#caf0f8', '#adb5bd', '#6c757d']
        for i, value in enumerate(y):
            plot = BarPlot(color=get_color_from_hex(colors[i % len(colors)]), bar_width=dp(20))
            plot.points = [(i + 0.5, value)]
            graph.add_plot(plot)

        # Add the graph to our main layout
        chart_layout.add_widget(graph)

        # --- NEW: Create a separate layout for our custom X-axis labels ---
        labels_layout = BoxLayout(size_hint_y=None, height=dp(20), padding=(dp(20), 0, dp(20), 0))
        for month in x:
            labels_layout.add_widget(
                MDLabel(text=month[0:3],
                        font_size='3sp',
                        size_hint_y=None,
                        height=dp(6),
                        color=get_color_from_hex('#333333'),
                        adaptive_height=True, )
            )

        # Add the custom labels layout below the graph
        chart_layout.add_widget(labels_layout)

        # Add the complete chart (title + graph + labels) to the screen
        self.ids.bar_box.clear_widgets()
        self.ids.bar_box.add_widget(chart_layout)

    def draw_pie_chart(self, label, data):
        self.labels = label
        self.data = data

        # Colors for each slice
        base_colors = ['#ff6b6b', '#f9c74f', '#90be6d', '#43aa8b', '#577590', '#4d908e']
        self.colors = (base_colors * ((len(self.data) // len(base_colors)) + 1))[:len(self.data)]

        self.ids.pie_box.add_widget(MDLabel(
            text="Patient Common Disease",
            font_size='15sp',
            size_hint_y=None,
            height=dp(20),
            color=get_color_from_hex('#333333'),
            adaptive_height=True
        ))
        chart_area = MDBoxLayout(orientation='horizontal', spacing=dp(10))
        pie_chart = PieChartWidget(data=self.data, colors=self.colors, size_hint_x=0.7)

        legend = self.create_legend()

        chart_area.add_widget(pie_chart)
        chart_area.add_widget(legend)

        self.ids.pie_box.add_widget(chart_area)

    def create_legend(self):

        legend_layout = MDBoxLayout(orientation='vertical', size_hint_x=0.3, spacing=dp(8))

        for i, label_text in enumerate(self.labels):

            item_layout = MDBoxLayout(adaptive_height=True, spacing=dp(10))
            color_swatch = ColorSwatch(color=self.colors[i], size_hint=(None, None), size=(dp(12), dp(12)))

            text_label = MDLabel(text=label_text, font_size='8sp',
                                 size_hint_y=None,
                                 height=dp(7),
                                 color=get_color_from_hex('#333333'),
                                 adaptive_height=True,)

            item_layout.add_widget(color_swatch)
            item_layout.add_widget(text_label)
            legend_layout.add_widget(item_layout)

        legend_layout.add_widget(Widget())

        return legend_layout




# This custom widget is responsible for drawing the pie chart itself.
class PieChartWidget(Widget):
    def __init__(self, data, colors, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.colors = colors
        # Bind the redrawing function to the widget's size and position changes.
        # This makes the chart responsive.
        self.bind(pos=self.update_chart, size=self.update_chart)

    def draw_chart(self):
        # Clear any previous drawings
        self.canvas.clear()

        # Don't draw if there's no data
        if not self.data:
            return

        total = sum(self.data)
        angle_start = 0

        with self.canvas:
            # Calculate size and position based on the widget's current properties
            chart_size = min(self.width, self.height) - dp(20)  # Add some padding
            size = (chart_size, chart_size)
            pos = (self.center_x - size[0] / 2, self.center_y - size[1] / 2)

            # --- EDITED: First loop to draw all pie slices ---
            for i, value in enumerate(self.data):
                slice_angle = (value / total) * 360

                Color(rgb=get_color_from_hex(self.colors[i]))
                Ellipse(
                    pos=pos,
                    size=size,
                    angle_start=angle_start,
                    angle_end=angle_start + slice_angle
                )
                percentage = (value / total) * 100
                mid_angle = angle_start + slice_angle / 2

                label_angle = 90 - mid_angle

                label_x = self.center_x + (size[0] / 2.5) * cos(radians(label_angle))
                label_y = self.center_y + (size[1] / 2.5) * sin(radians(label_angle))

                label = Label(text=f"{percentage:.1f}%", font_size='7sp',
                              size_hint_y=None,
                              height=dp(4), color=(1, 1, 1, 1), bold=True)
                label.texture_update()

                Color(1, 1, 1, 1)  # Reset color to white for the text
                Rectangle(
                    texture=label.texture,
                    size=label.texture_size,
                    pos=(label_x - label.texture_size[0] / 2, label_y - label.texture_size[1] / 2)
                )

                angle_start += slice_angle

    def update_chart(self, *args):
        # This method is called whenever the widget's position or size changes.
        self.draw_chart()


# This widget is now more robust to fix the drawing bug.
class ColorSwatch(Widget):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *args):
        # This function now clears and redraws the swatch completely
        # whenever its position or size changes.
        self.canvas.clear()
        with self.canvas:
            Color(rgb=get_color_from_hex(self.color))
            Ellipse(pos=self.pos, size=self.size)
