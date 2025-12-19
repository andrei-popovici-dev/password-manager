from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '600')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

from BackApp import add_account, get_account, verify_main_password, add_credential, decrypt_credential

# ---------------- Reusable Rounded Input ----------------
class RoundedInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.2, 0.3, 1)
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = (1, 1, 1, 1)
        self.padding = [15, 15, 15, 15]
        self.font_size = 20
        self.multiline = False
        self.background_normal = ''
        self.background_active = ''


# ---------------- Main App ----------------
class PasswordManager(App):
    def build(self):
        self.layout = FloatLayout()
        Window.clearcolor = (0.1, 0.1, 0.2, 1)

        self.message_label = Label(
            text="Welcome! Please login",
            size_hint=(0.9, 0.15),
            pos_hint={"center_x": 0.5, "top": 0.95},
            color=(1, 0.9, 0.8, 1),
            font_size=28
        )
        self.layout.add_widget(self.message_label)

        self.username_input = RoundedInput(hint_text="Username", size_hint=(0.7, None), height=70, pos_hint={"center_x": 0.5, "y": 0.55})
        self.password_input = RoundedInput(hint_text="Password", password=True, size_hint=(0.7, None), height=70, pos_hint={"center_x": 0.5, "y": 0.42})
        self.login_pass_toggle = Button(text="Show", size_hint=(0.10, 0.07), pos_hint={"x": 0.88, "y": 0.41})
        self.login_btn = Button(text="Login", size_hint=(0.7, 0.12), pos_hint={"center_x": 0.5, "y": 0.25}, background_color=(0.2,0.6,0.8,1), font_size=22)
        self.signup_btn = Button(text="Create Account", size_hint=(0.7,0.12), pos_hint={"center_x":0.5, "y":0.1}, background_color=(0.3,0.7,0.4,1), font_size=20)

        self.login_widgets = [self.username_input, self.password_input, self.login_pass_toggle, self.login_btn, self.signup_btn]
        for w in self.login_widgets:
            self.layout.add_widget(w)

        self.login_btn.bind(on_press=self.login)
        self.login_pass_toggle.bind(on_press=self.toggle_login_password)
        self.signup_btn.bind(on_press=self.show_create_account)

        self.current_screen = 'login'
        Window.bind(on_key_down=self.on_key_down)
        self.dynamic_widgets = []

        return self.layout

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key != 13:
            return
        if self.current_screen == 'login':
            self.login(None)
        elif self.current_screen == 'create_main':
            if hasattr(self, 'new_username') and hasattr(self, 'new_password'):
                self.create_new_account(None)
        elif self.current_screen == 'add_credential':
            if hasattr(self, 'acc_name') and hasattr(self, 'acc_pass'):
                self.save_account(None)

    # ---------------- LOGIN ----------------
    def toggle_login_password(self, instance):
        self.password_input.password = not self.password_input.password
        self.login_pass_toggle.text = "Hide" if not self.password_input.password else "Show"

    def login(self, instance):
        username = (self.username_input.text or '').strip()
        password = (self.password_input.text or '').strip()
        if not username or not password:
            self.message_label.text = "Username and password required!"
            return

        if verify_main_password(username, password):
            self.logged_in_user = username
            self.main_password = password
            self.message_label.text = f"Welcome, {username}!"

            for w in list(self.login_widgets):
                if w in self.layout.children:
                    self.layout.remove_widget(w)

            self.current_screen = 'main'
            self.show_main_interface()
        else:
            self.message_label.text = "Invalid username or password."

    # ---------------- CREATE ACCOUNT ----------------
    def show_create_account(self, instance):
        self.clear_dynamic()
        for w in self.login_widgets:
            w.opacity = 0
            w.disabled = True

        y = 0.6
        back = Button(text="Back", size_hint=(0.2,0.1), pos_hint={"x":0.02,"top":0.95})
        back.bind(on_press=self.back_to_login_from_create)
        self.layout.add_widget(back)
        self.dynamic_widgets.append(back)

        self.new_username = RoundedInput(hint_text="New Username", size_hint=(0.7,None), height=70, pos_hint={"center_x":0.5,"center_y":y})
        self.layout.add_widget(self.new_username)
        self.dynamic_widgets.append(self.new_username)

        self.new_password = RoundedInput(hint_text="New Password", password=True, size_hint=(0.7,None), height=70, pos_hint={"center_x":0.5,"center_y":y-0.13})
        self.layout.add_widget(self.new_password)
        self.dynamic_widgets.append(self.new_password)

        self.new_pass_toggle = Button(text="Show", size_hint=(0.10,0.07), pos_hint={"x":0.88,"center_y":y-0.13})
        self.new_pass_toggle.bind(on_press=self.toggle_new_pass)
        self.layout.add_widget(self.new_pass_toggle)
        self.dynamic_widgets.append(self.new_pass_toggle)

        create_btn = Button(text="Create Account", size_hint=(0.7,0.1), pos_hint={"center_x":0.5,"y":0.1}, background_color=(0.3,0.7,0.4,1))
        create_btn.bind(on_press=self.create_new_account)
        self.layout.add_widget(create_btn)
        self.dynamic_widgets.append(create_btn)

        self.current_screen = 'create_main'

    def toggle_new_pass(self, instance):
        self.new_password.password = not self.new_password.password
        instance.text = "Hide" if not self.new_password.password else "Show"

    def create_new_account(self, instance):
        username = (self.new_username.text or '').strip()
        password = (self.new_password.text or '').strip()
        if not username or not password:
            self.message_label.text = "Username and password required!"
            return
        if add_account(username, password):
            self.message_label.text = f"Account '{username}' created!"
            for w in list(self.login_widgets):
                if w in self.layout.children:
                    self.layout.remove_widget(w)
            self.logged_in_user = username
            self.main_password = password
            self.clear_dynamic()
            self.current_screen = 'main'
            self.show_main_interface()
        else:
            self.message_label.text = f"Username '{username}' already exists."

    def back_to_login_from_create(self, *args):
        self.clear_dynamic()
        for w in self.login_widgets:
            if w not in self.layout.children:
                self.layout.add_widget(w)
            w.opacity = 1
            w.disabled = False
        self.current_screen = 'login'

    # ---------------- MAIN INTERFACE ----------------
    def show_main_interface(self):
        # Logout button
        self.logout_btn = Button(text="Logout", size_hint=(0.2,0.1), pos_hint={"right":0.98,"top":0.95}, background_color=(0.8,0.2,0.2,1))
        self.logout_btn.bind(on_press=self.logout)
        self.layout.add_widget(self.logout_btn)

        # Add credential button
        self.add_account_btn = Button(text="Add Account", size_hint=(0.7,0.1), pos_hint={"center_x":0.5,"y":0.05}, background_color=(0.3,0.7,0.4,1), font_size=22)
        self.add_account_btn.bind(on_press=self.show_add_account)
        self.layout.add_widget(self.add_account_btn)

        self.show_bubbles()

    def logout(self, instance):
        self.clear_dynamic()
        if hasattr(self, "logout_btn") and self.logout_btn in self.layout.children:
            self.layout.remove_widget(self.logout_btn)
        if hasattr(self, "add_account_btn") and self.add_account_btn in self.layout.children:
            self.layout.remove_widget(self.add_account_btn)
        for w in self.login_widgets:
            if w not in self.layout.children:
                self.layout.add_widget(w)
            w.opacity = 1
            w.disabled = False
        self.password_input.password = True
        self.login_pass_toggle.text = "Show"
        self.username_input.text = ""
        self.password_input.text = ""
        self.message_label.text = "Welcome! Please login"
        self.current_screen = 'login'

    # ---------------- ADD / SAVE CREDENTIAL ----------------
    def show_add_account(self, instance):
        self.clear_dynamic()
        for w in self.login_widgets:
            w.opacity = 0
            w.disabled = True
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 0

        back = Button(text="Back", size_hint=(0.2,0.1), pos_hint={"x":0.02,"top":0.95})
        back.bind(on_press=self.back_to_bubbles_from_add)
        self.layout.add_widget(back)
        self.dynamic_widgets.append(back)

        y = 0.7
        self.acc_name = RoundedInput(hint_text="Account / Website Name", size_hint=(0.7,None), height=70, pos_hint={"center_x":0.5,"center_y":y})
        self.layout.add_widget(self.acc_name)
        self.dynamic_widgets.append(self.acc_name)

        self.acc_user = RoundedInput(hint_text="User / Email / Phone", size_hint=(0.7,None), height=70, pos_hint={"center_x":0.5,"center_y":y-0.13})
        self.layout.add_widget(self.acc_user)
        self.dynamic_widgets.append(self.acc_user)

        self.acc_pass = RoundedInput(hint_text="Password", password=True, size_hint=(0.7,None), height=70, pos_hint={"center_x":0.5,"center_y":y-0.26})
        self.layout.add_widget(self.acc_pass)
        self.dynamic_widgets.append(self.acc_pass)

        self.add_pass_toggle = Button(text="Show", size_hint=(0.10,0.07), pos_hint={"x":0.88,"center_y":y-0.26})
        self.add_pass_toggle.bind(on_press=self.toggle_add_pass)
        self.layout.add_widget(self.add_pass_toggle)
        self.dynamic_widgets.append(self.add_pass_toggle)

        save_btn = Button(text="Save Account", size_hint=(0.7,0.1), pos_hint={"center_x":0.5,"center_y":0.07}, background_color=(0.2,0.6,0.8,1), font_size=22)
        save_btn.bind(on_press=self.save_account)
        self.layout.add_widget(save_btn)
        self.dynamic_widgets.append(save_btn)

        self.current_screen = 'add_credential'

    def toggle_add_pass(self, instance):
        self.acc_pass.password = not self.acc_pass.password
        instance.text = "Hide" if not self.acc_pass.password else "Show"

    def save_account(self, instance):
        name = (self.acc_name.text or '').strip()
        user = (self.acc_user.text or '').strip()
        pwd = (self.acc_pass.text or '').strip()

        if not name:
            self.message_label.text = "Account name required!"
            return

        add_credential(self.logged_in_user, name, user, pwd, self.main_password)
        self.message_label.text = f"Account '{name}' saved!"
        self.back_to_bubbles_from_add()

    # ---------------- BUBBLES ----------------
    def show_bubbles(self):
        self.clear_dynamic()
        self.current_screen = 'main'
        acc = get_account(self.logged_in_user)
        creds = acc.get("credentials", []) if acc else []

        self.scroll = ScrollView(size_hint=(0.9,0.55), pos_hint={"center_x":0.5,"y":0.3})
        self.dynamic_widgets.append(self.scroll)
        self.box = BoxLayout(orientation="vertical", spacing=15, size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        self.layout.add_widget(self.scroll)

        for cred in creds:
            btn = Button(text=cred.get("website",""), size_hint=(1,None), height=90, background_color=(0.4,0.6,0.8,1), font_size=24)
            btn.bind(on_press=lambda inst, c=cred: self.show_details(c))
            self.box.add_widget(btn)

    def show_details(self, cred):
        self.clear_dynamic()
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 0
        self.current_screen = 'details'

        back = Button(text="Back", size_hint=(0.2,0.1), pos_hint={"x":0.02,"top":0.95})
        back.bind(on_press=self.back_to_bubbles)
        self.layout.add_widget(back)
        self.dynamic_widgets.append(back)

        y = 0.65
        font = 26

        L = Label(text=f"Website: {cred.get('website','')}", pos_hint={"center_x":0.5,"center_y":y}, size_hint=(0.8,0.1), font_size=font)
        self.layout.add_widget(L)
        self.dynamic_widgets.append(L)

        self.login_lbl = Label(text=f"Login: {cred.get('login','')}", pos_hint={"center_x":0.5,"center_y":y-0.15}, size_hint=(0.7,0.1), font_size=font)
        self.layout.add_widget(self.login_lbl)
        self.dynamic_widgets.append(self.login_lbl)

        decrypted_pwd = decrypt_credential(get_account(self.logged_in_user), cred, self.main_password)

        self.pass_lbl = Label(text=f"Password: {'*'*len(decrypted_pwd)}", pos_hint={"center_x":0.5,"center_y":y-0.28}, size_hint=(0.7,0.1), font_size=font)
        self.layout.add_widget(self.pass_lbl)
        self.dynamic_widgets.append(self.pass_lbl)

        self.detail_pass_toggle = Button(text="Show", size_hint=(0.15,0.07), pos_hint={"x":0.78,"center_y":y-0.28})
        self.detail_pass_toggle.bind(on_press=lambda inst: self.toggle_label(self.pass_lbl, decrypted_pwd, self.detail_pass_toggle))
        self.layout.add_widget(self.detail_pass_toggle)
        self.dynamic_widgets.append(self.detail_pass_toggle)

    def toggle_label(self, lbl, value, toggle_btn):
        text = lbl.text.split(": ")[0]
        if lbl.text.endswith("*"*len(value)):
            lbl.text = f"{text}: {value}"
            toggle_btn.text = "Hide"
        else:
            lbl.text = f"{text}: {'*'*len(value)}"
            toggle_btn.text = "Show"

    def back_to_bubbles_from_add(self, *args):
        self.clear_dynamic()
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 1
        for w in self.login_widgets:
            w.opacity = 1
            w.disabled = False
        self.show_bubbles()

    def back_to_bubbles(self, *args):
        self.clear_dynamic()
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 1
        self.show_bubbles()

    # ---------------- UTIL ----------------
    def clear_dynamic(self):
        for w in self.dynamic_widgets:
            if w in self.layout.children:
                self.layout.remove_widget(w)
        self.dynamic_widgets = []


if __name__ == "__main__":
    PasswordManager().run()
