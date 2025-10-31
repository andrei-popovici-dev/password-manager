from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.widget import Widget

class PositionedPasswordManager(App):
    def build(self):
        layout = FloatLayout()

        Window.clearcolor = (0,0,1,1)
        # Label feedback
        self.message_label = Label(
            text='',
            size_hint=(0.8, 0.1),
            pos_hint={'x':0.1, 'y':0.85},
            color=(1,1,1,1)
        )
        layout.add_widget(self.message_label)

        # Username
        self.username_input = self.create_text_input(0.2,0.65,'Username')

        self.username_input.on_cursor()

        layout.add_widget(self.username_input)

        # Password
        self.password_input = self.create_text_input(0.2,0.5,'Password')
        layout.add_widget(self.password_input)

        # Save Button
        save_btn = Button(
            text='Save',
            size_hint=(0.25,0.1),
            pos_hint={'x':0.1, 'y':0.3}
        )
        save_btn.bind(on_press=self.save_password)
        layout.add_widget(save_btn)

        # Show Password
        show_btn = Button(
            text='Show',
            size_hint=(0.25,0.1),
            pos_hint={'x':0.37, 'y':0.3}
        )
        show_btn.bind(on_press=self.show_password)
        layout.add_widget(show_btn)

        # Generate
        generate_btn = Button(
            text='Generate',
            size_hint=(0.25,0.1),
            pos_hint={'x':0.64, 'y':0.3}
        )
        generate_btn.bind(on_press=self.generate_password)
        layout.add_widget(generate_btn)

        return layout

    def save_password(self, instance):
        self.message_label.text = 'Saved!'

    def show_password(self, instance):
        self.password_input.password = not self.password_input.password

    def generate_password(self, instance):
        import random, string
        self.password_input.text = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        self.message_label.text = 'Generated!'

    def create_text_input(self,x,y,hint_text):
        return TextInput(
            hint_text=hint_text,
            multiline=False,
            background_normal='Photos/GroupedList.png',  # imagine ta când nu e selectat
            background_active='Photos/GroupedList.png',  # imagine când e focusat
            size_hint=(0.6, 0.1),
            padding_y=(15, 15),  # sus, jos
            padding_x=10,
            font_size=24,
            _cursor_blink=True,
            cursor_color=(0, 0, 0, 1),
            cursor_blink=True,
            pos_hint={'x': x, 'y': y},
            foreground_color=(0, 0, 0, 1),)  # text negru


if __name__ == '__main__':
    PositionedPasswordManager().run()
