import pytest
from unittest.mock import patch, MagicMock
from cryptography.exceptions import InvalidTag
from src.main import main, create_user, build_parser, decrypt_container, load_private_key, load_public_key, get_key_id


'''
Valid signature → file accepted
Modified ciphertext → rejected
'''


@pytest.fixture
def mock_env(tmp_path):
    users_path = tmp_path / "users"
    users_path.mkdir()
    vault_path = tmp_path / "vault_container"
    vault_path.mkdir()
    
    with patch("src.main.USERS_PATH", str(users_path)), \
         patch("src.main.VAULT_PATH", str(vault_path)):
        yield tmp_path, users_path, vault_path
             
def test_signature_and_tampering(mock_env):
    tmp_path, users_path, vault_path = mock_env
    
    with patch("getpass.getpass", return_value="examplepassword"):
        create_user("Alice")
        create_user("Bob")
        create_user("Eve")

    content = "tests D5 1"
    test_file = tmp_path / "test.txt"
    test_file.write_text(content)

    encrypt_sim = MagicMock(
        command="encrypt",
        input_file=str(test_file),
        to=["Alice", "Bob"],
        sender="Alice"
    )
    
    with patch("src.main.build_parser") as mock_parser:
        mock_parser.return_value.parse_args.return_value = encrypt_sim
        
        with patch("getpass.getpass", return_value="examplepassword"):
            main()

    vault_file = vault_path / "test.txt"
    assert vault_file.exists() # nosec

    output_test1 = tmp_path / "output_test1.txt"
    keypair_path = users_path / "Bob" 
    private_key = load_private_key(keypair_path / "private.pem", "examplepassword")
    pub_key = load_public_key(keypair_path / "public.pem")
    my_id = get_key_id(pub_key)  

    decrypt_args = MagicMock(
        command="decrypt",
        container_dir=str(vault_file),
        output_file=str(output_test1),
        user="Bob"
    )
    
    if decrypt_container(str(vault_file), str(output_test1), private_key, my_id, str(users_path)):
        assert output_test1.read_text() == content # the verifying is done inside

    ciphertext_path = vault_file / "ciphertext"
    data = ciphertext_path.read_bytes()
    modify_ciph = data[:-2]
    ciphertext_path.write_bytes(modify_ciph)

    with pytest.raises(ValueError) as tampering:
        decrypt_container(str(vault_file), str(output_test1), private_key, my_id, str(users_path))
    assert not "Authentication failed: container contents or metadata may have been tampered with" in str(tampering.value)