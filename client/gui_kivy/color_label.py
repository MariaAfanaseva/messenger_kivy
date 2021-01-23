from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label


class CLabel(Label):
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 0, 0, 0.5)
            Rectangle(pos=self.pos, size=self.size)
