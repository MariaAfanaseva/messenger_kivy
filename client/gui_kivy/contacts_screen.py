from functools import partial
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label


class ContactScreen(Screen):
    class CLabel(Label):
        def on_size(self, *args):
            self.canvas.before.clear()
            with self.canvas.before:
                Color(1, 0, 0, 0.5)
                Rectangle(pos=self.pos, size=self.size)

    def __init__(self, screen_manager, **kwargs):
        super(ContactScreen, self).__init__(**kwargs)

        self.screen_manager = screen_manager

        self.contacts_buttons = []
        self.database = None
        self.client_transport = None

        self.contacts_layout = GridLayout(cols=1, size_hint_y=None, row_force_default=True, row_default_height=40)
        self.contacts_layout.bind(minimum_height=self.contacts_layout.setter('height'))

        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.scroll_view.add_widget(self.contacts_layout)

        self.add_widget(self.scroll_view)
        #  befor show
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

    def get_contact_list(self):
        contacts_list = self.database.get_contacts()
        return contacts_list

    def show_label(self, *args):
        sender = args[0]
        self.update_contact_list(new_message=sender)

    def connect_contacts_signal(self, client_obj):
        client_obj.new_message_signal_contacts.connect(self.show_label)
