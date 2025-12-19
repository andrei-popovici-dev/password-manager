import base64, os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

# ================================
# PASSWORD HASH (pentru LOGIN)
# ================================

def hash_password(password: str, salt: bytes) -> str:
    """Returnează un hash PBKDF2 al parolei."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    hashed = kdf.derive(password.encode())
    return base64.b64encode(hashed).decode()


def verify_password(password: str, stored_hash: str, salt: bytes) -> bool:
    """Verifică parola folosind PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    try:
        kdf.verify(password.encode(), base64.b64decode(stored_hash.encode()))
        return True
    except:
        return False


# =============================================
# KEY DERIVATION pentru criptarea credentialelor
# =============================================

def derive_key(password: str, salt: bytes) -> bytes:
    """Generează o cheie Fernet din parolă (pentru criptarea credentialelor)."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)


# ============================
# ENCRYPT / DECRYPT PAROLE
# ============================

def encrypt_password(plaintext: str, key_b64: bytes) -> str:
    f = Fernet(key_b64)
    token = f.encrypt(plaintext.encode())
    return token.decode()


def decrypt_password(ciphertext: str, key_b64: bytes) -> str:
    f = Fernet(key_b64)
    return f.decrypt(ciphertext.encode()).decode()
