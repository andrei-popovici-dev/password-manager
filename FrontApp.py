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
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.core.clipboard import Clipboard

import random
import string

from BackApp import add_account, get_account, verify_main_password, add_credential, decrypt_credential, delete_credential

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

        # Fereastra intiala de login
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

    # Shortcut pentru user - Enter key to submit
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
        elif self.current_screen == 'edit_credential':
            if hasattr(self, 'edit_name') and hasattr(self, 'edit_pass'):
                self.save_edited_account(None)

    # ---------------- LOGIN ----------------
    def toggle_login_password(self, instance):
        self.password_input.password = not self.password_input.password
        self.login_pass_toggle.text = "Hide" if not self.password_input.password else "Show"

    def login(self, instance):
        # Extrage username si parola din campuri
        username = (self.username_input.text or '').strip()
        password = (self.password_input.text or '').strip()
        # Verifica daca au fost completate ambele campuri
        if not username or not password:
            self.message_label.text = "Username and password required!"
            return

        # Verifica credentialele impotriva bazei de date
        if verify_main_password(username, password):
            # Salveaza utilizatorul logat si parola principala
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

        # Fereastra de creare cont nou
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

        gen_pass_btn = Button(text="Generate Password", size_hint=(0.7,0.08), pos_hint={"center_x":0.5,"center_y":y-0.25}, background_color=(0.6,0.4,0.8,1))
        gen_pass_btn.bind(on_press=lambda inst: self.show_password_generator(inst, self.new_password))
        self.layout.add_widget(gen_pass_btn)
        self.dynamic_widgets.append(gen_pass_btn)

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
        # Buton de logout
        self.logout_btn = Button(text="Logout", size_hint=(0.2,0.1), pos_hint={"right":0.98,"top":0.95}, background_color=(0.8,0.2,0.2,1))
        self.logout_btn.bind(on_press=self.logout)
        self.layout.add_widget(self.logout_btn)

        # Buton pentru adaugarea credentialelor
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
        # Curata layout-ul si ascunde elementele din login
        self.clear_dynamic()
        for w in self.login_widgets:
            w.opacity = 0
            w.disabled = True
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 0

        # Buton pentru intoarcere
        back = Button(text="Back", size_hint=(0.2,0.1), pos_hint={"x":0.02,"top":0.95})
        back.bind(on_press=self.back_to_bubbles_from_add)
        self.layout.add_widget(back)
        self.dynamic_widgets.append(back)

        y = 0.7
        # Camp pentru website/cont
        self.acc_name = RoundedInput(hint_text="Account / Website Name", size_hint=(0.7,None), height=70, pos_hint={"center_x":0.5,"center_y":y})
        self.layout.add_widget(self.acc_name)
        self.dynamic_widgets.append(self.acc_name)

        # Camp pentru login/email
        self.acc_user = RoundedInput(hint_text="User / Email / Phone", size_hint=(0.7,None), height=70, pos_hint={"center_x":0.5,"center_y":y-0.13})
        self.layout.add_widget(self.acc_user)
        self.dynamic_widgets.append(self.acc_user)

        # Camp pentru parola
        self.acc_pass = RoundedInput(hint_text="Password", password=True, size_hint=(0.7,None), height=70, pos_hint={"center_x":0.5,"center_y":y-0.26})
        self.layout.add_widget(self.acc_pass)
        self.dynamic_widgets.append(self.acc_pass)

        # Buton pentru afisare/ascundere parola
        self.add_pass_toggle = Button(text="Show", size_hint=(0.10,0.07), pos_hint={"x":0.88,"center_y":y-0.26})
        self.add_pass_toggle.bind(on_press=self.toggle_add_pass)
        self.layout.add_widget(self.add_pass_toggle)
        self.dynamic_widgets.append(self.add_pass_toggle)

        # Buton pentru generare parola
        gen_pass_btn = Button(text="Generate Password", size_hint=(0.7,0.08), pos_hint={"center_x":0.5,"center_y":y-0.38}, background_color=(0.6,0.4,0.8,1))
        gen_pass_btn.bind(on_press=lambda inst: self.show_password_generator(inst, self.acc_pass))
        self.layout.add_widget(gen_pass_btn)
        self.dynamic_widgets.append(gen_pass_btn)

        # Buton pentru salvare
        save_btn = Button(text="Save Account", size_hint=(0.7,0.1), pos_hint={"center_x":0.5,"center_y":0.07}, background_color=(0.2,0.6,0.8,1), font_size=22)
        save_btn.bind(on_press=self.save_account)
        self.layout.add_widget(save_btn)
        self.dynamic_widgets.append(save_btn)

        self.current_screen = 'add_credential'

    def show_password_generator(self, instance, target_field):
        # Creeaza popup pentru generatorul de parole
        popup_box = BoxLayout(orientation="vertical", spacing=20, padding=20)
        
        # Sectiunea pentru lungimea minima
        length_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=60, spacing=10)
        length_box.add_widget(Label(text="Minimum Length:", size_hint_x=0.4, font_size=25))

        # Camp pentru introducerea lungimii
        self.length_input = RoundedInput(hint_text="12", size_hint_x=0.6, height=60)
        self.length_input.text = "12"
        length_box.add_widget(self.length_input)
        popup_box.add_widget(length_box)
        
        # Eticheta pentru optiuni
        checkbox_label = Label(text="Must Include:", size_hint_y=None, height=40, font_size=20)
        popup_box.add_widget(checkbox_label)
        
        # Checkbox pentru litere
        letters_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10)
        self.include_letters = CheckBox(size_hint_x=0.1, active=True)
        letters_box.add_widget(self.include_letters)
        letters_box.add_widget(Label(text="Letters (a-z, A-Z)", size_hint_x=0.9, font_size=22))
        popup_box.add_widget(letters_box)
        
        # Checkbox pentru numere
        numbers_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10)
        self.include_numbers = CheckBox(size_hint_x=0.1, active=True)
        numbers_box.add_widget(self.include_numbers)
        numbers_box.add_widget(Label(text="Numbers (0-9)", size_hint_x=0.9, font_size=22))
        popup_box.add_widget(numbers_box)
        
        # Checkbox pentru caractere speciale
        special_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=10)
        self.include_special = CheckBox(size_hint_x=0.1, active=True)
        special_box.add_widget(self.include_special)
        special_box.add_widget(Label(text="Special Characters (!@#$%)", size_hint_x=0.9, font_size=22))
        popup_box.add_widget(special_box)
        
        # Buton pentru generare
        gen_btn = Button(text="Generate", size_hint_y=None, height=70, background_color=(0.2,0.6,0.8,1), font_size=20)
        popup_box.add_widget(gen_btn)
        
        # Creeaza si afiseaza popup-ul
        popup = Popup(title="Generate Password", content=popup_box, size_hint=(0.9, 0.9))
        gen_btn.bind(on_press=lambda x: self.generate_password(popup, target_field))
        popup.open()

    def generate_password(self, popup, target_field):
        # Extrage lungimea dintr-un camp text
        try:
            length = int(self.length_input.text)
        except ValueError:
            self.message_label.text = "Please enter a valid minimum length!"
            return
        
        # Verifica daca lungimea este valida
        if length < 1:
            self.message_label.text = "Minimum length must be at least 1!"
            return
        
        # Construieste setul de caractere disponibile
        characters = ""
        if self.include_letters.active:
            characters += string.ascii_letters
        if self.include_numbers.active:
            characters += string.digits
        if self.include_special.active:
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Verifica daca a fost selectata cel putin o optiune
        if not characters:
            self.message_label.text = "Please select at least one character type!"
            return
        
        # Genereaza parola aleatoare cu lungimea specificata
        generated_password = ''.join(random.choice(characters) for _ in range(length))
        # Completeaza campul text
        target_field.text = generated_password
        # Inchide popup-ul
        popup.dismiss()
        # Arata mesaj de confirmare
        self.message_label.text = "Password generated!"

    def toggle_add_pass(self, instance):
        self.acc_pass.password = not self.acc_pass.password
        instance.text = "Hide" if not self.acc_pass.password else "Show"

    def save_account(self, instance):
        # Extrage valorile din campuri
        name = (self.acc_name.text or '').strip()
        user = (self.acc_user.text or '').strip()
        pwd = (self.acc_pass.text or '').strip()

        # Verifica daca s-a introdus un nume
        if not name:
            self.message_label.text = "Account name required!"
            return

        # Adauga o noua credentiala
        add_credential(self.logged_in_user, name, user, pwd, self.main_password)
        # Arata mesaj de confirmare
        self.message_label.text = f"Account '{name}' saved!"
        # Inapoi la lista
        self.back_to_bubbles_from_add()

    # ---------------- BUBBLES ----------------
    def show_bubbles(self):
        # Curata layout-ul si seteaza ecranul curent
        self.clear_dynamic()
        self.current_screen = 'main'
        # Obtine contul logat si lista de credentiale
        acc = get_account(self.logged_in_user)
        creds = acc.get("credentials", []) if acc else []

        # Creeaza o area cu scroll pentru butoanele de conturi
        self.scroll = ScrollView(size_hint=(0.9,0.55), pos_hint={"center_x":0.5,"y":0.3})
        self.dynamic_widgets.append(self.scroll)
        self.box = BoxLayout(orientation="vertical", spacing=15, size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        self.layout.add_widget(self.scroll)

        # Creeaza un buton pentru fiecare credentiala
        for cred in creds:
            btn = Button(text=cred.get("website",""), size_hint=(1,None), height=90, background_color=(0.4,0.6,0.8,1), font_size=24)
            btn.bind(on_press=lambda inst, c=cred: self.show_details(c))
            self.box.add_widget(btn)

    def show_details(self, cred):
        # Curata layout-ul si ascunde butonul de adaugare
        self.clear_dynamic()
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 0
        self.current_screen = 'details'

        # Buton pentru intoarcere
        back = Button(text="Back", size_hint=(0.2,0.1), pos_hint={"x":0.02,"top":0.95})
        back.bind(on_press=self.back_to_bubbles)
        self.layout.add_widget(back)
        self.dynamic_widgets.append(back)

        y = 0.75
        font = 26

        # Eticheta pentru website
        L = Label(text=f"Website: {cred.get('website','')}", pos_hint={"center_x":0.5,"center_y":y}, size_hint=(0.8,0.1), font_size=font)
        self.layout.add_widget(L)
        self.dynamic_widgets.append(L)

        # Eticheta pentru login
        self.login_lbl = Label(text=f"Login: {cred.get('login','')}", pos_hint={"center_x":0.5,"center_y":y-0.15}, size_hint=(0.7,0.1), font_size=font)
        self.layout.add_widget(self.login_lbl)
        self.dynamic_widgets.append(self.login_lbl)

        # Decripteaza parola
        decrypted_pwd = decrypt_credential(get_account(self.logged_in_user), cred, self.main_password)

        # Eticheta pentru parola mascata initial
        self.pass_lbl = Label(text=f"Password: {'*'*len(decrypted_pwd)}", pos_hint={"center_x":0.5,"center_y":y-0.28}, size_hint=(0.7,0.1), font_size=font)
        self.layout.add_widget(self.pass_lbl)
        self.dynamic_widgets.append(self.pass_lbl)

        # Buton pentru afisare/ascundere parola
        self.detail_pass_toggle = Button(text="Show", size_hint=(0.15,0.07), pos_hint={"x":0.78,"center_y":y-0.28})
        self.detail_pass_toggle.bind(on_press=lambda inst: self.toggle_label(self.pass_lbl, decrypted_pwd, self.detail_pass_toggle))
        self.layout.add_widget(self.detail_pass_toggle)
        self.dynamic_widgets.append(self.detail_pass_toggle)

        # Buton pentru copiere parola
        copy_pass_btn = Button(text="Copy", size_hint=(0.15,0.07), pos_hint={"x":0.78,"center_y":y-0.38})
        copy_pass_btn.bind(on_press=lambda inst: self.copy_password(decrypted_pwd))
        self.layout.add_widget(copy_pass_btn)
        self.dynamic_widgets.append(copy_pass_btn)

        # Buton pentru editare credentialelor
        edit_btn = Button(text="Edit Account", size_hint=(0.7,0.1), pos_hint={"center_x":0.5,"y":0.20}, background_color=(0.3,0.7,0.4,1), font_size=22)
        edit_btn.bind(on_press=lambda inst: self.edit_account(cred))
        self.layout.add_widget(edit_btn)
        self.dynamic_widgets.append(edit_btn)

        # Buton pentru stergere cont
        delete_btn = Button(text="Delete Account", size_hint=(0.7,0.1), pos_hint={"center_x":0.5,"y":0.08}, background_color=(0.8,0.2,0.2,1), font_size=22)
        delete_btn.bind(on_press=lambda inst: self.delete_account(cred))
        self.layout.add_widget(delete_btn)
        self.dynamic_widgets.append(delete_btn)

    def toggle_label(self, lbl, value, toggle_btn):
        # Extrage textul din eticheta
        text = lbl.text.split(": ")[0]
        # Verifica daca parola este mascata cu asteriscuri
        if lbl.text.endswith("*"*len(value)):
            # Afiseaza parola
            lbl.text = f"{text}: {value}"
            toggle_btn.text = "Hide"
        else:
            # Masca parola cu asteriscuri
            lbl.text = f"{text}: {'*'*len(value)}"
            toggle_btn.text = "Show"

    def copy_password(self, password):
        # Copie parola in clipboard
        Clipboard.copy(password)
        # Arata mesaj de confirmare
        self.message_label.text = "Password copied to clipboard!"

    def delete_account(self, cred):
        # Extrage website si login din credentiale
        website_name = cred.get("website", "")
        login = cred.get("login", "")
        # Sterge credentialele din baza de date
        delete_credential(self.logged_in_user, website_name, login, self.main_password)
        self.message_label.text = f"Account '{website_name}' deleted!"
        self.back_to_bubbles()

    def edit_account(self, cred):
        # Memoreaza credentialele originale pentru editare
        self.editing_cred = cred
        self.clear_dynamic()
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 0

        # Buton pentru intoarcere
        back = Button(text="Back", size_hint=(0.2,0.1), pos_hint={"x":0.02,"top":0.95})
        back.bind(on_press=self.back_to_details_from_edit)
        self.layout.add_widget(back)
        self.dynamic_widgets.append(back)

        y = 0.7
        # Camp pentru website/cont
        self.edit_name = RoundedInput(hint_text="Account / Website Name", size_hint=(0.7,None), height=70, pos_hint={"center_x":0.5,"center_y":y})
        self.edit_name.text = cred.get("website", "")
        self.layout.add_widget(self.edit_name)
        self.dynamic_widgets.append(self.edit_name)

        # Camp pentru login/email
        self.edit_user = RoundedInput(hint_text="User / Email / Phone", size_hint=(0.7,None), height=70, pos_hint={"center_x":0.5,"center_y":y-0.13})
        self.edit_user.text = cred.get("login", "")
        self.layout.add_widget(self.edit_user)
        self.dynamic_widgets.append(self.edit_user)

        # Decripteaza parola veche
        decrypted_pwd = decrypt_credential(get_account(self.logged_in_user), cred, self.main_password)
        
        # Camp pentru parola
        self.edit_pass = RoundedInput(hint_text="Password", password=True, size_hint=(0.7,None), height=70, pos_hint={"center_x":0.5,"center_y":y-0.26})
        self.edit_pass.text = decrypted_pwd
        self.layout.add_widget(self.edit_pass)
        self.dynamic_widgets.append(self.edit_pass)

        # Buton pentru afisare/ascundere parola
        self.edit_pass_toggle = Button(text="Show", size_hint=(0.10,0.07), pos_hint={"x":0.88,"center_y":y-0.26})
        self.edit_pass_toggle.bind(on_press=self.toggle_edit_pass)
        self.layout.add_widget(self.edit_pass_toggle)
        self.dynamic_widgets.append(self.edit_pass_toggle)

        # Buton pentru generare parola
        gen_pass_btn = Button(text="Generate Password", size_hint=(0.7,0.08), pos_hint={"center_x":0.5,"center_y":y-0.38}, background_color=(0.6,0.4,0.8,1))
        gen_pass_btn.bind(on_press=lambda inst: self.show_password_generator(inst, self.edit_pass))
        self.layout.add_widget(gen_pass_btn)
        self.dynamic_widgets.append(gen_pass_btn)

        # Buton pentru salvare
        save_btn = Button(text="Save Changes", size_hint=(0.7,0.1), pos_hint={"center_x":0.5,"center_y":0.07}, background_color=(0.2,0.6,0.8,1), font_size=22)
        save_btn.bind(on_press=self.save_edited_account)
        self.layout.add_widget(save_btn)
        self.dynamic_widgets.append(save_btn)

        self.current_screen = 'edit_credential'

    def toggle_edit_pass(self, instance):
        # Afiseaza sau ascunde parola
        self.edit_pass.password = not self.edit_pass.password
        instance.text = "Hide" if not self.edit_pass.password else "Show"

    def save_edited_account(self, instance):
        # Extrage valorile din campuri
        name = (self.edit_name.text or '').strip()
        user = (self.edit_user.text or '').strip()
        pwd = (self.edit_pass.text or '').strip()

        # Verifica daca s-a introdus un nume
        if not name:
            self.message_label.text = "Account name required!"
            return

        # Sterge credentialele vechi
        old_website = self.editing_cred.get("website", "")
        old_login = self.editing_cred.get("login", "")
        delete_credential(self.logged_in_user, old_website, old_login, self.main_password)
        
        # Adauga credentialele noi
        add_credential(self.logged_in_user, name, user, pwd, self.main_password)
        # Arata mesaj de confirmare
        self.message_label.text = f"Account '{name}' updated!"
        # Inapoi la lista de conturi
        self.back_to_bubbles()

    def back_to_details_from_edit(self, *args):
        self.clear_dynamic()
        if hasattr(self, 'add_account_btn'):
            self.add_account_btn.opacity = 0
        self.show_details(self.editing_cred)

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
