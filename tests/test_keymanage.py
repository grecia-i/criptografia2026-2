import pytest
import json
import random
from unittest.mock import patch, MagicMock
from cryptography.exceptions import InvalidTag
from src.main import main, create_user, build_parser, decrypt_container, load_keystore, load_public_key, get_key_id

'''
a) Correct password → access granted
b) Wrong password → access denied ALREADY DONE IN PERMISSIONS
Modified keystore → failure 
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
             

def test_correct_password_dec(mock_env):
    tmp_path, users_path, vault_path = mock_env
    
    with patch("getpass.getpass", return_value="examplepassword"):
        create_user("Alice")
        create_user("Bob")

    content = "tests D6 1"
    test_file = tmp_path / "test.txt"
    test_file.write_text(content)

    encrypt_sim = MagicMock(
        command="encrypt",
        input_file=str(test_file),
        to=["Bob"],
        sender="Alice"
    )
    
    with patch("src.main.build_parser") as mock_parser:
        mock_parser.return_value.parse_args.return_value = encrypt_sim
        with patch("getpass.getpass", return_value="examplepassword"):
            main()

    vault_file = vault_path / "test.txt"
    assert vault_file.exists() # nosec

    # Passing a wrong password
    output_bob = tmp_path / "output_alice.txt"
    with pytest.raises(ValueError) as password:
        with patch("getpass.getpass", return_value="wrongpassword"):
            decrypt_alice = MagicMock(
                command="decrypt",
                container_dir=str(vault_file),
                output_file=str(output_bob),
                user="Bob"
            )
            with patch("src.main.build_parser") as mock_p:
                mock_p.return_value.parse_args.return_value = decrypt_alice
                main()
    assert "Decryption failed: container may have been tampered with" in str(password.value) # nosec

def test_keystore_tampering(mock_env):
    tmp_path, users_path, vault_path = mock_env
    
    with patch("getpass.getpass", return_value="examplepassword"):
        create_user("Alice")
        create_user("Bob")

    content = "tests D6 3"
    test_file = tmp_path / "test.txt"
    test_file.write_text(content)

    encrypt_sim = MagicMock(
        command="encrypt",
        input_file=str(test_file),
        to=["Bob"],
        sender="Alice"
    )
    
    with patch("src.main.build_parser") as mock_parser:
        mock_parser.return_value.parse_args.return_value = encrypt_sim
        
        with patch("getpass.getpass", return_value="examplepassword"):
            main()

    vault_file = vault_path / "test.txt"

    output_test = tmp_path / "output_test.txt"
    keypair_path = users_path / "Bob" 
    private_key = load_keystore(keypair_path / "keystore.json", "examplepassword")
    pub_key = load_public_key(keypair_path / "public.pem")
    my_id = get_key_id(pub_key) 

    keystore_path = keypair_path / "keystore.json"

    with open(keystore_path, "r+", encoding="utf-8") as f:
        keystore = json.load(f)
        keystore['kdf'] = "Argona2"
        f.seek(0)
        print(keystore['kdf'])
        json.dump(keystore, f, sort_keys=True, separators=(',', ':'))
        f.truncate()

    with pytest.raises(ValueError) as tampering:
        load_keystore(keystore_path, "examplepassword")
    assert "Decryption failed: container may have been tampered with" in str(tampering.value) # nosec