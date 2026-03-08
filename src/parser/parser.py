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

    encrypt_parser = subparsers.add_parser(
        "encrypt",
        help="Encrypt a file into a vault container"
    )

    encrypt_parser.add_argument(
        "input_file",
        type=str,
        help="File to encrypt"
    )

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

    return parser
