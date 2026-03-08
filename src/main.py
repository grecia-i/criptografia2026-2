import os
import argparse
from encryption.encrypt import *
from decryption.decrypt import *
from parser.parser import build_parser

VAULT_PATH = "vault_container"


def validate_container(container_dir: str) -> None:
    required_files = [
        os.path.join(container_dir, "header.json"),
        os.path.join(container_dir, "nonce"),
        os.path.join(container_dir, "ciphertext"),
        os.path.join(container_dir, "key", "priv.key"),
    ]

    for path in required_files:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Missing required container file: {path}")


def handle_encrypt(input_file: str) -> None:
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")

    vault_container = os.path.join(VAULT_PATH, os.path.basename(input_file))
    key = generate_key()

    encrypt_file(input_file, vault_container, key)
    print(f"Encryption successful. Vault container created at: {vault_container}")


def handle_decrypt(container_dir: str, output_file: str) -> None:
    if not os.path.isdir(container_dir):
        raise FileNotFoundError(f"Container does not exist: {container_dir}")

    validate_container(container_dir)

    key_path = os.path.join(container_dir, "key", "priv.key")
    key = read_key(key_path)

    decrypt_container(container_dir, output_file, key)
    print(f"Decryption successful. Plaintext recovered at: {output_file}")


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "encrypt":
            handle_encrypt(args.input_file)

        elif args.command == "decrypt":
            handle_decrypt(args.container_dir, args.output_file)

        else:
            print("Unknown command.")

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")

    except PermissionError as e:
        print(f"[ERROR] Permission denied: {e}")

    except ValueError as e:
        print(f"[ERROR] {e}")

    except Exception as e:
        print(f"[ERROR] Unexpected failure: {e}")


if __name__ == "__main__":
    main()