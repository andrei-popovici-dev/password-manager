import webview
from typing_extensions import reveal_type

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

    def update_credential(self, cred_id, website, login, password):
        success,msg = BackApp.edit_credential_data(self.current_user,cred_id, website, login, password,self.main_password_cache)
        return success, msg


    def add_new_credential(self, website, login, password):
        if not self.current_user:
            return False, "Something went wrong"
        return BackApp.add_credential(self.current_user, website, login, password, self.main_password_cache)

    def reveal_password(self, index):
        if not self.current_user:
            return "Error"

        account = BackApp.get_account(self.current_user)
        credential = account["credentials"][index]

        decrypted = BackApp.decrypt_credential(account, credential, self.main_password_cache)
        return decrypted

    def get_current_username(self):
        return self.current_user

    def verify_weak_passwords(self):
        i = 0
        weak_accounts = []

        for cred in self.get_user_credentials():
            current_id = cred.get("id")
            success, err = BackApp.verify_password_style(self.reveal_password(current_id))
            if not success:
                weak_accounts.append(cred)

        return weak_accounts

    def delete_credential(self, index):
        if not self.current_user:
            return False, "Something went wrong"
        status, err = BackApp.delete_credential_data(self.current_user, index)
        return status, err

if __name__ == '__main__':
    api = Api()
    window = webview.create_window('Password Manager', 'index.html', js_api=api, width=900, height=700)
    window.min_size = (800, 600)
    webview.start(debug=True)
