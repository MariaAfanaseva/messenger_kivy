from functools import partial
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from gui_kivy.color_label import CLabel


class AddContactScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super(AddContactScreen, self).__init__(**kwargs)

        self.screen_manager = screen_manager

        self.users_buttons = []
        self.database = None
        self.client_transport = None

        self.main_layout = GridLayout(cols=1)

        self.header_layout = GridLayout(cols=2, size_hint=(1, 0.1))
        self.scroll_view = ScrollView(size_hint=(1, 0.8), size=(100, 100))

        self.contact_list_button = Button(text='<=', size_hint=(0.1, 1))
        self.contact_list_button.on_press = self.go_to_contact_list
        self.label = CLabel(text='Add contact.', size_hint=(0.9, 1))

        self.users_layout = GridLayout(cols=1, size_hint_y=None, row_force_default=True, row_default_height=40)
        self.users_layout.bind(minimum_height=self.users_layout.setter('height'))
        self.scroll_view.add_widget(self.users_layout)

        self.header_layout.add_widget(self.contact_list_button)
        self.header_layout.add_widget(self.label)
        self.main_layout.add_widget(self.header_layout)
        self.main_layout.add_widget(self.scroll_view)
        self.add_widget(self.main_layout)
        #  Before show
        self.on_pre_enter = self.show_users_list

    def go_to_contact_list(self):
        self.screen_manager.current = 'contacts'

    def go_to_login(self):
        self.screen_manager.current = 'login'

    def set_objects(self, database, client_transport):
        self.database = database
        self.client_transport = client_transport

    def get_users_list(self):
        users_all = set(self.database.get_known_users())
        contacts_all = set(self.database.get_contacts())
        new_contacts = users_all - contacts_all
        new_contacts.remove(self.client_transport.client_login)
        return new_contacts

    def show_users_list(self):
        for button in self.users_buttons:
            self.users_layout.remove_widget(button)
        self.users_buttons.clear()

        user_list = self.get_users_list()

        for user in user_list:
            user_grid = GridLayout(cols=1, size_hint=(1, 1))
            button = Button(text=user, id=user, size_hint_y=None, height=40)
            user_grid.add_widget(button)
            self.users_buttons.append(user_grid)
            self.users_layout.add_widget(user_grid)
            button.on_press = partial(self.add_contact, user)

    def add_contact(self, user):
        if self.client_transport.add_contact(user):
            text_title = 'Success!'
            text_label = 'Contact successfully added.'
            self.create_message_window(text_title, text_label, self.go_to_contact_list)
        else:
            text_title = 'Error!'
            text_label = 'Lost server connection.'
            self.create_message_window(text_title, text_label, self.go_to_login)

    @staticmethod
    def create_message_window(text_title, text_label, ok_func):
        box = GridLayout(cols=1)
        label = Label(text=text_label,
                      size_hint=(1, 0.7))
        ok_button = Button(text='OK', size_hint=(0.5, 0.2))
        box.add_widget(label)
        box.add_widget(ok_button)
        popup = Popup(title=text_title,
                      content=box,
                      size_hint=(0.6, 0.6))
        ok_button.on_press = ok_func
        ok_button.bind(on_press=popup.dismiss)
        popup.open()


