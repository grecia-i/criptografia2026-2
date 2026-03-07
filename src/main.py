import os
import argparse
from encryption.encrypt import *
from decryption.decrypt import *
from parser.parser import build_parser

VAULT_PATH = "vault_container"
KEY_PATH = os.path.join(VAULT_PATH, "key", "priv.key")

def main():
    # parser = argparse.ArgumentParser(description="A secure file encryption module")
    # parser.add_argument("file",nargs='?', type=str, help="The path of the file to be encrypted")
    # parser.add_argument("command",nargs="", type=str,choices=["encrypt","decrypt"])
    # args = parser.parse_args()
    parser = build_parser()
    args = parser.parse_args()
    print(args)
    
    if os.path.isfile(KEY_PATH):
        key=read_key(KEY_PATH)
        print("Key read from file, key is: \n", key.hex()) #debug
    else:
        key = generate_key()
        write_key(KEY_PATH,key)
        print("New key generated, key is: \n", key.hex()) #debug


    if(args.command == "encrypt"):
        file_name = args.input_file
        if not (os.path.isfile(file_name)):
            print(f"ERROR, {file_name} does not exist")
            return

        vault_container = os.path.join(VAULT_PATH, file_name)
        print("Vault container = ", vault_container) #debug
        encrypt_file(file_name, vault_container, key)


    elif(args.command =="decrypt"):
        vault_container = args.container_dir
        if os.path.isdir(vault_container):
            decrypt_container(vault_container, args.output_file, key)


        


    
    
    

if __name__ == "__main__":
    main()