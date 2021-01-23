from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.progressbar import ProgressBar


class LoadingScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super(LoadingScreen, self).__init__(**kwargs)

        self.screen_manager = screen_manager
        self.main_layout = GridLayout(cols=1, padding=(100, 0, 100, 0))
        self.add_widget(self.main_layout)

        self.progressbar = ProgressBar(max=100)
        self.progressbar.value = 0
        self.main_layout.add_widget(self.progressbar)

    def change_progressbar_value(self):
        self.progressbar.value += 20
        if self.progressbar.value == 100:
            self.screen_manager.current = 'contacts'

    def show_info_screen(self, *args):
        self.screen_manager.current = 'info'
        self.screen_manager.get_screen('info').set_message(*args)

    def connect_loading_signal(self, client_obj):
        client_obj.progressbar_signal.connect(self.change_progressbar_value)
        client_obj.answer_server.connect(self.show_info_screen)
