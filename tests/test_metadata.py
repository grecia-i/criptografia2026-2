import os
import json
import pytest

from src.encryption.decrypt import decrypt_container
from src.encryption.keys import load_private_key, load_public_key, get_key_id

def test_modified_metadata_rejected():
    container_dir = "vault_container/test.txt"
    output_file = "recovered_test.txt"

    # 1. Modificar metadata del header
    header_path = os.path.join(container_dir, "header.json")

    with open(header_path, "rb") as f:
        header = json.loads(f.read())

    header["file_name"] = "hacked_name.txt"

    with open(header_path, "wb") as f:
        f.write(json.dumps(header, sort_keys=True).encode())

    # 2. Cargar llave privada del usuario autorizado
    private_key = load_private_key(
        "users/alice/private.pem",
        "TU_PASSWORD_DE_ALICE"
    )

    public_key = load_public_key("users/alice/public.pem")
    my_id = get_key_id(public_key)

    # 3. Debe rechazar el contenedor modificado
    with pytest.raises(ValueError):
        decrypt_container(container_dir, output_file, private_key, my_id)