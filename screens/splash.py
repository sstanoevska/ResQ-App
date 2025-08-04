from kivy import platform
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
import threading
import socket
import urllib.request

class SplashScreen(Screen):
    status_text = StringProperty("Checking internet connection...")
    show_retry = BooleanProperty(False)

    def on_enter(self):
        self.start_check()

    def start_check(self):
        self.status_text = "Checking internet connection..."
        self.show_retry = False
        threading.Thread(target=self.check_internet, daemon=True).start()

    def check_internet(self):
        try:
            if platform=='android':
                urllib.request.urlopen("http://clients3.google.com/generate_204", timeout=3)
            else:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
            Clock.schedule_once(lambda dt: self.goto_login())
        except OSError:
            Clock.schedule_once(lambda dt: self.no_connection())

    def goto_login(self):
        self.status_text = "Internet connected. Redirecting..."
        self.show_retry = False
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 1)

    def no_connection(self):
        self.status_text = "No internet connection. Please check your connection."
        self.show_retry = True

    def retry_check(self):
        self.start_check()

