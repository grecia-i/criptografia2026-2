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
    users_path = tmp_path / "users"import pytest
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
    
    # Patch the global paths in your module to use these temp folders
    with patch("main.USERS_PATH", str(users_path)), \
         patch("main.VAULT_PATH", str(vault_path)):
        yield tmp_path, users_path, vault_path

def test_sharing_and_unauthorized_access(mock_env):
    tmp_path, users_path, vault_path = mock_env
    
    # temp users 
    with patch("getpass.getpass", return_value="examplepassword"):
        create_user("Alice")
        create_user("Bob")
        create_user("Eve")

    # temp mock file
    content = "tests D3 1,2"
    test_file = tmp_path / "test.txt"
    test_file.write_text(content)

    # run a mock encryption
    encrypt_sim = MagicMock(
        command="encrypt",
        input_file=str(test_file),
        to=["Alice", "Bob"]
    )
    
    with patch("build_parser") as mock_parser:
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

        with patch("build_parser") as mock_p:
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

        with patch("build_parser") as mock_p:
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

        with patch("build_parser") as mock_p:
            mock_p.return_value.parse_args.return_value = decrypt_args
        
            with pytest.raises(Exception):
                main()

    users_path.mkdir()
    vault_path = tmp_path / "vault"
    vault_path.mkdir()
    
    # Patch the global paths in your module to use these temp folders
    with patch("main.USERS_PATH", str(users_path)), \
         patch("main.VAULT_PATH", str(vault_path)):
        yield tmp_path, users_path, vault_path

def test_sharing_and_unauthorized_access(mock_env):
    tmp_path, users_path, vault_path = mock_env
    
    # temp users 
    with patch("getpass.getpass", return_value="examplepassword"):
        create_user("Alice")
        create_user("Bob")
        create_user("Eve")

    # temp mock file
    content = "tests D3 1,2"
    test_file = tmp_path / "test.txt"
    test_file.write_text(content)

    # run a mock encryption
    encrypt_sim = MagicMock(
        command="encrypt",
        input_file=str(test_file),
        to=["Alice", "Bob"]
    )
    
    with patch("build_parser") as mock_parser:
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

        with patch("build_parser") as mock_p:
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

        with patch("build_parser") as mock_p:
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

        with patch("build_parser") as mock_p:
            mock_p.return_value.parse_args.return_value = decrypt_args
        
            with pytest.raises(Exception):
                main()
