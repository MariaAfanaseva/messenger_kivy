from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class InfoScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        self.screen_manager = screen_manager
        self.back_screen = 'contacts'

        self.main_layout = GridLayout(cols=1, padding=(100, 0, 100, 0))
        self.main_layout.add_widget(Label(size_hint=(1, 0.3)))
        self._label = Label(text='', size_hint=(0.1, 0.1))
        self.main_layout.add_widget(self._label)
        self.button = Button(text='Back', size_hint=(0.7, 0.1))
        self.button.on_press = self.go_to_screen
        self.main_layout.add_widget(self.button)
        self.main_layout.add_widget(Label(size_hint=(1, 0.3)))
        self.add_widget(self.main_layout)

    def set_message(self, message, back_screen):
        self._label.text = message
        self.back_screen = back_screen

    def go_to_screen(self):
        self.screen_manager.current = self.back_screen
