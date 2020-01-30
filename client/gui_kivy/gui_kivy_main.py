from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from gui_kivy.login_screen import LoginScreen
from gui_kivy.chat_screen import ChatScreen
from gui_kivy.contacts_screen import ContactScreen
from gui_kivy.loading_screen import LoadingScreen
from gui_kivy.info_screen import InfoScreen

sm = ScreenManager()
sm.add_widget(LoginScreen(sm, name='login'))
sm.add_widget(LoadingScreen(sm, name='loading'))
sm.add_widget(ContactScreen(sm, name='contacts'))
sm.add_widget(ChatScreen(sm, name='chat'))
sm.add_widget(InfoScreen(sm, name='info'))


class MessengerApp(App):
    def build(self):
        return sm


if __name__ == '__main__':
    MessengerApp().run()
