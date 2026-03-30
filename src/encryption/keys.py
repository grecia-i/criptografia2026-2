from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes

def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key

def load_private_key(path, password):
    with open(path, "rb") as f:
        pem_data = f.read()

    private_key = serialization.load_pem_private_key(
        pem_data,
        password=password.encode()
    )

    return private_key

def load_public_key(path):
    with open(path, "rb") as f:
        pem_data = f.read()

    public_key = serialization.load_pem_public_key(pem_data)

    return public_key

def store_private_key(private_key, path, password = None):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
    )

    with open(path, "wb") as f:
        f.write(pem)

def store_public_key(public_key, path):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(path, "wb") as f:
        f.write(pem)

def get_key_id(public_key):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, #DER o PEM ??
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    digest = hashes.Hash(hashes.SHA256())
    digest.update(pem)

    return digest.finalize().hex()
