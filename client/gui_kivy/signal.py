from kivy.event import EventDispatcher


class KivySignal(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_emit')
        super(KivySignal, self).__init__(**kwargs)
        self._callback = None

    def connect(self, callback):
        self._callback = callback

    def emit(self, *args):
        self.dispatch('on_emit', *args)

    def on_emit(self, *args):
        if self._callback:
            self._callback(*args)


if __name__ == "__main__":
    def foo(*args):
        print('args:', *args)

    sig = KivySignal()
    sig.connect(foo)
    sig.emit(123)
