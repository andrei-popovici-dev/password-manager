from kivy.config import Config
# make the app not resizeable to keep GUI looking clean
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '700')

from kivy.app import App
from kivy.uix import layout
from kivy.uix.behaviors import DragBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.widget import Widget
from TextInputApp import TextInputBox

class PasswordManager(App):
    def build(self):
        layout = FloatLayout()

        Window.clearcolor = (0,0,1,1)
        # Label feedback
        self.message_label = Label(
            text='Hello!',
            size_hint=(0.8, 0.1),
            pos_hint={'x':0.3, 'y':0.75},
            color=(1,1,1,1),
            font_size = 24
        )
        layout.add_widget(self.message_label)

        # Username
        self.username_input = TextInputBox(x = 0.05,y = 0.83,hint = 'Username')

        layout.add_widget(self.username_input)

        # Password
        self.password_input = TextInputBox(x = 0.05,y = 0.70,hint = 'Password',password = True)
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
        self.show_btn = Button(
            text='Show',
            size_hint=(0.25,0.1),
            pos_hint={'x':0.37, 'y':0.3}
        )
        self.show_btn.bind(on_press=self.show_password)
        layout.add_widget(self.show_btn)

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
        self.show_btn.text = 'Hide' if not self.password_input.password else 'Show'
        
    def generate_password(self, instance):
        import random, string
        self.password_input.text = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        self.message_label.text = 'Generated!'


if __name__ == '__main__':
    PasswordManager().run()
