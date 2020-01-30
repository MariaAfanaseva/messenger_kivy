from functools import partial
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from gui_kivy.color_label import CLabel


class ContactScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super(ContactScreen, self).__init__(**kwargs)

        self.screen_manager = screen_manager

        self.contacts_buttons = []
        self.database = None
        self.client_transport = None
        self.new_messages = {}

        self.main_layout = GridLayout(cols=1)
        self.header_layout = GridLayout(cols=2, size_hint=(1, 0.1))
        self.scroll_view = ScrollView(size_hint=(1, 0.8), size=(100, 100))

        #  Create menu
        self.menu_button = DropDown()
        for name in ['Add contact']:
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
            contact_grid = GridLayout(cols=3, size_hint=(1, 0.1))

            contact_menu = DropDown()
            for name in ['Delete']:
                btn = Button(text=f'{name}', size_hint_y=None, height=30)
                btn.bind(on_release=lambda btn: contact_menu.select(btn.text))
                contact_menu.add_widget(btn)
            main_button = Button(text=':', size_hint=(.1, .3))
            main_button.bind(on_release=contact_menu.open)

            contact_menu.bind(on_select=lambda instance, x: self.delete_contact(x, contact))

            button = Button(text=contact, id=contact, size_hint_y=None, height=40)
            contact_grid.add_widget(main_button)
            contact_grid.add_widget(button)

            if contact in self.new_messages:
                col = self.new_messages[contact]
                if col:
                    label = Label(text=str(col), size_hint=(.1, .1))
                    contact_grid.add_widget(label)
            self.contacts_buttons.append(contact_grid)
            self.contacts_layout.add_widget(contact_grid)
            button.on_press = partial(self.go_to_chat, contact)

    def go_to_chat(self, contact_name):
        if self.client_transport.is_received_pubkey(contact_name):
            self.screen_manager.current = 'chat'
            chat = self.screen_manager.get_screen('chat')
            chat.load_chat(contact_name)
            self.new_messages[contact_name] = 0
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
        if sender in self.new_messages:
            self.new_messages[sender] += 1
        else:
            self.new_messages[sender] = 1
        self.update_contact_list(new_message=sender)

    def connect_contacts_signal(self, client_obj):
        client_obj.new_message_signal_contacts.connect(self.show_label)

    def show_screen(self, name):
        if name == 'Add contact':
            self.screen_manager.current = 'add_contact'

    def go_to_login(self):
        self.screen_manager.current = 'login'

    def delete_contact(self, name, user):
        if name == 'Delete':
            if self.client_transport.del_contact(user):
                text_title = 'Success!'
                text_label = 'Contact successfully removed.'
                self.create_message_window(text_title, text_label)
                self.update_contact_list()
            else:
                text_title = 'Error!'
                text_label = 'Lost server connection.'
                self.create_message_window(text_title, text_label, self.go_to_login)

    @staticmethod
    def create_message_window(text_title, text_label, ok_func=None):
        box = GridLayout(cols=1)
        label = Label(text=text_label,
                      size_hint=(1, 0.7))
        ok_button = Button(text='OK', size_hint=(0.5, 0.2))
        box.add_widget(label)
        box.add_widget(ok_button)
        popup = Popup(title=text_title,
                      content=box,
                      size_hint=(0.6, 0.6))
        if ok_func:
            ok_button.on_press = ok_func
        ok_button.bind(on_press=popup.dismiss)
        popup.open()



