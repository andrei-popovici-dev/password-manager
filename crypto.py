import base64, os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

def hash_password(password: str, salt: bytes) -> str:
    """Genereaza un hash PBKDF2 al parolei cu salt."""
    # Creeaza un derivator de chei folosind PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    hashed = kdf.derive(password.encode())
    # Codifica hash-ul in base64 pentru stocare
    return base64.b64encode(hashed).decode()


def verify_password(password: str, stored_hash: str, salt: bytes) -> bool:
    """Verifica parola comparand hash-urile."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    try:
        # Verifica daca parola introdusa se potriveste cu hash-ul stocat
        kdf.verify(password.encode(), base64.b64decode(stored_hash.encode()))
        return True
    except:
        return False

def derive_key(password: str, salt: bytes) -> bytes:
    """Genereaza o cheie Fernet din parola pentru criptarea credentialelor."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    key = kdf.derive(password.encode())
    # Codifica cheia pentru a fi compatibila cu Fernet
    return base64.urlsafe_b64encode(key)

def encrypt_password(plaintext: str, key_b64: bytes) -> str:
    """Cripteaza o parola folosind Fernet."""
    f = Fernet(key_b64)
    token = f.encrypt(plaintext.encode())
    return token.decode()


def decrypt_password(ciphertext: str, key_b64: bytes) -> str:
    """Decripteaza o parola folosind Fernet."""
    f = Fernet(key_b64)
    # Decripteaza si returneaza parola in format text
    return f.decrypt(ciphertext.encode()).decode()
