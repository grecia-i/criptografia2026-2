import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

SUPPORTED_ALGORITHMS = "AES-256-GCM"


def read_key(path):
    with open(path,"rb") as key_file:
        key=key_file.read()
    return key

def decrypt_container(container_dir, output_file, master_key):

    with open(os.path.join(container_dir, "header.json"), "rb") as f:
        header_bytes = f.read()

    header = json.loads(header_bytes)

    if header.get("algorithm") != SUPPORTED_ALGORITHMS:
        raise ValueError("Unsupported encryption algorithm")

    with open(os.path.join(container_dir, "nonce"), "rb") as f:
        nonce = f.read()

    with open(os.path.join(container_dir, "ciphertext"), "rb") as f:
        ciphertext = f.read()

    key=decrypt_key(header_bytes,container_dir,master_key)

    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce,ciphertext,header_bytes)
    except InvalidTag:
        raise ValueError("Authentication failed: container contents or metadata may have been tampered with")

    with open(output_file, "wb") as f:
        f.write(plaintext)

def decrypt_key(header_bytes,container_dir,master_key):
    key_path = os.path.join(container_dir,"file.key")
    encrypted_key = read_key(key_path)

    with open(os.path.join(container_dir, "key_nonce"), "rb") as f:
        nonce = f.read()

    aesgcm = AESGCM(master_key)

    try:
        decrypted_key = aesgcm.decrypt(nonce,encrypted_key,header_bytes)
    except InvalidTag:
        raise ValueError("Authentication failed: password may be incorrect or the encrypted key may have been tampered with")

    return decrypted_key




