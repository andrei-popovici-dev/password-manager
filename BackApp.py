import json
import os
import base64
from crypto import hash_password, verify_password, derive_key, encrypt_password, decrypt_password

# Calea catre fisierul de date
DATA_FILE = "data.json"

# Asigura ca fisierul JSON exista
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"accounts": []}, f, indent=4)


def load_data():
    """Incarca datele din fisierul JSON."""
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    """Salveaza datele in fisierul JSON."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_account(username, password):
    """Creeaza un nou cont principal cu parola hash-ata si salt."""
    data = load_data()

    # Verifica daca utilizatorul deja exista
    for acc in data["accounts"]:
        if acc["username"] == username:
            return False

    # Genereaza salt si parola hash-ata
    salt = os.urandom(16)
    hashed = hash_password(password, salt)

    # Adauga noul cont
    data["accounts"].append({
        "username": username,
        "password": hashed,
        "salt": base64.b64encode(salt).decode(),
        "credentials": []
    })
    save_data(data)
    return True


def get_account(username):
    """Obtine contul unui utilizator dupa username."""
    data = load_data()
    for acc in data["accounts"]:
        if acc["username"] == username:
            return acc
    return None


def verify_main_password(username, password):
    """Verifica daca parola principala este corecta."""
    acc = get_account(username)
    if not acc or "salt" not in acc or "password" not in acc:
        return False
    salt = base64.b64decode(acc["salt"])
    stored_hash = acc["password"]
    return verify_password(password, stored_hash, salt)


def add_credential(username, website, login, password, main_password):
    """Adauga o credentiala la un utilizator, criptand parola."""
    data = load_data()
    for acc in data["accounts"]:
        if acc["username"] == username:
            # Deriveaza cheia din parola principala si salt
            salt = base64.b64decode(acc["salt"])
            key = derive_key(main_password, salt)
            # Cripteaza parola
            encrypted_pwd = encrypt_password(password, key)
            # Adauga credentiala in lista de credentiale
            acc.setdefault("credentials", []).append({
                "website": website,
                "login": login,
                "password": encrypted_pwd
            })
            save_data(data)
            return True
    return False


def decrypt_credential(acc, credential, main_password):
    """Decripteaza parola unei credentiale."""
    salt = base64.b64decode(acc["salt"])
    key = derive_key(main_password, salt)
    decrypted = decrypt_password(credential["password"], key)
    return decrypted


def delete_credential(username, website, login, main_password):
    """Sterge o credentiala specifica de la un utilizator."""
    data = load_data()
    for acc in data["accounts"]:
        if acc["username"] == username:
            credentials = acc.get("credentials", [])
            # Cauta si sterge credentiala care se potriveste
            for i, cred in enumerate(credentials):
                if cred.get("website") == website and cred.get("login") == login:
                    acc["credentials"].pop(i)
                    save_data(data)
                    return True
    return False
