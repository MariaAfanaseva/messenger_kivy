from functools import partial
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from gui_kivy.color_label import CLabel


class ContactScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super(ContactScreen, self).__init__(**kwargs)

        self.screen_manager = screen_manager

        self.contacts_buttons = []
        self.database = None
        self.client_transport = None

        self.main_layout = GridLayout(cols=1)
        self.header_layout = GridLayout(cols=2, size_hint=(1, 0.1))
        self.scroll_view = ScrollView(size_hint=(1, 0.8), size=(100, 100))

        #  Create menu
        self.menu_button = DropDown()
        for name in ['Add contact', 'Delete contact']:
            btn = Button(text=f'{name}', size_hint_y=None, height=30)
            btn.bind(on_release=lambda btn: self.menu_button.select(btn.text))
            self.menu_button.add_widget(btn)
        self.main_button = Button(text='Menu', size_hint=(.2, .5))
        self.main_button.bind(on_release=self.menu_button.open)

        self.menu_button.bind(on_select=lambda instance, x: self.show_screen(x))

        self.label = CLabel(size_hint=(0.9, 1))

        self.contacts_layout = GridLayout(cols=1, size_hint_y=None, row_force_default=True, row_default_height=40)
        self.contacts_layout.bind(minimum_height=self.contacts_layout.setter('height'))

        self.header_layout.add_widget(self.main_button)
        self.header_layout.add_widget(self.label)
        self.scroll_view.add_widget(self.contacts_layout)

        self.main_layout.add_widget(self.header_layout)
        self.main_layout.add_widget(self.scroll_view)
        self.add_widget(self.main_layout)
        #  Before show
        self.on_pre_enter = self.update_contact_list

    def update_contact_list(self, new_message=None):
        for button in self.contacts_buttons:
            self.contacts_layout.remove_widget(button)
        self.contacts_buttons.clear()

        contact_list = self.get_contact_list()

        for contact in contact_list:
            contact_grid = GridLayout(cols=2, size_hint=(1, 0.1))
            button = Button(text=contact, id=contact, size_hint_y=None, height=40)
            contact_grid.add_widget(button)
            if new_message:
                if new_message == contact:
                    label = ContactScreen.CLabel(text="new message", size_hint=(0.2, 1))
                    contact_grid.add_widget(label)
            self.contacts_buttons.append(contact_grid)
            self.contacts_layout.add_widget(contact_grid)
            button.on_press = partial(self.go_to_chat, contact)

    def go_to_chat(self, contact_name):
        if self.client_transport.is_received_pubkey(contact_name):
            self.screen_manager.current = 'chat'
            chat = self.screen_manager.get_screen('chat')
            chat.load_chat(contact_name)
        else:
            self.show_info_screen('User is not online.', 'contacts')

    def show_info_screen(self, *args):
        self.screen_manager.current = 'info'
        self.screen_manager.get_screen('info').set_message(*args)

    def set_objects(self, database, client_transport):
        self.database = database
        self.client_transport = client_transport
        self.label.text = f'Hello {self.client_transport.client_login}! ' \
                          f'Here is your contact list.'

    def get_contact_list(self):
        contacts_list = self.database.get_contacts()
        return contacts_list

    def show_label(self, *args):
        sender = args[0]
        self.update_contact_list(new_message=sender)

    def connect_contacts_signal(self, client_obj):
        client_obj.new_message_signal_contacts.connect(self.show_label)

    def show_screen(self, name):
        if name == 'Add contact':
            self.screen_manager.current = 'add_contact'
