import re
import datetime
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.dropdown import DropDown
from gui_kivy.color_label import CLabel
from gui_kivy.message_window import create_message_window


class ChatScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super(ChatScreen, self).__init__(**kwargs)

        self.screen_manager = screen_manager
        self.database = None
        self.client_transport = None
        self.contact = None
        self.client_login = None

        self.main_layout = GridLayout(cols=1)

        self.header_layout = GridLayout(cols=3, size_hint=(1, 0.1))
        self.scroll_view = ScrollView(size_hint=(1, 0.8), size=(100, 100), scroll_y=0)
        self.footer_layout = GridLayout(cols=2, size_hint=(1, 0.1))

        self.contact_list_button = Button(text='<=', size_hint=(0.1, 1))
        self.contact_list_button.on_press = self.go_to_contact_list
        self.label = CLabel(text="Chat with bla bla", size_hint=(0.9, 1))

        self.contact_menu = DropDown()
        for name in ['Info', 'Delete']:
            btn = Button(text=f'{name}', size_hint_y=None, height=30)
            btn.bind(on_release=lambda btn: self.contact_menu.select(btn.text))
            self.contact_menu.add_widget(btn)
        self.main_button = Button(text=':', size_hint=(.1, .3))
        self.main_button.bind(on_release=self.contact_menu.open)

        self.contact_menu.bind(on_select=lambda instance, x: self.menu_contact(x))

        self.messages = []
        self.messages_layout = GridLayout(cols=1, padding=(30, 0, 30, 0),
                                          size_hint_y=None, row_force_default=True,
                                          row_default_height=40)
        self.messages_layout.bind(minimum_height=self.messages_layout.setter('height'))

        self.scroll_view.add_widget(self.messages_layout)

        self.text_input = TextInput(size_hint=(0.9, 1))
        self.send_button = Button(text='>>', size_hint=(0.1, 1))
        self.send_button.on_press = self.send_message

        self.header_layout.add_widget(self.contact_list_button)
        self.header_layout.add_widget(self.label)
        self.header_layout.add_widget(self.main_button)

        self.footer_layout.add_widget(self.text_input)
        self.footer_layout.add_widget(self.send_button)

        self.main_layout.add_widget(self.header_layout)
        self.main_layout.add_widget(self.scroll_view)
        self.main_layout.add_widget(self.footer_layout)

        self.add_widget(self.main_layout)

    def send_message(self):
        message_text = self.text_input.text
        if message_text:
            is_success = self.client_transport.send_user_message(self.contact, message_text)
            self.text_input.text = ''
            if not is_success:
                self.show_info_screen('Lost server connection!', 'login')
            elif is_success is True:
                self.add_message_history(message_text)
            else:
                self.show_info_screen(is_success, 'contacts')

    def show_info_screen(self, *args):
        self.screen_manager.current = 'info'
        self.screen_manager.get_screen('info').set_message(*args)

    def go_to_contact_list(self):
        self.screen_manager.current = 'contacts'

    def load_chat(self, contact_name):
        self.contact = contact_name
        if self.client_transport.is_received_pubkey(contact_name):
            self.show_history()
        else:
            self.clear_messages()

    def set_objects(self, database, client_transport):
        self.database = database
        self.client_transport = client_transport
        self.client_login = self.client_transport.client_login

    def clear_messages(self):
        for msg in self.messages:
            self.messages_layout.remove_widget(msg)

        self.messages.clear()

        self.label.text = f'Chat with {self.contact}'

    def show_history(self):
        self.clear_messages()

        list_message = sorted(self.database.get_history(self.contact),
                              key=lambda item: item[3])  # sort by date

        length = len(list_message)
        start_index = 0
        if length > 20:
            start_index = length - 20

        for i in range(start_index, length):
            item = list_message[i]
            message = re.findall(r'>([^<>]+)</p|>([^<>]+)</span', item[2])
            if message:
                message = message[0][0]
            else:
                message = item[2]

            if item[1] == 'in':
                time = f'{self.contact}' \
                    f' {item[3].replace(microsecond=0)}:'
                label = Label(text=f"{time}\n{message}",
                              color=[0.7, 0.3, 1, 0.8],
                              halign='right',
                              valign='middle')
                label.bind(size=label.setter('text_size'))
                self.messages.append(label)
                self.messages_layout.add_widget(self.messages[-1])

            elif item[1] == 'out':
                time = f'{self.client_login}' \
                    f' {item[3].replace(microsecond=0)}:'
                label = Label(text=f"{time}\n{message}",
                              color=[0.8, 1, .3, 0.7],
                              halign='left',
                              valign='middle')
                label.bind(size=label.setter('text_size'))
                self.messages.append(label)
                self.messages_layout.add_widget(self.messages[-1])

    def add_message_history(self, message):
        time = f'{self.client_login}' \
            f' {datetime.datetime.now().replace(microsecond=0)}:'
        label = Label(text=f"{time}\n{message}",
                      color=[0.8, 1, .3, 0.7],
                      halign='left',
                      valign='middle')
        label.bind(size=label.setter('text_size'))
        self.messages.append(label)
        self.messages_layout.add_widget(self.messages[-1])

    def get_message(self, *args):
        if self.screen_manager.current == 'chat':
            sender = args[0]
            if sender == self.contact:
                self.show_history()
            else:
                if self.database.is_contact(sender):
                    text_title = f'New message from {sender}'
                    text_label = f'Received a new message from {sender}, open chat with him?'
                    create_message_window(text_title, text_label, self.open_new_chat, sender)
                else:
                    text_title = f'New message from {sender}'
                    text_label = f'Received a new message from {sender}.\n ' \
                                 f'This user is not in your contact list.\n ' \
                                 f'Add to contacts and open a chat with him?'

                    create_message_window(text_title, text_label, self.add_contact, sender)

    def add_contact(self, sender):
        if self.client_transport.add_contact(sender):
            text_title = 'Info message'
            text_label = f'Contact {sender} successfully added.'
            create_message_window(text_title, text_label, self.open_new_chat, sender)
        else:
            text_title = 'Info message'
            text_label = f'Lost server connection!.'
            create_message_window(text_title, text_label, self.show_login_screen)

    def open_new_chat(self, sender):
        self.load_chat(sender)

    def connect_chat_signal(self, client_obj):
        client_obj.new_message_signal_chat.connect(self.get_message)

    def show_login_screen(self):
        self.screen_manager.current = 'login'

    def menu_contact(self, button):
        if button == 'Delete':
            if self.client_transport.del_contact(self.contact):
                text_title = 'Success!'
                text_label = 'Contact successfully removed.'
                create_message_window(text_title, text_label)
                self.update_contact_list()
            else:
                text_title = 'Error!'
                text_label = 'Lost server connection.'
                create_message_window(text_title, text_label, self.go_to_login)
        elif button == 'Info':
            self.screen_manager.current = 'contact_info'
            self.screen_manager.get_screen('contact_info').get_contact_name(self.contact)
