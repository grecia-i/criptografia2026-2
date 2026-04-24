import os
import json
import secrets
from datetime import datetime # for the timestamp
import zoneinfo
import tzlocal # timestamp + timezone
import uuid # rand id generation
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from warnings import deprecated

KEY_SIZE = 256
NONCE_SIZE = 12
SUPPORTED_ALGORITHMS = "AES-256-GCM"
TIMEZONE = tzlocal.get_localzone()

#Signing
def sign_data(private_key, data):
    return private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
#Asymetric encryption

def encrypt_file_key_with_pubkey(file_key, public_key):
    return public_key.encrypt(
        file_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


###########################################################
#AEAD encryption

def generate_key():
    return AESGCM.generate_key(KEY_SIZE)

#recipient key is 
#   recipient_public_keys = [
#     {"user": alice, "id": "alice_fingerprint", "key": alice_pubkey},
#     {"user": bob, "id": "bob_fingerprint", "key": bob_pubkey}
#   ]
def encrypt_file(input_file, vault_dir, recipient_public_keys, signer_key, sender_id):

    key = generate_key()

    os.makedirs(vault_dir, exist_ok=True)

    with open(input_file, "rb") as f:
        plaintext = f.read()

    nonce = secrets.token_bytes(NONCE_SIZE)

    recipients = []
    for r in recipient_public_keys:
        enc_key = encrypt_file_key_with_pubkey(key, r["key"])

        recipients.append({
            "user": r["user"],
            "id": r["id"],
            "encrypted_key": enc_key.hex()  # store safely
        })

    header = {
        "algorithm": SUPPORTED_ALGORITHMS,
        "key_encryption": "RSA-OAEP",
        "nonce_size": NONCE_SIZE*8,
        "sender_id": sender_id,
        "recipients": recipients,
        "file_name": os.path.basename(input_file),
        "file_size": os.path.getsize(input_file),
        "key_length": KEY_SIZE,
        "time_creation": datetime.now(TIMEZONE).isoformat()
    }

    header_bytes = json.dumps(header, sort_keys=True).encode()

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce,plaintext,header_bytes)

    signature_data= header_bytes + ciphertext
    signature = sign_data(signer_key, signature_data)

    tag = ciphertext[-16:]

    with open(os.path.join(vault_dir, "header.json"), "wb") as f:
        f.write(header_bytes)

    with open(os.path.join(vault_dir, "nonce"), "wb") as f:
        f.write(nonce)

    with open(os.path.join(vault_dir, "ciphertext"), "wb") as f:
        f.write(ciphertext)

    with open(os.path.join(vault_dir, "authentication_tag"), "wb") as f:
        f.write(tag)

    with open(os.path.join(vault_dir, "signature"), "wb") as f:
        f.write(signature)
