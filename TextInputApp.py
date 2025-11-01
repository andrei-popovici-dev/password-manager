from kivy.uix.textinput import TextInput


class TextInputBox(TextInput):
    def __init__(self, **kwargs):
        super().__init__(
            multiline=False,
            background_normal='Photos/TextBox.png',  # imagine ta când nu e selectat
            background_active='Photos/TextBox.png',  # imagine când e focusat
            size_hint = [None, None],
            width = 300,
            height = 50,
            cursor_color=(0, 0, 0, 1),
            cursor_blink=True,
            font_size = 16,
            padding_y=(14, 10),
            padding_x=10
        )  # text negru
        self.pos_hint = {'x' : kwargs.get('x', None,),'y' : kwargs.get('y', None,)}
        self.password = kwargs.get('password', False)
        self.hint_text = kwargs.get('hint', '')

