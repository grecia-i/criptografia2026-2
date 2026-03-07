import os
import json
import secrets
from datetime import datetime # for the timestamp
import zoneinfo
import tzlocal # timestamp + timezone
import uuid # rand id generation
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_SIZE = 256
NONCE_SIZE = 12
SUPPORTED_ALGORITHMS = "AES-256-GCM"
TIMEZONE = tzlocal.get_localzone()

def generate_key():
    return AESGCM.generate_key(KEY_SIZE)

def read_key(path):
    with open(path,"rb") as key_file:
        key=key_file.read()
    return key

def write_key(vault_path,key):
    key_path = os.path.join(vault_path,"key")
    os.makedirs(key_path,exist_ok=True)
    
    with open(os.path.join(key_path,"priv.key"),"wb") as key_file:
        key_file.write(key)

def encrypt_file(input_file, vault_dir, key):
    os.makedirs(vault_dir, exist_ok=True)
    write_key(vault_dir,key)

    with open(input_file, "rb") as f:
        plaintext = f.read()

    nonce = secrets.token_bytes(NONCE_SIZE)

    header = {
        "algorithm": SUPPORTED_ALGORITHMS,
        "nonce_size": NONCE_SIZE*8,
        "file_name": os.path.basename(input_file),
        "file_size": os.path.getsize(input_file),
        "key_length": KEY_SIZE,
        "time_creation": datetime.now(TIMEZONE).isoformat()
        # the owner id NEEDS TO BE CHANGED to be generated while creating an user -> storaged
        # "owner_id": str(uuid.uuid4), # random UUID in a cryptographically-secure method according to RFC 9562, §5.4.
        # "file_id": str(uuid.uuid4)
    }

    header_bytes = json.dumps(header, sort_keys=True).encode()

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