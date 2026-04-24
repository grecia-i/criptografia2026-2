import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
from src.encryption.keys import load_public_key, get_key_id

SUPPORTED_ALGORITHMS = "AES-256-GCM"

#Signing
def verify_signature(public_key, signature, data):
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
        # raise ValueError(
        #     "Authentication failed: Invalid signature"
        # )
        

#Asymetric encryption
def decrypt_file_key_with_privkey(encrypted_key, private_key):
    return private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

#def decrypt_container(container_dir, output_file, derived_key):
def decrypt_container(container_dir, output_file, private_key, my_id): 
    with open(os.path.join(container_dir, "header.json"), "rb") as f:
        header_bytes = f.read()

    header = json.loads(header_bytes)
    my_entry = None
    for r in header["recipients"]:
        if r["id"] == my_id:
            my_entry = r
            break

    if my_entry is None:
        raise ValueError("You are not an authorized recipient")

    if header.get("algorithm") != SUPPORTED_ALGORITHMS:
        raise ValueError("Unsupported encryption algorithm")

    with open(os.path.join(container_dir, "nonce"), "rb") as f:
        nonce = f.read()

    with open(os.path.join(container_dir, "ciphertext"), "rb") as f:
        ciphertext = f.read()

    #Signing
    with open(os.path.join(container_dir, "signature"), "rb") as f:
        signature = f.read()
    
    sender_id = header.get("sender_id")
    if not sender_id:
        raise ValueError("Missing sender_id")
    
    sender_key = None

    # TODO revisar esta parte, carpetas con id de usuario
    for username in os.listdir("users"):
        pub_path = os.path.join("users", username, "public.pem")
        pub = load_public_key(pub_path)

        if get_key_id(pub) == sender_id:
            sender_key = pub
            break

    if sender_key is None:
        raise ValueError("Sender public key not found")
    signature_input = header_bytes + ciphertext

    if not verify_signature(sender_key, signature, signature_input):
        raise ValueError("Signature verification failed")

    #key = decrypt_key(header_bytes, container_dir, derived_key)
    encrypted_key = bytes.fromhex(my_entry["encrypted_key"])
    key = decrypt_file_key_with_privkey(encrypted_key, private_key)

    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, header_bytes)
    except InvalidTag:
        raise ValueError(
            "Authentication failed: container contents or metadata may have been tampered with"
        )

    with open(output_file, "wb") as f:
        f.write(plaintext)