import os
import getpass
import secrets
from encryption.encrypt import encrypt_file
from encryption.decrypt import decrypt_container
from derivation.pw_derivation import derive_key, write_salt, read_salt
from parser.parser import build_parser

VAULT_PATH = "vault_container"
SALT_PATH = os.path.join(VAULT_PATH,"salt.bin")


def get_master_key():
    if not os.path.isfile(SALT_PATH):
        print("Password has not been set, please create a password")
        print("NOTE: losing the password means losing access to ALL encrypted files")
        print()

        while True:
            password = getpass.getpass(prompt='Enter your password: ')
            password_confirm = getpass.getpass(prompt='Confirm your password: ')

            if not password:
                print("Password cannot be empty")
                continue

            if password == password_confirm:
                salt = secrets.token_bytes(16)
                os.makedirs(VAULT_PATH, exist_ok=True)
                write_salt(salt, SALT_PATH)
                break

            print("Passwords do not match")
    else:
        password = getpass.getpass(prompt='Enter your password: ')
        if not password:
            raise ValueError("Password cannot be empty")
        
        salt = read_salt(SALT_PATH)
        

    master_key = derive_key(password, salt)
    return master_key

def validate_container(container_dir):
    if not os.path.isdir(container_dir):
        raise FileNotFoundError(f"Container does not exist: {container_dir}")

    required_files = [
        "header.json",
        "nonce",
        "ciphertext",
        "file.key",
        "key_nonce"
    ]

    for file_name in required_files:
        file_path = os.path.join(container_dir, file_name)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Missing required container file: {file_path}")

    return True

def validate_input_file(input_file):
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")
    
def validate_encrypt_output(vault_container):
    if os.path.isdir(vault_container):
        raise FileExistsError(f"Vault container already exists: {vault_container}")

def validate_decrypt_output(output_file):
    if os.path.exists(output_file):
        raise FileExistsError(f"Output file already exists: {output_file}")


def main():
    parser = build_parser()
    args = parser.parse_args()
    #print(args)
    try:
        if(args.command == "encrypt"):
            file_name = args.input_file
            validate_input_file(file_name)
            
            vault_container = os.path.join(VAULT_PATH, os.path.basename(file_name))
            validate_encrypt_output(vault_container)
            print("Vault container = ", vault_container) #debug

            master_key = get_master_key()

            encrypt_file(file_name, vault_container,master_key)
            print("Container encryption successful, created at: ", vault_container)

        elif(args.command =="decrypt"):

            vault_container = args.container_dir
            validate_container(vault_container)

            master_key = get_master_key()
            validate_decrypt_output(args.output_file)
            decrypt_container(vault_container, args.output_file, master_key)
            print("Container decryption successful, contents written to: ", args.output_file)

    except FileNotFoundError as e:
        print(f"ERROR: {e}")

    except PermissionError as e:
        print(f"ERROR: Permission denied - {e}")

    except ValueError as e:
        print(f"ERROR: {e}")

    except Exception as e:
        print(f"ERROR: Unexpected failure - {e}")
    
    except FileExistsError as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()