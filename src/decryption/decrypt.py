import os
import json
#from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

SUPPORTED_ALGORITHMS = "AES-256-GCM"


def decrypt_container(container_dir, output_file, key):

    with open(os.path.join(container_dir, "header.json"), "rb") as f:
        header_bytes = f.read()

    header = json.loads(header_bytes)

    # verify algorithm metadata
    if header.get("algorithm") != SUPPORTED_ALGORITHMS:
        raise ValueError("Unsupported encryption algorithm")

    with open(os.path.join(container_dir, "nonce"), "rb") as f:
        nonce = f.read()

    with open(os.path.join(container_dir, "ciphertext"), "rb") as f:
        ciphertext = f.read()

    # with open(os.path.join(container_dir, "header.json"), "rb") as f:
    #     tag = f.read()

    # cipher = Cipher(
    #     algorithms.AES(key),
    #     modes.GCM(nonce, tag)
    # )

    #decryptor = cipher.decryptor()
    aesgcm = AESGCM(key)

    # authenticate metadata again

    try:
        plaintext = aesgcm.decrypt(nonce,ciphertext,header_bytes)
    except InvalidTag:
        raise ValueError("Integrity verification failed: container may be tampered")

    with open(output_file, "wb") as f:
        f.write(plaintext)