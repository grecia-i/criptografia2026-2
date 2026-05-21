import os
import json
import secrets
import shutil
from flask import Flask, render_template, jsonify, request, send_file
from datetime import datetime, timezone
from src.encryption.keys import generate_key_pair, store_public_key, load_public_key, get_key_id
from src.encryption.keystore import create_keystore, load_keystore
from src.encryption.encrypt import encrypt_file
from src.encryption.decrypt import decrypt_container

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuración de rutas
VAULT_PATH = "vault_container"
USERS_PATH = "users"
os.makedirs(VAULT_PATH, exist_ok=True)
os.makedirs(USERS_PATH, exist_ok=True)

@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').lower().strip()
    user_dir = os.path.join(USERS_PATH, username)
    
    if os.path.exists(user_dir):
        return jsonify({"status": "error", "message": "El usuario ya existe"}), 400
    
    os.makedirs(user_dir)
    with open(os.path.join(user_dir, "profile.json"), "w") as f:
        json.dump({"nombre": data.get('nombre')}, f, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    
    priv, pub = generate_key_pair()
    create_keystore(priv, data['password'], os.path.join(user_dir, "keystore.json"), get_key_id(pub))
    store_public_key(pub, os.path.join(user_dir, "public.pem"))
    return jsonify({"status": "success"})

@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.get_json()
    username = data.get('username', '').lower().strip()
    try:
        load_keystore(os.path.join(USERS_PATH, username, "keystore.json"), data['password'])
        return jsonify({"status": "success", "user": {"username": username, "nombre": username.capitalize()}})
    except:
        return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401

@app.route('/api/encrypt', methods=['POST'])
def encrypt():
    file = request.files.get('file')
    sender = request.form.get('sender', '').lower().strip()
    recipient = request.form.get('recipient', '').lower().strip()
    passphrase = request.form.get('passphrase')

    if not all([file, sender, recipient, passphrase]):
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400

    uid = secrets.token_hex(4)
    temp_path = os.path.join(VAULT_PATH, f"temp_{uid}_{file.filename}")
    file.save(temp_path)
    
    vault_dir = os.path.join(VAULT_PATH, f"{file.filename}_{uid}_vault")
    zip_path = f"{vault_dir}.zip"

    try:
        priv = load_keystore(os.path.join(USERS_PATH, sender, "keystore.json"), passphrase)
        pub = load_public_key(os.path.join(USERS_PATH, recipient, "public.pem"))
        
        encrypt_file(
            temp_path,
            vault_dir,
            [{"user": recipient, "id": get_key_id(pub), "key": pub}],
            priv,
            get_key_id(load_public_key(os.path.join(USERS_PATH, sender, "public.pem")))
        )
        
        shutil.make_archive(vault_dir, 'zip', vault_dir)
        if os.path.exists(temp_path): os.remove(temp_path)
        
        return send_file(zip_path, as_attachment=True, download_name=f"{file.filename}.zip")
    except Exception:
        return jsonify({"status": "error", "message": "Error en la firma o cifrado. Verifique su contraseña."}), 401

@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    file = request.files.get('file')
    passphrase = request.form.get('passphrase')
    username = request.form.get('user', '').lower().strip()
    
    uid = secrets.token_hex(4)
    zip_path = os.path.join(VAULT_PATH, f"in_{uid}.zip")
    extract_dir = os.path.join(VAULT_PATH, f"ex_{uid}")
    file.save(zip_path)
    shutil.unpack_archive(zip_path, extract_dir, 'zip')
    
    out_path = os.path.join(VAULT_PATH, f"out_{uid}")
    try:
        priv = load_keystore(os.path.join(USERS_PATH, username, "keystore.json"), passphrase)
        user_pub = load_public_key(os.path.join(USERS_PATH, username, "public.pem"))
        my_id = get_key_id(user_pub)
        decrypt_container(extract_dir, out_path, priv, my_id, USERS_PATH)
        return send_file(out_path, as_attachment=True)
    except Exception:
        return jsonify({"status": "error", "message": "No se pudo descifrar. Verifique su clave."}), 401

@app.route('/api/archivos', methods=['GET'])
def get_archivos():
    user = request.args.get('user', '').lower().strip()
    res = []
    if os.path.exists(VAULT_PATH):
        for d in os.listdir(VAULT_PATH):
            if os.path.isdir(os.path.join(VAULT_PATH, d)):
                header_path = os.path.join(VAULT_PATH, d, "header.json")
                if os.path.exists(header_path):
                    with open(header_path) as f:
                        if any(r['user'] == user for r in json.load(f).get('recipients', [])):
                            res.append({"archivo": d, "remitente": "Sistema", "container": d})
    return jsonify(res)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        "archivos_protegidos": len([d for d in os.listdir(VAULT_PATH) if os.path.isdir(os.path.join(VAULT_PATH, d))]),
        "usuarios_activos": len([d for d in os.listdir(USERS_PATH) if os.path.isdir(os.path.join(USERS_PATH, d))]),
        "pendientes_liberar": 0
    })

@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = []
    if os.path.exists(USERS_PATH):
        for d in os.listdir(USERS_PATH):
            user_dir = os.path.join(USERS_PATH, d)
            if os.path.isdir(user_dir):
                nombre = d.capitalize()
                profile_path = os.path.join(user_dir, "profile.json")
                if os.path.exists(profile_path):
                    try:
                        with open(profile_path, "r") as f:
                            nombre = json.load(f).get("nombre", d.capitalize())
                    except:
                        pass
                
                usuarios.append({
                    "username": d, 
                    "nombre": nombre, 
                    "estado": "Activo"
                })
    return jsonify(usuarios)

@app.route('/api/keys/status', methods=['GET'])
def get_keys_status():
    user = request.args.get('user', '').lower().strip()
    keystore_path = os.path.join(USERS_PATH, user, "keystore.json")
    pubkey_path = os.path.join(USERS_PATH, user, "public.pem")
    
    status = []
    
    # Llave Privada
    if os.path.exists(keystore_path):
        with open(keystore_path, "r") as f:
            data = json.load(f)
            status.append({
                "alias": "Llave privada", 
                "meta": "Llave para firma y descifrado", 
                "badge": "ACTIVA", 
                "class": "badge-active"
            })
            
    if os.path.exists(pubkey_path):
        status.append({
            "alias": "Llave pública", 
            "meta": "Llave de emparejamiento e intercambio asimétrico", 
            "badge": "ACTIVA", 
            "class": "badge-active"
        })
        
    return jsonify(status)

@app.route('/api/rotate-keys', methods=['POST'])
def rotate_keys():
    data = request.get_json()
    username = data.get('username', '').lower().strip()
    password = data.get('password') # Usamos la contraseña actual para autorizar la rotación

    user_dir = os.path.join(USERS_PATH, username)
    keystore_path = os.path.join(user_dir, "keystore.json")
    pubkey_path = os.path.join(user_dir, "public.pem")

    try:
        load_keystore(keystore_path, password)
        priv, pub = generate_key_pair()
        create_keystore(priv, password, keystore_path, get_key_id(pub))
        store_public_key(pub, pubkey_path)
        
        return jsonify({"status": "success", "message": "Llaves rotadas correctamente. Seguridad renovada."})
    except Exception as e:
        return jsonify({"status": "error", "message": "No se pudo rotar: verifica tu contraseña."}), 401

if __name__ == '__main__':
    app.run(debug=True)