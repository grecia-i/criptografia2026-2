import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password: str,salt):
    # Salts should be randomly generated
    # derive
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,
    )
    key = kdf.derive(password.encode())
    return key

def verify_key(password,salt,key):
    # verify
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,
    )
    kdf.verify(password, key)

def write_salt(salt, salt_path):
    with open(salt_path, "wb") as f:
        f.write(salt)

def read_salt(salt_path):
    with open(salt_path, "rb") as f:
        return f.read()
