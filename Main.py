import webview
import BackApp


class Api:
    def __init__(self):
        self.current_user = None

    def login(self, username, password):
        is_valid = BackApp.verify_main_password(username, password)
        if is_valid:
            self.current_user = username
            self.main_password_cache = password
            return {"status": "success", "username": username}
        else:
            return {"status": "error", "message": "Incorect username or password"}

    def register(self, username, password):
        success, message = BackApp.add_account(username, password)
        if success:
            return {"status": "success", "message": "Account created"}
        else:
            return {"status": "error", "message": message}

    def get_user_credentials(self):
        if not self.current_user:
            return []

        account = BackApp.get_account(self.current_user)
        if "credentials" in account:
            clean_list = []
            for i, cred in enumerate(account["credentials"]):
                clean_list.append({
                    "id": i,
                    "website": cred["website"],
                    "login": cred["login"]
                })
            return clean_list
        return []

    def add_new_credential(self, website, login, password):
        if not self.current_user:
            return False
        return BackApp.add_credential(self.current_user, website, login, password, self.main_password_cache)

    def reveal_password(self, index):
        if not self.current_user:
            return "Error"

        account = BackApp.get_account(self.current_user)
        credential = account["credentials"][index]

        # Folosim parola master din cache pentru a decripta
        decrypted = BackApp.decrypt_credential(account, credential, self.main_password_cache)
        return decrypted.decode()  # sau convertit în string cum e nevoie


# Pornirea aplicației
if __name__ == '__main__':
    api = Api()
    # Creăm fereastra și atașăm API-ul
    window = webview.create_window('Password Manager', 'gui.html', js_api=api, width=800, height=600)
    webview.start(debug=False)
