from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from client_main import start_client


class LoginScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        self.screen_manager = screen_manager

        self.main_layout = GridLayout(cols=1, padding=(50, 0, 50, 0), spacing=(10, 10))

        self.main_layout.add_widget(Label(size_hint=(1, 0.4)))

        self.login_input = TextInput(hint_text='Enter your name', multiline=False, size_hint=(1, 0.1))
        self.main_layout.add_widget(self.login_input)

        self.password_input = TextInput(hint_text='Enter your password', password=True,
                                        multiline=False, size_hint=(0.5, 0.1))
        self.main_layout.add_widget(self.password_input)

        self.login_button = Button(text='Login', size_hint=(0.8, 0.1))
        self.main_layout.add_widget(self.login_button)

        self.main_layout.add_widget(Label(size_hint=(1, 0.3)))

        self.add_widget(self.main_layout)

        self.login_button.on_press = self.go_to_loading

    def go_to_loading(self):
        if self.login_input.text and self.password_input.text:
            database, client_transport = start_client(self.login_input.text, self.password_input.text,
                                                      self.screen_manager)
            self.screen_manager.current = 'loading'
            self.screen_manager.get_screen('contacts').set_objects(database, client_transport)
            self.screen_manager.get_screen('chat').set_objects(database, client_transport)
            self.screen_manager.get_screen('add_contact').set_objects(database, client_transport)
