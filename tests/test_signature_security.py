import json
import pytest
from unittest.mock import patch, MagicMock

from src.main import (
    main,
    create_user,
    decrypt_container,
    load_private_key,
    load_public_key,
    get_key_id
)


@pytest.fixture
def mock_env(tmp_path):
    users_path = tmp_path / "users"
    users_path.mkdir()

    vault_path = tmp_path / "vault_container"
    vault_path.mkdir()

    with patch("src.main.USERS_PATH", str(users_path)), \
         patch("src.main.VAULT_PATH", str(vault_path)):
        yield tmp_path, users_path, vault_path


def create_signed_container(tmp_path, users_path, vault_path, create_eve=False):
    with patch("getpass.getpass", return_value="examplepassword"):
        create_user("Alice")
        create_user("Bob")
        if create_eve:
            create_user("Eve")

    test_file = tmp_path / "test.txt"
    test_file.write_text("contenido de prueba")

    encrypt_args = MagicMock(
        command="encrypt",
        input_file=str(test_file),
        to=["Bob"],
        sender="Alice"
    )

    with patch("src.main.build_parser") as mock_parser:
        mock_parser.return_value.parse_args.return_value = encrypt_args

        with patch("getpass.getpass", return_value="examplepassword"):
            main()

    vault_file = vault_path / "test.txt"
    assert vault_file.exists()

    return vault_file


def get_bob_decryption_data(users_path, tmp_path):
    bob_path = users_path / "Bob"

    private_key = load_private_key(
        bob_path / "private.pem",
        "examplepassword"
    )

    public_key = load_public_key(
        bob_path / "public.pem"
    )

    my_id = get_key_id(public_key)
    output_file = tmp_path / "recovered_test.txt"

    return private_key, my_id, output_file


def test_modified_metadata_rejected(mock_env):
    tmp_path, users_path, vault_path = mock_env

    vault_file = create_signed_container(tmp_path, users_path, vault_path)

    header_path = vault_file / "header.json"

    header = json.loads(header_path.read_bytes())
    header["file_name"] = "archivo_modificado.txt"
    header_path.write_bytes(json.dumps(header, sort_keys=True).encode())

    private_key, my_id, output_file = get_bob_decryption_data(users_path, tmp_path)

    with pytest.raises(ValueError):
        decrypt_container(
            str(vault_file),
            str(output_file),
            private_key,
            my_id,
            str(users_path)
        )


def test_signature_removed_rejected(mock_env):
    tmp_path, users_path, vault_path = mock_env

    vault_file = create_signed_container(tmp_path, users_path, vault_path)

    signature_path = vault_file / "signature"
    assert signature_path.exists()

    signature_path.unlink()

    private_key, my_id, output_file = get_bob_decryption_data(users_path, tmp_path)

    with pytest.raises(FileNotFoundError):
        decrypt_container(
            str(vault_file),
            str(output_file),
            private_key,
            my_id,
            str(users_path)
        )


def test_wrong_public_key_rejected(mock_env):
    tmp_path, users_path, vault_path = mock_env

    vault_file = create_signed_container(
        tmp_path,
        users_path,
        vault_path,
        create_eve=True
    )

    alice_public_key = users_path / "Alice" / "public.pem"
    eve_public_key = users_path / "Eve" / "public.pem"

    alice_public_key.write_bytes(eve_public_key.read_bytes())

    private_key, my_id, output_file = get_bob_decryption_data(users_path, tmp_path)

    with pytest.raises(ValueError):
        decrypt_container(
            str(vault_file),
            str(output_file),
            private_key,
            my_id,
            str(users_path)
        )