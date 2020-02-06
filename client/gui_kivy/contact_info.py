import os
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from gui_kivy.color_label import CLabel
from common.variables import get_path


class ContactInfoScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super(ContactInfoScreen, self).__init__(**kwargs)
        self.screen_manager = screen_manager
        self.contact_name = None

        self.main_layout = GridLayout(cols=1)
        self.header_layout = GridLayout(cols=2, size_hint=(1, 0.1))
        self.info_layout = GridLayout(cols=2, size_hint=(1, 1))
        self.back_button = Button(text='<=', size_hint=(0.1, 1))
        self.back_button.on_press = self.go_to_contact_list
        self.label = CLabel(text='', size_hint=(0.9, 1))
        self.header_layout.add_widget(self.back_button)
        self.header_layout.add_widget(self.label)
        self.main_layout.add_widget(self.header_layout)
        self.main_layout.add_widget(self.info_layout)
        self.add_widget(self.main_layout)

    def get_contact_name(self, name):
        self.contact_name = name
        print(self.contact_name)
        self.show_label()
        self.show_avatar()

    def show_label(self):
        self.label.text = f'Personal information for contact {self.contact_name}'

    def show_avatar(self):
        self.info_layout.clear_widgets()
        path_img = get_path(self.contact_name)
        if os.path.exists(path_img):
            img = Image(source=path_img)
            self.info_layout.add_widget(img)

    def go_to_contact_list(self):
        self.screen_manager.current = 'chat'
        self.screen_manager.get_screen('chat').load_chat(self.contact_name)
