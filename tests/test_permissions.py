import pytest
from unittest.mock import patch, MagicMock
from src.main import main, create_user, get_master_key
from src.parser.parser import build_parser

'''
File shared with 2 users then both can decrypt.
Unauthorized user cannot decrypt.
'''

@pytest.fixture
def mock_env(tmp_path):
    users_path = tmp_path / "users"
    users_path.mkdir()
    vault_path = tmp_path / "vault"
    vault_path.mkdir()
    
    with patch("src.main.USERS_PATH", str(users_path)), \
         patch("src.main.VAULT_PATH", str(vault_path)):
        yield tmp_path, users_path, vault_path

def test_sharing_and_unauthorized_access(mock_env):
    tmp_path, users_path, vault_path = mock_env
    
    with patch("getpass.getpass", return_value="examplepassword"):
        create_user("Alice")
        create_user("Bob")
        create_user("Eve")

    content = "tests D3 1,2"
    test_file = tmp_path / "test.txt"
    test_file.write_text(content)

    encrypt_sim = MagicMock(
        command="encrypt",
        input_file=str(test_file),
        to=["Alice", "Bob"]
    )
    
    with patch("src.main.build_parser") as mock_parser:
        mock_parser.return_value.parse_args.return_value = encrypt_sim
        main()

    vault_file = vault_path / "test.txt"
    assert vault_file.exists()

    # Alice can decrypt ? same who shared
    output_alice = tmp_path / "output_alice.txt"
    with patch("getpass.getpass", return_value="examplepassword"):
        decrypt_alice = MagicMock(
            command="decrypt",
            container_dir=str(vault_file),
            output_file=str(output_alice),
            user="Alice"
        )
        with patch("src.main.build_parser") as mock_p:
            mock_p.return_value.parse_args.return_value = decrypt_alice
            main()
    
    assert output_alice.read_text() == content

    # Bob can decrypt ? the one it was shared to
    output_bob = tmp_path / "output_bob.txt"
    with patch("getpass.getpass", return_value="examplepassword"):
        decrypt_bob = MagicMock(
            command="decrypt",
            container_dir=str(vault_file),
            output_file=str(output_bob),
            user="Bob"
        )
        with patch("src.main.build_parser") as mock_p:
            mock_p.return_value.parse_args.return_value = decrypt_bob
            main()

    assert output_bob.read_text() == content

    # Eve shouldn't decrypt
    output_eve = tmp_path / "output_eve.txt"
    with patch("getpass.getpass", return_value="examplepassword"):
        decrypt_args = MagicMock(
            command="decrypt",
            container_dir=str(vault_file),
            output_file=str(output_eve),
            user="Eve"
        )
        with patch("src.main.build_parser") as mock_p:
            mock_p.return_value.parse_args.return_value = decrypt_args
            main()

    assert not output_eve.exists(), "Eve no debe poder descifrar el archivo"

# Wrong private key then fails
def test_wrong_password_cannot_decrypt(mock_env):
    tmp_path, users_path, vault_path = mock_env

    with patch("getpass.getpass", return_value="correctpassword"):
        create_user("Alice")

    content = "sensitive data 123"
    test_file = tmp_path / "secret.txt"
    test_file.write_text(content)

    encrypt_args = MagicMock(
        command="encrypt",
        input_file=str(test_file),
        to=["Alice"]
    )
    with patch("getpass.getpass", return_value="correctpassword"), \
         patch("src.main.build_parser") as mock_parser:
        mock_parser.return_value.parse_args.return_value = encrypt_args
        main()

    vault_file = vault_path / "secret.txt"
    assert vault_file.exists()

    output_file = tmp_path / "output_alice.txt"
    decrypt_args = MagicMock(
        command="decrypt",
        container_dir=str(vault_file),
        output_file=str(output_file),
        user="Alice"
    )
    with patch("getpass.getpass", return_value="wrongpassword"), \
         patch("src.main.build_parser") as mock_p:
        mock_p.return_value.parse_args.return_value = decrypt_args
        main()

    assert not output_file.exists(), "El archivo resultante no se genera cuando el descifrado falla"