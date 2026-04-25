import os
import json
import secrets
from datetime import datetime # for the timestamp
import zoneinfo
import tzlocal # timestamp + timezone
import uuid # rand id generation
from encryption.keys import load_public_key, get_key_id
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

KEY_SIZE = 256
NONCE_SIZE = 12
SUPPORTED_ALGORITHMS = "AES-256-GCM"
TIMEZONE = tzlocal.get_localzone()

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


def sign_data(private_key, data: bytes) -> bytes:
    return private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


def encrypt_file_key_with_pubkey(file_key: bytes, public_key) -> bytes:
    return public_key.encrypt(
        file_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

# ── AES-256-GCM ───────────────────────────────────────────────────────────────

def generate_key() -> bytes:
    return AESGCM.generate_key(KEY_SIZE)
###########################################################
#AEAD encryption

#recipient key is 
#   recipient_public_keys = [
#     {"user": alice, "id": "alice_fingerprint", "key": alice_pubkey},
#     {"user": bob, "id": "bob_fingerprint", "key": bob_pubkey}
#   ]
def encrypt_file(
    input_file: str,
    vault_dir: str,
    recipient_public_keys: list,
    signer_key,
    sender_id: str,
) -> None:

    session_key = generate_key()
    os.makedirs(vault_dir, exist_ok=True)
 
    with open(input_file, "rb") as f:
        plaintext = f.read()
 
    nonce = secrets.token_bytes(NONCE_SIZE)
 
    recipients = []
    for r in recipient_public_keys:
        enc_key = encrypt_file_key_with_pubkey(session_key, r["key"])
        recipients.append({
            "user": r["user"],
            "id": r["id"],
            "encrypted_key": enc_key.hex()
        })
 
    # sender_id en el header → queda cubierto por la firma
    header = {
        "algorithm": SUPPORTED_ALGORITHMS,
        "key_encryption": "RSA-OAEP",
        "signing_algorithm": "RSA-PSS",
        "nonce_size": NONCE_SIZE * 8,
        "sender_id": sender_id,
        "recipients": recipients,
        "file_name": os.path.basename(input_file),
        "file_size": os.path.getsize(input_file),
        "key_length": KEY_SIZE,
        "time_creation": datetime.now(TIMEZONE).isoformat()
    }
 
    header_bytes = json.dumps(header, sort_keys=True).encode()
 
    aesgcm = AESGCM(session_key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, header_bytes)
 
    # Firma cubre metadatos + ciphertext (incluye el GCM tag)
    signature = sign_data(signer_key, header_bytes + ciphertext)
 
    with open(os.path.join(vault_dir, "header.json"), "wb") as f:
        f.write(header_bytes)
 
    with open(os.path.join(vault_dir, "nonce"), "wb") as f:
        f.write(nonce)
 
    with open(os.path.join(vault_dir, "ciphertext"), "wb") as f:
        f.write(ciphertext)
 
    with open(os.path.join(vault_dir, "signature"), "wb") as f:
        f.write(signature)
