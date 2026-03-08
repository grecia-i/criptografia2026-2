import os
from encryption.encrypt import *
from decryption.decrypt import *
from derivation.pw_derivation import *
from parser.parser import build_parser
import getpass
import secrets

VAULT_PATH = "vault_container"
KEY_PATH = os.path.join(VAULT_PATH,"priv.key")
SALT_PATH = os.path.join(VAULT_PATH,"salt.bin")


def main():
    # parser = argparse.ArgumentParser(description="A secure file encryption module")
    # parser.add_argument("file",nargs='?', type=str, help="The path of the file to be encrypted")
    # parser.add_argument("command",nargs="", type=str,choices=["encrypt","decrypt"])
    # args = parser.parse_args()
    parser = build_parser()
    args = parser.parse_args()
    print(args)

    if not (os.path.isfile(SALT_PATH)):
        print("Password has not been set, please create a password")
        print("NOTE: losing the password means losing access to ALL encrypted files")
        print()
        while True:
            password = getpass.getpass(prompt='Enter your password: ')
            password_confirm = getpass.getpass(prompt='Confirm your password: ')

            if (password == password_confirm):
                salt = secrets.token_bytes(16)
                os.makedirs(VAULT_PATH, exist_ok=True)
                write_salt(salt,SALT_PATH)
                break
            print("Passwords do not match")
    else:
        password = getpass.getpass(prompt='Enter your password: ')
        salt= read_salt(SALT_PATH)


    master_key=derive_key(password,salt)
    print("Master key is: ",master_key.hex()) #DEBUG
        

    


    #Una llave para todos los archivos
    # if os.path.isfile(KEY_PATH):
    #     key=read_key(KEY_PATH)
    #     print("Key read from file, key is: \n", key.hex()) #debug
    # else:
    #     key = generate_key()
    #     print("New key generated, key is: \n", key.hex()) #debug


    if(args.command == "encrypt"):
        file_name = args.input_file
        if not (os.path.isfile(file_name)):
            print(f"ERROR, {file_name} does not exist")
            return

        vault_container = os.path.join(VAULT_PATH, file_name)
        print("Vault container = ", vault_container) #debug

        encrypt_file(file_name, vault_container,master_key)


    elif(args.command =="decrypt"):

        vault_container = args.container_dir

        if os.path.isdir(vault_container):
            # key_path = os.path.join(vault_container,"file.key")
            # if(os.path.isfile(key_path)):
            #     encrypted_key = read_key(key_path)
            #     key  = decrypt_key(encrypted_key,master_key,vault_container)
            #     print("read key is :",key.hex()) #debug

            #     decrypt_container(vault_container, args.output_file, key)
            decrypt_container(vault_container,args.output_file,master_key)
            print("Container decryption successful, contents written to: ",args.output_file)
        else:
            print(f"ERROR: Container {vault_container} does not exist")
            return


        


    
    
    

if __name__ == "__main__":
    main()