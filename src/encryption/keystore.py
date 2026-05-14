import json
import os
import secrets
from datetime import datetime

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidTag

KDF_N = 2**14       #CPU cost
KDF_R = 8           #Tamaño de bloque
KDF_P = 1           #Paralelización
KEY_LENGTH = 32     

NONCE_LENGTH = 12
SALT_LENGTH = 16


def derive_key(password: str, salt: bytes):

    kdf = Scrypt(
        salt=salt,
        length=KEY_LENGTH,
        n=KDF_N,
        r=KDF_R,
        p=KDF_P
    )

    return kdf.derive(password.encode())


def create_keystore(private_key, password: str, keystore_path: str, key_id: str):

    salt = secrets.token_bytes(SALT_LENGTH)
    nonce = secrets.token_bytes(NONCE_LENGTH)

    aes_key = derive_key(password, salt)

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    aesgcm = AESGCM(aes_key)

    ciphertext = aesgcm.encrypt(nonce, pem, None)

    #TODO Verificar keystore
    keystore = {
        "version": 1,
        "kdf": "scrypt",
        "kdf_parameters": {
            "n": KDF_N,
            "r": KDF_R,
            "p": KDF_P,
            "length": KEY_LENGTH
        },
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "encrypted_key": ciphertext.hex(),
        "public_key_id": key_id,
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    }

    with open(keystore_path, "w") as f:
        json.dump(keystore, f, indent=4)


def load_keystore(keystore_path: str, password: str):

    with open(keystore_path, "r") as f:
        keystore = json.load(f)

    if keystore.get("status") == "revoked":
        raise ValueError("Key has been revoked")

    salt = bytes.fromhex(keystore["salt"])
    nonce = bytes.fromhex(keystore["nonce"])
    ciphertext = bytes.fromhex(keystore["encrypted_key"])

    aes_key = derive_key(password, salt)

    aesgcm = AESGCM(aes_key)

    try:
        pem = aesgcm.decrypt(nonce, ciphertext, None)
    except InvalidTag:
        raise ValueError(
            "Decryption failed: container may have been tampered with"
        )

    private_key = serialization.load_pem_private_key(
        pem,
        password=None
    )

    return private_key


def revoke_keystore(keystore_path: str):

    with open(keystore_path, "r") as f:
        keystore = json.load(f)

    keystore["status"] = "revoked"
    keystore["revoked_at"] = datetime.utcnow().isoformat()

    with open(keystore_path, "w") as f:
        json.dump(keystore, f, indent=4)


def rotate_keys(user_dir: str, password: str, generate_key_pair, store_public_key, get_key_id):

    private_key, public_key = generate_key_pair()

    key_id = get_key_id(public_key)

    create_keystore(
        private_key,
        password,
        os.path.join(user_dir, "keystore.json"),
        key_id
    )

    store_public_key(
        public_key,
        os.path.join(user_dir, "public.pem")
    )

    return key_id


def backup_keystore(user_dir: str, backup_dir: str):

    os.makedirs(backup_dir, exist_ok=True)

    files = ["keystore.json", "public.pem"]

    for file_name in files:
        src = os.path.join(user_dir, file_name)
        dst = os.path.join(backup_dir, file_name)

        with open(src, "rb") as fsrc:
            data = fsrc.read()

        with open(dst, "wb") as fdst:
            fdst.write(data)


def restore_keystore(backup_dir: str, user_dir: str):

    os.makedirs(user_dir, exist_ok=True)

    files = ["keystore.json", "public.pem"]

    for file_name in files:
        src = os.path.join(backup_dir, file_name)
        dst = os.path.join(user_dir, file_name)

        with open(src, "rb") as fsrc:
            data = fsrc.read()

        with open(dst, "wb") as fdst:
            fdst.write(data)