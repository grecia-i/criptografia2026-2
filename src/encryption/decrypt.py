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

 
def find_sender_key(sender_id: str, users_path="users"):
    """Recorre users_path y retorna la public key cuyo fingerprint coincide."""
    if not os.path.isdir(users_path):
        raise FileNotFoundError(f"Users directory not found: {users_path}")
 
    for username in os.listdir(users_path):
        pub_path = os.path.join(users_path, username, "public.pem")
        if not os.path.isfile(pub_path):
            continue
        try:
            pub = load_public_key(pub_path)
        except Exception:
            continue
 
        if get_key_id(pub) == sender_id:
            return pub
 
    raise ValueError(
        f"Sender public key not found (id={sender_id!r}). "
        "El sender debe ser un usuario registrado."
    )


#def decrypt_container(container_dir, output_file, derived_key):
def decrypt_container(container_dir:str, output_file:str, private_key:str, my_id:str, users_path="users") -> None: 

    with open(os.path.join(container_dir, "header.json"), "rb") as f:
        header_bytes = f.read()
    
    with open(os.path.join(container_dir, "nonce"), "rb") as f:
        nonce = f.read()

    with open(os.path.join(container_dir, "ciphertext"), "rb") as f:
        ciphertext = f.read()

    with open(os.path.join(container_dir, "signature"),"rb") as f:
        signature = f.read()

    header = json.loads(header_bytes)

    sender_id = header.get ("sender_id")

    if header.get("algorithm") not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {header.get('algorithm')!r}")

    if not sender_id:
        raise ValueError("Security Error: Missing sender_id in metadata.")

    # Localizar la llave pública del remitente para verificar la firma
    # Se busca en la carpeta de usuarios basándose en el sender_id del header
    sender_key = None
    users_path = "users"
    
    for username in os.listdir(users_path):
        pub_path = os.path.join(users_path, username, "public.pem")
        if os.path.exists(pub_path):
            pub = load_public_key(pub_path)
            if get_key_id(pub) == sender_id:
                sender_key = pub
                break

    if sender_key is None:
        raise ValueError(f"Verification Failed: Public key for sender '{sender_id}' not found.")

    # Origin Authentication & Integrity)
    # Firmamos Header + Ciphertext para asegurar que NADA se modificado
    signature_input = header_bytes + ciphertext
    sender_key = find_sender_key(sender_id, users_path)

    if not verify_signature(sender_key, signature, signature_input):
        raise ValueError("SECURITY ALERT: Signature verification failed! The file is forged or tampered.")

    # el usuario actual es un destinatario autorizado?
    my_entry = next((r for r in header["recipients"] if r["id"] == my_id), None)
    if not my_entry:
        raise ValueError("Access Denied: You are not an authorized recipient for this file.")

    # Descifrar la llave simétrica (File Key)
    try:
        encrypted_key = bytes.fromhex(my_entry["encrypted_key"])
        session_key = decrypt_file_key_with_privkey(encrypted_key, private_key)
    except (KeyError, ValueError) :
        raise ValueError("Decryption Failed: Could not recover the symmetric key.")

    # Descifrado Simétrico (AES-GCM)
    aesgcm = AESGCM(session_key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, header_bytes)
    except InvalidTag:
        raise ValueError("Integrity Error: Ciphertext or metadata authentication tag mismatch.")

    # Escribir el archivo recuperado
    with open(output_file, "wb") as f:
        f.write(plaintext)
    
    print(f"Success: File verified and decrypted as '{header.get('file_name', 'recovered_file')}'")
