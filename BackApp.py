import json
import os
import base64
from crypto import hash_password, verify_password, derive_key, encrypt_password, decrypt_password

DATA_FILE = "Data/data.json"

# Ensure JSON file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"accounts": []}, f, indent=4)


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_account(username, password):
    """Create a new main account with hashed password and salt."""
    data = load_data()

    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if set(password).isdisjoint('1234567890'):
        return False, "Password must contain at least one number"


    # Check if user exists
    for acc in data["accounts"]:
        if acc["username"] == username:
            return False, "Account already exists"

    # Generate salt for hashing
    salt = os.urandom(16)
    hashed = hash_password(password, salt)

    # Add account
    data["accounts"].append({
        "username": username,
        "password": hashed,
        "salt": base64.b64encode(salt).decode(),
        "credentials": []
    })
    save_data(data)
    return True, "Account created"


def get_account(username):
    data = load_data()
    for acc in data["accounts"]:
        if acc["username"] == username:
            return acc
    return None


def verify_main_password(username, password):
    """Return True if main password is correct."""
    acc = get_account(username)
    if not acc or "salt" not in acc or "password" not in acc:
        return False
    salt = base64.b64decode(acc["salt"])
    stored_hash = acc["password"]
    return verify_password(password, stored_hash, salt)


def add_credential(username, website, login, password, main_password):
    """Add a credential to a user, encrypting the password."""
    data = load_data()
    for acc in data["accounts"]:
        if acc["username"] == username:
            salt = base64.b64decode(acc["salt"])
            key = derive_key(main_password, salt)
            encrypted_pwd = encrypt_password(password, key)
            acc.setdefault("credentials", []).append({
                "website": website,
                "login": login,
                "password": encrypted_pwd
            })
            save_data(data)
            return True
    return False


def decrypt_credential(acc, credential, main_password):
    """Decrypt a single credential's password."""
    salt = base64.b64decode(acc["salt"])
    key = derive_key(main_password, salt)
    decrypted = decrypt_password(credential["password"], key)
    return decrypted
