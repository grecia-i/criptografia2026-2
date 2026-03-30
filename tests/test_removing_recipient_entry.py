import os
import json
import tempfile
import pytest

from encryption.encrypt import encrypt_file
from encryption.decrypt import decrypt_container
from encryption.keys import (
    generate_key_pair,
    store_private_key,
    store_public_key,
    load_private_key,
    load_public_key,
    get_key_id
)

def test_removing_recipient_entry_breaks_access():
    with tempfile.TemporaryDirectory() as tmp:
        users_dir = os.path.join(tmp, "users")
        vault_dir = os.path.join(tmp, "vault")
        os.makedirs(users_dir, exist_ok=True)

        # Crear usuarios Alice y Bob
        for username in ["alice", "bob"]:
            user_dir = os.path.join(users_dir, username)
            os.makedirs(user_dir, exist_ok=True)

            priv, pub = generate_key_pair()
            store_private_key(priv, os.path.join(user_dir, "private.pem"), "1234")
            store_public_key(pub, os.path.join(user_dir, "public.pem"))

        # Cargar claves públicas
        alice_pub = load_public_key(os.path.join(users_dir, "alice", "public.pem"))
        bob_pub = load_public_key(os.path.join(users_dir, "bob", "public.pem"))

        recipients = [
            {"user": "alice", "id": get_key_id(alice_pub), "key": alice_pub},
            {"user": "bob", "id": get_key_id(bob_pub), "key": bob_pub},
        ]

        # Crear archivo de prueba
        input_file = os.path.join(tmp, "mensaje.txt")
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("archivo secreto")

        container_dir = os.path.join(vault_dir, "mensaje.txt")
        encrypt_file(input_file, container_dir, recipients)

        # Abrir y modificar header.json
        header_path = os.path.join(container_dir, "header.json")
        with open(header_path, "r", encoding="utf-8") as f:
            header = json.load(f)

        # Eliminar a Bob de la lista de recipients
        header["recipients"] = [
            r for r in header["recipients"]
            if r["user"] != "bob"
        ]

        with open(header_path, "w", encoding="utf-8") as f:
            json.dump(header, f, sort_keys=True)

        # Intentar descifrar como Bob
        bob_priv = load_private_key(
            os.path.join(users_dir, "bob", "private.pem"),
            "1234"
        )
        bob_id = get_key_id(bob_pub)

        output_file = os.path.join(tmp, "salida_bob.txt")

        with pytest.raises(ValueError, match="You are not an authorized recipient"):
            decrypt_container(container_dir, output_file, bob_priv, bob_id)