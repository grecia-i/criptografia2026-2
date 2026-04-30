import os
import getpass
import secrets
from src.encryption.encrypt import encrypt_file
from src.encryption.decrypt import decrypt_container
from src.encryption.keys import (
    generate_key_pair,
    store_private_key,
    store_public_key,
    load_private_key,
    load_public_key,
    get_key_id
)
from src.parser.parser import build_parser

VAULT_PATH = "vault_container"
USERS_PATH = "users"

def create_user(username):
    user_dir = os.path.join(USERS_PATH, username)
    if os.path.exists(user_dir):
        raise FileExistsError(f"User '{username}' already exists")

    os.makedirs(user_dir)
    password = getpass.getpass("Set password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm or not password:
        raise ValueError("Invalid password")

    private_key, public_key = generate_key_pair()
    store_private_key(private_key, os.path.join(user_dir, "private.pem"), password)
    store_public_key(public_key, os.path.join(user_dir, "public.pem"))
    print(f"User '{username}' created successfully")

def validate_container(container_dir):
    if not os.path.isdir(container_dir):
        raise FileNotFoundError(f"Container does not exist: {container_dir}")
    # Ahora la firma es obligatoria
    required_files = ["header.json", "nonce", "ciphertext", "signature"]
    for file_name in required_files:
        file_path = os.path.join(container_dir, file_name)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Missing required file: {file_path}")
    return True

def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "create-user":
            create_user(args.username)

        elif args.command == "encrypt":
            # 1. Validaciones iniciales
            if not os.path.isfile(args.input_file):
                raise FileNotFoundError(f"Input file not found: {args.input_file}")
            
            vault_container = os.path.join(VAULT_PATH, os.path.basename(args.input_file))
            if os.path.exists(vault_container):
                raise FileExistsError(f"Vault container already exists: {vault_container}")

            # 2. CARGAR LLAVE DEL REMITENTE PARA FIRMAR (Nuevo para D4)
            sender_dir = os.path.join(USERS_PATH, args.sender)
            if not os.path.isdir(sender_dir):
                raise FileNotFoundError(f"Sender '{args.sender}' not found")
            
            print(f"--- Authentication for Sender: {args.sender} ---")
            password_sender = getpass.getpass("Enter your password: ")
            signer_key = load_private_key(os.path.join(sender_dir, "private.pem"), password_sender)
            
            sender_pub = load_public_key(os.path.join(sender_dir, "public.pem"))
            sender_id = get_key_id(sender_pub)

            # 3. Cargar llaves públicas de destinatarios
            recipient_public_keys = []
            for username in args.to:
                pub_path = os.path.join(USERS_PATH, username, "public.pem")
                if not os.path.isfile(pub_path):
                    print(f"Warning: User {username} not found, skipping.")
                    continue
                pub = load_public_key(pub_path)
                recipient_public_keys.append({
                    "user": username,
                    "id": get_key_id(pub),
                    "key": pub
                })

            if not recipient_public_keys:
                raise ValueError("No valid recipients provided.")

            # 4. Encriptar y FIRMAR
            os.makedirs(vault_container, exist_ok=True)
            encrypt_file(args.input_file, vault_container, recipient_public_keys, signer_key, sender_id)
            print(f"Success: File saved at {vault_container}")

        elif args.command == "decrypt":
            validate_container(args.container_dir)
            
            user_dir = os.path.join(USERS_PATH, args.user)
            if not os.path.isdir(user_dir):
                raise FileNotFoundError(f"User '{args.user}' not found")
            
            password = getpass.getpass(f"Password for {args.user}: ")
            private_key = load_private_key(os.path.join(user_dir, "private.pem"), password)
            
            public_key = load_public_key(os.path.join(user_dir, "public.pem"))
            my_id = get_key_id(public_key)

            decrypt_container(args.container_dir, args.output_file, private_key, my_id, USERS_PATH)
            print(f"Success: File saved to {args.output_file}")

    except Exception as e:
        print(f"ERROR: {e}")
        raise e

if __name__ == "__main__":
    main()
