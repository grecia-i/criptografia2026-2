import os
import json
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_SIZE = 256
NONCE_SIZE = 12
SUPPORTED_ALGORITHMS = "AES-256-GCM"


def generate_key():
    return AESGCM.generate_key(256)

def read_key(path):
    with open(path,"rb") as key_file:
        key=key_file.read()
    return key

def write_key(path,key):
    with open(path,"wb") as key_file:
        key_file.write(key)

def encrypt_file(input_file, vault_dir, key):
    os.makedirs(vault_dir, exist_ok=True)

    with open(input_file, "rb") as f:
        plaintext = f.read()

    nonce = secrets.token_bytes(NONCE_SIZE)

    header = {
        "algorithm": SUPPORTED_ALGORITHMS,
        "nonce_size": NONCE_SIZE*8,
        "file_name": os.path.basename(input_file),
        "key_length": KEY_SIZE
    }

    header_bytes = json.dumps(header).encode()

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce,plaintext,header_bytes)
    tag = ciphertext[-16:]
    print("CT= ",ciphertext.hex())
    print("TAG= ",tag.hex())


    with open(os.path.join(vault_dir, "header.json"), "wb") as f:
        f.write(header_bytes)

    with open(os.path.join(vault_dir, "nonce"), "wb") as f:
        f.write(nonce)

    with open(os.path.join(vault_dir, "ciphertext"), "wb") as f:
        f.write(ciphertext)

    with open(os.path.join(vault_dir, "authentication_tag"), "wb") as f:
        f.write(tag)