import json
import pytest
from unittest.mock import patch, MagicMock
from src.main import main, create_user


@pytest.fixture
def mock_env(tmp_path):
    users_path = tmp_path / "users"
    users_path.mkdir()
    vault_path = tmp_path / "vault"
    vault_path.mkdir()

    with patch("src.main.USERS_PATH", str(users_path)), \
         patch("src.main.VAULT_PATH", str(vault_path)):
        yield tmp_path, users_path, vault_path


def test_removing_recipient_entry_breaks_access(mock_env):
    tmp_path, users_path, vault_path = mock_env

    # Crear usuarios
    with patch("getpass.getpass", return_value="1234"):
        create_user("Alice")
        create_user("Bob")

    # Crear archivo de prueba
    content = "archivo secreto"
    test_file = tmp_path / "mensaje.txt"
    test_file.write_text(content)

    # Cifrar para Alice y Bob
    encrypt_args = MagicMock(
        command="encrypt",
        input_file=str(test_file),
        to=["Alice", "Bob"],
        sender="Alice"
    )

    with patch("src.main.build_parser") as mock_parser:
        mock_parser.return_value.parse_args.return_value = encrypt_args
        with patch("getpass.getpass", return_value="1234"):
                main()

    container_dir = vault_path / "mensaje.txt"
    assert container_dir.exists()  # nosec

    # Abrir y alterar header.json quitando a Bob
    header_path = container_dir / "header.json"
    with open(header_path, "r", encoding="utf-8") as f:
        header = json.load(f)

    header["recipients"] = [
        r for r in header["recipients"]
        if r.get("user") != "Bob"
    ]

    with open(header_path, "w", encoding="utf-8") as f:
        json.dump(header, f, sort_keys=True)

    # Bob ya no debe poder descifrar
    output_bob = tmp_path / "salida_bob.txt"
    decrypt_args = MagicMock(
        command="decrypt",
        container_dir=str(container_dir),
        output_file=str(output_bob),
        user="Bob"
    )

    with patch("getpass.getpass", return_value="1234"), \
         patch("src.main.build_parser") as mock_parser:
        mock_parser.return_value.parse_args.return_value = decrypt_args
        with pytest.raises(Exception):
            main()

    assert not output_bob.exists()  # nosec