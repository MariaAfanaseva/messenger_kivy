from functools import partial
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label


def create_message_window(text_title, text_label, ok_func=None, sender=None):
    box = GridLayout(cols=1)
    label = Label(text=text_label,
                  size_hint=(1, 0.7))
    ok_button = Button(text='OK', size_hint=(0.5, 0.2))
    box.add_widget(label)
    box.add_widget(ok_button)
    popup = Popup(title=text_title,
                  content=box,
                  size_hint=(0.6, 0.6))
    if ok_func and sender:
        ok_button.on_press = partial(ok_func, sender)
    elif ok_func and not sender:
        ok_button.on_press = ok_func
    ok_button.bind(on_press=popup.dismiss)
    popup.open()
