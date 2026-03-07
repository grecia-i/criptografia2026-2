import os
import argparse
from encryption.encrypt import *
from decryption.decrypt import *

VAULT_PATH = "vault_container"
KEY_PATH = os.path.join(VAULT_PATH, "key", "priv.key")

def main():
    parser = argparse.ArgumentParser(description="A secure file encryption module")
    parser.add_argument("--f",nargs='?', type=str, help="The path of the file to be encrypted")
    args = parser.parse_args()
    #print(args.f)
    if args.f == None:
        file_name = input("Enter the name of the file (e.g., secret.txt):  ")
    else:
        file_name = args.f

    if not (os.path.exists(file_name)):
        print(f"ERROR, {file_name} does not exist")
        return

    if os.path.exists(KEY_PATH):
        key=read_key(KEY_PATH)
        print("Key read from file, key is: \n", key.hex())
    else:
        key = generate_key()
        write_key(KEY_PATH,key)
        print("New key generated, key is: \n", key.hex())

    vault_container = os.path.join(VAULT_PATH, file_name)
    print("Vault container = ", vault_container)

    encrypt_file(file_name, vault_container, key)
    
    decrypt_container(vault_container, "recovered.txt", key)

if __name__ == "__main__":
    main()