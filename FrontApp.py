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

from BackApp import get_account, load_data, save_data, add_account


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

        # Message label
        self.message_label = Label(
            text="Welcome! Please login",
            size_hint=(0.9, 0.15),
            pos_hint={"center_x": 0.5, "top": 0.95},
            color=(1, 0.9, 0.8, 1),
            font_size=28
        )
        self.layout.add_widget(self.message_label)

        # Login screen widgets
        self.username_input = RoundedInput(
            hint_text="Username",
            size_hint=(0.7, None),
            height=70,
            pos_hint={"center_x": 0.5, "y": 0.55}
        )
        self.password_input = RoundedInput(
            hint_text="Password",
            password=True,
            size_hint=(0.7, None),
            height=70,
            pos_hint={"center_x": 0.5, "y": 0.42}
        )
        self.login_pass_toggle = Button(
            text="Show",
            size_hint=(0.10, 0.07),
            pos_hint={"x": 0.88, "y": 0.41}
        )
        self.login_btn = Button(
            text="Login",
            size_hint=(0.7, 0.12),
            pos_hint={"center_x": 0.5, "y": 0.25},
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=22
        )
        self.signup_btn = Button(
            text="Create Account",
            size_hint=(0.7, 0.12),
            pos_hint={"center_x": 0.5, "y": 0.1},
            background_color=(0.3, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=20
        )

        # Group login widgets so we can show/hide/re-add easily
        self.login_widgets = [self.username_input, self.password_input, self.login_pass_toggle, self.login_btn, self.signup_btn]
        for w in self.login_widgets:
            self.layout.add_widget(w)

        # Bind buttons
        self.login_btn.bind(on_press=self.login)
        self.login_pass_toggle.bind(on_press=self.toggle_login_password)
        self.signup_btn.bind(on_press=self.show_create_account)

        # Track active screen to control Enter behaviour
        # values: 'login', 'create_main', 'main', 'add_credential', 'details'
        self.current_screen = 'login'

        # Bind Enter key (global). We'll dispatch based on current_screen.
        Window.bind(on_key_down=self.on_key_down)

        # Widgets that are added/removed per-screen (kept in a list so clear_dynamic works)
        self.dynamic_widgets = []

        return self.layout

    # ---------------- ENTER KEY HANDLING ----------------
    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        # Enter key is 13 (desktop)
        if key != 13:
            return
        # Dispatch based on current screen
        if self.current_screen == 'login':
            # Enter triggers login
            self.login(None)
        elif self.current_screen == 'create_main':
            # Enter triggers create main account
            # ensure fields exist
            if hasattr(self, 'new_username') and hasattr(self, 'new_password'):
                self.create_new_account(None)
        elif self.current_screen == 'add_credential':
            # Option A: Enter saves the new credential
            if hasattr(self, 'acc_name') and hasattr(self, 'acc_pass'):
                self.save_account(None)
        # else: ignore

    # ---------------- LOGIN ----------------
    def toggle_login_password(self, instance):
        self.password_input.password = not self.password_input.password
        self.login_pass_toggle.text = "Hide" if not self.password_input.password else "Show"

    def login(self, instance):
        username = (self.username_input.text or '').strip()
        password = (self.password_input.text or '').strip()

        if not username:
            self.message_label.text = "Please enter username."
            return
        acc = get_account(username)
        if acc and acc.get("password") == password:
            self.logged_in_user = username
            self.message_label.text = f"Welcome, {username}!"

            # Remove login widgets from layout (we'll re-add on logout)
            for w in list(self.login_widgets):
                if w in self.layout.children:
                    self.layout.remove_widget(w)

            self.current_screen = 'main'
            self.show_main_interface()
        else:
            self.message_label.text = "Invalid username or password."

    # ---------------- MAIN INTERFACE ----------------
    def show_main_interface(self):
        # Logout button
        self.logout_btn = Button(
            text="Logout",
            size_hint=(0.2, 0.1),
            pos_hint={"right": 0.98, "top": 0.95},
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        self.logout_btn.bind(on_press=self.logout)
        self.layout.add_widget(self.logout_btn)

        # Add account (credential) button
        self.add_account_btn = Button(
            text="Add Account",
            size_hint=(0.7, 0.1),
            pos_hint={"center_x": 0.5, "y": 0.05},
            background_color=(0.3, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=22
        )
        self.add_account_btn.bind(on_press=self.show_add_account)
        self.layout.add_widget(self.add_account_btn)

        # Show credentials bubbles
        self.show_bubbles()

    def logout(self, instance):
        # Clear any dynamic screen widgets (details / add / bubbles / create main)
        self.clear_dynamic()

        # Remove persistent main buttons if present
        if hasattr(self, "logout_btn") and self.logout_btn in self.layout.children:
            self.layout.remove_widget(self.logout_btn)
        if hasattr(self, "add_account_btn") and self.add_account_btn in self.layout.children:
            self.layout.remove_widget(self.add_account_btn)

        # Re-add login widgets (if missing) and re-enable them
        for w in self.login_widgets:
            if w not in self.layout.children:
                self.layout.add_widget(w)
            w.opacity = 1
            w.disabled = False

        # Reset login-specific visuals/states
        self.password_input.password = True
        self.login_pass_toggle.text = "Show"
        self.username_input.text = ""
        self.password_input.text = ""
        self.message_label.text = "Welcome! Please login"
        self.current_screen = 'login'

    # ---------------- CREATE NEW APP USER ----------------
    def show_create_account(self, instance):
        # Enter create-main mode
        self.clear_dynamic()
        # hide login widgets visually (we keep them attached so Back/Logout can re-enable reliably)
        for w in self.login_widgets:
            w.opacity = 0
            w.disabled = True

        y = 0.6
        back = Button(
            text="Back",
            size_hint=(0.2, 0.1),
            pos_hint={"x": 0.02, "top": 0.95},
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1)
        )
        back.bind(on_press=self.back_to_login_from_create)
        self.layout.add_widget(back)
        self.dynamic_widgets.append(back)

        self.new_username = RoundedInput(
            hint_text="New Username",
            size_hint=(0.7, None),
            height=70,
            pos_hint={"center_x": 0.5, "center_y": y}
        )
        self.layout.add_widget(self.new_username)
        self.dynamic_widgets.append(self.new_username)

        self.new_password = RoundedInput(
            hint_text="New Password",
            password=True,
            size_hint=(0.7, None),
            height=70,
            pos_hint={"center_x": 0.5, "center_y": y - 0.13}
        )
        self.layout.add_widget(self.new_password)
        self.dynamic_widgets.append(self.new_password)

        self.new_pass_toggle = Button(
            text="Show",
            size_hint=(0.10, 0.07),
            pos_hint={"x": 0.88, "center_y": y - 0.13}
        )
        self.new_pass_toggle.bind(on_press=self.toggle_new_pass)
        self.layout.add_widget(self.new_pass_toggle)
        self.dynamic_widgets.append(self.new_pass_toggle)

        create_btn = Button(
            text="Create Account",
            size_hint=(0.7, 0.1),
            pos_hint={"center_x": 0.5, "y": 0.1},
            background_color=(0.3, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=22
        )
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

            # Remove login widgets (we'll log in as the created user)
            for w in list(self.login_widgets):
                if w in self.layout.children:
                    self.layout.remove_widget(w)

            # Log in immediately as new user
            self.logged_in_user = username
            self.clear_dynamic()
            self.current_screen = 'main'
            self.show_main_interface()
        else:
            self.message_label.text = f"Username '{username}' already exists."

    def back_to_login_from_create(self, *args):
        self.clear_dynamic()
        # restore login widgets for interaction
        for w in self.login_widgets:
            if w not in self.layout.children:
                self.layout.add_widget(w)
            w.opacity = 1
            w.disabled = False
        self.current_screen = 'login'

    # ---------------- ACCOUNT BUBBLES ----------------
    def show_bubbles(self):
        self.clear_dynamic()
        # we are in main screen
        self.current_screen = 'main'

        data = get_account(self.logged_in_user) or {}
        creds = data.get("credentials", [])

        self.scroll = ScrollView(size_hint=(0.9, 0.55), pos_hint={"center_x": 0.5, "y": 0.3})
        self.dynamic_widgets.append(self.scroll)

        self.box = BoxLayout(orientation="vertical", spacing=15, size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        self.layout.add_widget(self.scroll)

        for cred in creds:
            btn = Button(
                text=cred.get("website", ""),
                size_hint=(1, None),
                height=90,
                background_color=(0.4, 0.6, 0.8, 1),
                color=(1, 1, 1, 1),
                font_size=24
            )
            btn.bind(on_press=lambda inst, c=cred: self.show_details(c))
            self.box.add_widget(btn)

    # ---------------- DETAILS PAGE ----------------
    def show_details(self, cred):
        # show single credential details
        self.clear_dynamic()
        # hide the add_account_btn so it's visually not in the way
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 0
        self.current_screen = 'details'

        back = Button(
            text="Back",
            size_hint=(0.2, 0.1),
            pos_hint={"x": 0.02, "top": 0.95},
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1)
        )
        back.bind(on_press=self.back_to_bubbles)
        self.layout.add_widget(back)
        self.dynamic_widgets.append(back)

        y = 0.65
        font = 26

        L = Label(
            text=f"Website: {cred.get('website','')}",
            pos_hint={"center_x": 0.5, "center_y": y},
            size_hint=(0.8, 0.1),
            font_size=font,
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(L)
        self.dynamic_widgets.append(L)

        self.login_lbl = Label(
            text=f"Login: {'*' * len(cred.get('login',''))}",
            pos_hint={"center_x": 0.5, "center_y": y - 0.15},
            size_hint=(0.7, 0.1),
            font_size=font,
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.login_lbl)
        self.dynamic_widgets.append(self.login_lbl)

        self.login_toggle = Button(
            text="Show",
            size_hint=(0.15, 0.07),
            pos_hint={"x": 0.78, "center_y": y - 0.15}
        )
        self.login_toggle.bind(on_press=lambda inst: self.toggle_label(self.login_lbl, cred.get("login", ""), self.login_toggle))
        self.layout.add_widget(self.login_toggle)
        self.dynamic_widgets.append(self.login_toggle)

        self.pass_lbl = Label(
            text=f"Password: {'*' * len(cred.get('password',''))}",
            pos_hint={"center_x": 0.5, "center_y": y - 0.28},
            size_hint=(0.7, 0.1),
            font_size=font,
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.pass_lbl)
        self.dynamic_widgets.append(self.pass_lbl)

        self.detail_pass_toggle = Button(
            text="Show",
            size_hint=(0.15, 0.07),
            pos_hint={"x": 0.78, "center_y": y - 0.28}
        )
        self.detail_pass_toggle.bind(on_press=lambda inst: self.toggle_label(self.pass_lbl, cred.get("password", ""), self.detail_pass_toggle))
        self.layout.add_widget(self.detail_pass_toggle)
        self.dynamic_widgets.append(self.detail_pass_toggle)

    def toggle_label(self, lbl, value, toggle_btn):
        text = lbl.text.split(": ")[0]
        if lbl.text.endswith("*" * len(value)):
            lbl.text = f"{text}: {value}"
            toggle_btn.text = "Hide"
        else:
            lbl.text = f"{text}: {'*' * len(value)}"
            toggle_btn.text = "Show"

    def back_to_bubbles(self, *args):
        # restore add_account_btn
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 1
        self.show_bubbles()

    # ---------------- ADD ACCOUNT (credential) ----------------
    def show_add_account(self, instance):
        self.clear_dynamic()
        # visually hide login widgets while still present (so Back/Logout works)
        for w in self.login_widgets:
            w.opacity = 0
            w.disabled = True

        # hide main add button so it doesn't overlap
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 0

        back = Button(
            text="Back",
            size_hint=(0.2, 0.1),
            pos_hint={"x": 0.02, "top": 0.95},
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1)
        )
        back.bind(on_press=self.back_to_bubbles_from_add)
        self.layout.add_widget(back)
        self.dynamic_widgets.append(back)

        y = 0.7
        self.acc_name = RoundedInput(
            hint_text="Account / Website Name",
            size_hint=(0.7, None),
            height=70,
            pos_hint={"center_x": 0.5, "center_y": y}
        )
        self.layout.add_widget(self.acc_name)
        self.dynamic_widgets.append(self.acc_name)

        self.acc_user = RoundedInput(
            hint_text="User / Email / Phone",
            size_hint=(0.7, None),
            height=70,
            pos_hint={"center_x": 0.5, "center_y": y - 0.13}
        )
        self.layout.add_widget(self.acc_user)
        self.dynamic_widgets.append(self.acc_user)

        self.acc_pass = RoundedInput(
            hint_text="Password",
            password=True,
            size_hint=(0.7, None),
            height=70,
            pos_hint={"center_x": 0.5, "center_y": y - 0.26}
        )
        self.layout.add_widget(self.acc_pass)
        self.dynamic_widgets.append(self.acc_pass)

        self.add_pass_toggle = Button(
            text="Show",
            size_hint=(0.10, 0.07),
            pos_hint={"x": 0.88, "center_y": y - 0.26}
        )
        self.add_pass_toggle.bind(on_press=self.toggle_add_pass)
        self.layout.add_widget(self.add_pass_toggle)
        self.dynamic_widgets.append(self.add_pass_toggle)

        gen = Button(
            text="Generate Password",
            size_hint=(0.6, 0.1),
            pos_hint={"center_x": 0.5, "center_y": y - 0.38},
            background_color=(0.8, 0.4, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=20
        )
        gen.bind(on_press=lambda *args: setattr(self.acc_pass, "text", "complex_password"))
        self.layout.add_widget(gen)
        self.dynamic_widgets.append(gen)

        save_btn = Button(
            text="Save Account",
            size_hint=(0.7, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.07},
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=22
        )
        save_btn.bind(on_press=self.save_account)
        self.layout.add_widget(save_btn)
        self.dynamic_widgets.append(save_btn)

        # Enter should save (Option A). Set screen flag
        self.current_screen = 'add_credential'

    def toggle_add_pass(self, instance):
        self.acc_pass.password = not self.acc_pass.password
        instance.text = "Hide" if not self.acc_pass.password else "Show"

    def back_to_bubbles_from_add(self, *args):
        self.clear_dynamic()
        # restore add account button
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 1
        # restore login widgets
        for w in self.login_widgets:
            w.opacity = 1
            w.disabled = False
        self.show_bubbles()

    def save_account(self, instance):
        # Save credential under current logged_in_user
        name = (self.acc_name.text or '').strip()
        user = (self.acc_user.text or '').strip()
        pwd = (self.acc_pass.text or '').strip()

        if not name:
            self.message_label.text = "Account name required!"
            return

        data = load_data()
        for acc in data.get("accounts", []):
            if acc.get("username") == self.logged_in_user:
                acc.setdefault("credentials", []).append({"website": name, "login": user, "password": pwd})
                break
        save_data(data)
        self.message_label.text = f"Account '{name}' saved!"

        # After saving go back to bubbles
        self.back_to_bubbles_from_add()

    # ---------------- UTIL ----------------
    def clear_dynamic(self):
        # remove widgets created for temporary screens (create main / add credential / details / bubbles)
        for w in list(self.dynamic_widgets):
            if w in self.layout.children:
                self.layout.remove_widget(w)
        self.dynamic_widgets = []

        # also remove scroll/box if present (bubbles)
        if hasattr(self, 'scroll') and self.scroll in self.layout.children:
            self.layout.remove_widget(self.scroll)
        # don't delete persistent main buttons here (logout/add_account) — other flows remove them explicitly if needed

        # reset current_screen to main/login depending on presence of logout_btn
        # but don't change if user intentionally set it elsewhere
        if hasattr(self, 'logout_btn') and self.logout_btn in self.layout.children:
            self.current_screen = 'main'
        else:
            # default to login if no logout button present
            self.current_screen = 'login'

    # run
if __name__ == "__main__":
    PasswordManager().run()
