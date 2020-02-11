from functools import partial
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from gui_kivy.color_label import CLabel
from gui_kivy.create_diagram import CreateDiagram


class StatisticScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super(StatisticScreen, self).__init__(**kwargs)

        self.screen_manager = screen_manager
        self.database = None

        self.main_layout = GridLayout(cols=1)
        self.header_layout = GridLayout(cols=2, size_hint=(1, 0.1))
        self.scroll_view = ScrollView(size_hint=(1, 0.8), size=(100, 100))

        self.contact_list_button = Button(text='<=', size_hint=(0.1, 1))
        self.contact_list_button.on_press = self.go_to_contact_list
        self.label = CLabel(text='All statistic', size_hint=(0.9, 1))

        self.buttons_layout = GridLayout(cols=1, size_hint_y=None, row_force_default=True, row_default_height=40)
        self.buttons_layout.bind(minimum_height=self.buttons_layout.setter('height'))
        self.button_all_messages = Button(text='Diagram all messages')
        self.buttons_layout.add_widget(self.button_all_messages)
        self.button_all_messages.on_press = partial(self.create_diagram, self.button_all_messages.text)
        self.scroll_view.add_widget(self.buttons_layout)

        self.header_layout.add_widget(self.contact_list_button)
        self.header_layout.add_widget(self.label)
        self.main_layout.add_widget(self.header_layout)
        self.main_layout.add_widget(self.scroll_view)
        self.add_widget(self.main_layout)

    def go_to_contact_list(self):
        self.screen_manager.current = 'contacts'

    def show_chart(self, label):
        self.screen_manager.current = 'diagram'
        self.screen_manager.get_screen('diagram').set_label(label)

    def get_database(self, database):
        self.database = database

    def create_diagram(self, label):
        new_diagram = CreateDiagram(self.database)
        new_diagram.diagram_all_messages()
        self.show_chart(label)
