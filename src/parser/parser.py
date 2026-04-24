import argparse

def build_parser():
    parser = argparse.ArgumentParser(
        description="Secure Digital Document Vault CLI"
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands"
    )

    #Create user
    user_parser = subparsers.add_parser(
        "create-user",
        help = "Create a new user")
    user_parser.add_argument("username", type=str)


    #Encrypt
    encrypt_parser = subparsers.add_parser(
        "encrypt",
        help="Encrypt a file into a vault container"
    )

    encrypt_parser.add_argument(
        "input_file",
        type=str,
        help="File to encrypt"
    )

    encrypt_parser.add_argument(
        "--to",
        nargs="+", 
        required=True,
        help="Authorized user list, separated by spaces"
    )

    encrypt_parser.add_argument(
        "--sender",
        required=True,
        help="Sender username"
    )

    #Decrypt
    decrypt_parser = subparsers.add_parser(
        "decrypt",
        help="Decrypt a vault container"
    )

    decrypt_parser.add_argument(
        "container_dir",
        type=str,
        help="Vault container directory"
    )

    decrypt_parser.add_argument(
        "output_file",
        type=str,
        help="Path where the recovered plaintext file will be written"
    )

    decrypt_parser.add_argument(
        "--user", 
        required=True,
        help = "Your username (create a user with 'create-user <name>')"
    )

    return parser
