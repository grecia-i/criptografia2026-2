# Key Management

Contribuyentes:

- Castillo Soto Jacqueline,
- Meneses Calderas Grecia Irais,
- Pérez Osorio Luis Eduardo,
- Rivas Gil María Lucía.

## ¿Qué pasa si un atacante roba el keystore?

El atacante no obtiene directamente la llave privada del usuario, porque nuestro sistema no almacena las llaves privadas en texto plano. La llave privada se almacena cifrada con AES-GCM y la clave de cifrado se deriva de la contraseña del usuario mediante Argon2id. El keystore contiene salt, nonce, parámetros del KDF y la llave privada cifrada.

Esto significa que el atacante necesitaría conocer la contraseña correcta para poder derivar la clave y descifrar la llave privada. Además, si intenta modificar el contenido del keystore, AES-GCM puede detectar alteraciones mediante su etiqueta de autenticación. Por lo que en nuestro código, si la validación falla, se lanza un error y no se entrega la llave privada.

## ¿Qué pasa si la contraseña es débil?

El robo del keystore sí representa un riesgo si la contraseña del usuario es débil, porque el atacante podría intentar ataques offline de fuerza bruta o diccionario. Argon2id ayuda a hacer estos ataques más costosos, la seguridad final depende también de que el usuario use una contraseña fuerte.

## ¿Qué pasa si el dispositivo está comprometido?

Si el dispositivo está comprometido, el sistema ya no puede garantizar completamente la seguridad. Aunque el keystore esté cifrado, un atacante con malware, keylogger o acceso al sistema podría capturar la contraseña cuando el usuario la escribe, leer archivos antes o después de cifrarlos, o acceder a la llave privada mientras está temporalmente descifrada en memoria.

Por eso, nuestro sistema protege principalmente contra el robo de archivos almacenados, como el keystore o el contenedor cifrado, pero no protege contra un dispositivo infectado o controlado por un atacante. En ese caso, se debe considerar la llave como comprometida, revocarla, rotarla y generar nuevas llaves para el usuario.

## ¿Qué protege nuestro sistema y contra qué NO protege nuestro sistema?

Nuestro sistema protege contra el robo de archivos almacenados, como el keystore y los contenedores cifrados, ya que las llaves privadas nunca se guardan en texto plano y los archivos se protegen mediante cifrado autenticado. También protege contra modificaciones no autorizadas, porque AES-GCM y las firmas permiten detectar alteraciones. Además, el acceso se limita a los usuarios autorizados mediante llaves públicas y privadas. Sin embargo, el sistema no protege contra contraseñas débiles, dispositivos comprometidos, malware, keyloggers o atacantes que ya tengan acceso al sistema del usuario. Tampoco puede evitar que un usuario autorizado comparta manualmente un archivo después de descifrarlo.

## Key Management Design

### Selección del KDF y sus parámetros

Nuestro sistema utiliza Argon2id como función de derivación de claves basada en contraseña (KDF). Argon2id fue seleccionado porque es un KDF moderno diseñado para hacer más costosos los ataques de fuerza bruta, ya que requiere tanto recursos computacionales como memoria. La contraseña del usuario nunca se almacena; en su lugar, se combina con una salt generada aleatoriamente para derivar una clave de cifrado de 256 bits. Esta clave derivada se utiliza posteriormente con AES-GCM para cifrar y descifrar la llave privada del usuario dentro del keystore.

Los parámetros utilizados son: una salt de 16 bytes, una longitud de clave derivada de 32 bytes, 3 iteraciones, 4 lanes de paralelización y un costo de memoria de 64 × 1024 KiB. Estos valores se almacenan dentro de los metadatos del keystore, de manera que el sistema pueda repetir el mismo proceso de derivación cuando el usuario ingrese la contraseña correcta. Este diseño ayuda a proteger la llave privada incluso si el archivo del keystore es robado, aunque la seguridad final también depende de la fortaleza de la contraseña utilizada por el usuario.

### Formato de almacenamiento de llaves

Nuestro sistema utiliza un formato estructurado basado en JSON para almacenar las llaves criptográficas de manera segura dentro del keystore. El archivo keystore.json contiene la llave privada cifrada junto con la información necesaria para poder recuperarla únicamente mediante la contraseña correcta del usuario. El keystore almacena metadatos como el algoritmo KDF, parámetros de derivación, salt, nonce, identificador de la llave pública y estado de la llave. La llave privada nunca se guarda en texto plano; se serializa en formato PEM y se cifra con AES-GCM usando una clave derivada mediante Argon2id. Además, el sistema utiliza AAD para proteger la integridad de los metadatos, permitiendo detectar modificaciones no autorizadas en el archivo.

Este diseño permite mantener separadas las llaves públicas y privadas: las llaves públicas se almacenan en archivos public.pem, mientras que las llaves privadas permanecen protegidas dentro del keystore.json. De esta forma, el sistema puede administrar autenticación, cifrado y recuperación de llaves de manera consistente y segura.

Para una mejor visualización, el esquema del formato de almacenamiento de llaves utilizado por el sistema es el siguiente:

```text
users/
└── <username>/
    ├── keystore.json
    │   ├── version
    │   ├── kdf
    │   ├── kdf_parameters
    │   │   ├── iterations
    │   │   ├── lanes
    │   │   ├── memory_cost
    │   │   └── length
    │   ├── salt
    │   ├── nonce
    │   ├── encrypted_key
    │   ├── public_key_id
    │   ├── created_at
    │   └── status
    └── public.pem
```

En resumen, el formato de almacenamiento de llaves del sistema se organiza por usuario dentro del directorio users/. Cada usuario tiene una carpeta propia que contiene dos archivos principales: keystore.json y public.pem. El archivo keystore.json almacena la llave privada cifrada en el campo encrypted_key, junto con los elementos anteriormente mencionados. La llave pública se almacena por separado en el archivo public.pem, lo que permite compartirla con otros usuarios sin exponer la llave privada.

### Estrategia de respaldo

Nuestro sistema incluye una estrategia de respaldo para permitir la recuperación de las llaves del usuario sin debilitar su seguridad. El respaldo copia únicamente los archivos necesarios para restaurar el acceso criptográfico del usuario: keystore.json y public.pem.

La función backup_keystore() crea una carpeta de respaldo y copia dentro de ella el keystore.json y la llave pública del usuario. Esto no expone directamente la llave privada, porque dentro del keystore.json la llave privada sigue estando cifrada con AES-GCM mediante una clave derivada de la contraseña del usuario con Argon2id.

Para recuperar las llaves, la función restore_keystore() vuelve a copiar esos archivos desde la carpeta de respaldo al directorio del usuario. Sin embargo, el respaldo no permite acceder a la llave privada por sí solo: el usuario todavía necesita ingresar la contraseña correcta para que el sistema pueda derivar la clave y descifrar la llave privada. Es importante considerar que el respaldo debe almacenarse en un lugar seguro, porque si se combina con una contraseña débil o robada, podría representar un riesgo.

### Supuestos de seguridad

Nuestro sistema parte de varios supuestos de seguridad necesarios para que la protección de llaves funcione correctamente. Primero, se asume que el usuario utiliza una contraseña fuerte y que no la comparte con terceros. La contraseña es el elemento principal para derivar la clave que protege la llave privada, por lo que una contraseña débil podría permitir ataques de fuerza bruta o diccionario.

También se asume que el dispositivo del usuario no está comprometido al momento de usar el sistema. Si existe malware, keyloggers o control del sistema operativo por parte de un atacante, la contraseña o la llave privada podrían ser capturadas mientras se encuentran en uso. Por ello, el sistema protege principalmente contra el robo de archivos almacenados, pero no contra un entorno ya comprometido.

Además, se asume que la librería criptográfica utilizada funciona correctamente y que los algoritmos implementados, como Argon2id y AES-GCM, se utilizan de forma adecuada. Finalmente, se considera que los respaldos del keystore se almacenan en ubicaciones seguras y que solo los usuarios autorizados tienen acceso a ellos.

## Security Discussion

### ¿Por qué cifrar las llaves privadas?

Ciframos las llaves privadas porque son el elemento principal que permite al usuario descifrar los archivos protegidos. Si una llave privada se almacenara en texto plano y un atacante lograra robarla, podría usarla para acceder a los archivos cifrados destinados a ese usuario.

En nuestro sistema, la llave privada no se guarda directamente. Primero se convierte a formato PEM y después se cifra con AES-GCM usando una clave derivada de la contraseña del usuario mediante Argon2id. De esta forma, aunque un atacante robe el keystore, no podrá usar la llave privada sin conocer la contraseña correcta. Por lo tanto, cifrar las llaves privadas reduce el riesgo de exposición ante robo de archivos, copias de seguridad comprometidas o acceso no autorizado al almacenamiento. 

### ¿Qué pasa si la contraseña es débil?

Si la contraseña es débil, el atacante podría intentar adivinarla mediante ataques de fuerza bruta o diccionario, especialmente si ya robó el keystore. Aunque el sistema usa Argon2id para hacer más costoso ese proceso, una contraseña corta, común o reutilizada sigue siendo vulnerable.

En ese caso, si el atacante logra descubrir la contraseña, podría derivar la misma clave de cifrado y descifrar la llave privada almacenada en el keystore. Por eso, la seguridad del sistema no depende sde la boveda, sino también de que el usuario utilice una contraseña fuerte y dificil de adivinar.

### ¿Cuáles son las limitaciones de nuestro sistema?

Las principales limitaciones de nuestro sistema son que no puede proteger completamente contra contraseñas débiles, dispositivos comprometidos o usuarios que compartan su contraseña o archivos descifrados. Aunque el keystore protege la llave privada, si un atacante obtiene la contraseña correcta, podría descifrar la llave privada.

El sistema tampoco protege contra malware, keyloggers o un atacante con control del sistema operativo, ya que podría capturar la contraseña mientras el usuario la escribe o acceder a la llave privada cuando está temporalmente descifrada en memoria.

Otra vulnerabilidad puede ser que al generar una nueva llave, no se conserva automáticamente un historial de llaves anteriores, por lo que archivos cifrados con llaves antiguas podrían requerir manejo adicional. Y finalmente, el sistema protege los archivos cifrados y el keystore, pero no puede evitar que un usuario autorizado comparta manualmente un archivo después de descifrarlo.

## Pruebas
Para la prueba de contraseña correcta e incorrecta ya se tenía una prueba automatizada en donde poníamos a prueba el acceso al sistema mediante el uso de credenciales válidas y no válidas. Primero se crea un usuario con una contraseña correcta, se cifra un archivo y posteriormente se intenta descifrarlo usando esa misma contraseña, comprobando que el acceso sea concedido y que el archivo recuperado coincida con el contenido original. Después, se realiza otro intento de descifrado utilizando una contraseña incorrecta, verificando que el sistema niegue el acceso, genere un error y no produzca ningún archivo de salida.

<img width="1393" height="111" alt="image" src="https://github.com/user-attachments/assets/dd7305f3-b114-4593-abcd-7aa886070bf5" />

### a) Correct password → access granted

Primero se creó un usuario y posteriormente se cifró un archivo utilizando sus llaves criptográficas. Después, se realizó el proceso de descifrado ingresando la contraseña correcta del usuario. El sistema logró cargar correctamente el keystore, derivar la clave mediante Argon2id y descifrar la llave privada protegida con AES-GCM. Una vez validada la autenticidad e integridad de los datos, el sistema permitió el descifrado del contenedor y generó exitosamente el archivo salida_correcta.txt, mostrando el mensaje Success.

<img width="1405" height="231" alt="image" src="https://github.com/user-attachments/assets/fcc79616-5e07-42ec-83d0-90bce68ae60b" />

### b) Wrong password → access denied

Para la prueba de contraseña incorrecta, se intentó descifrar un contenedor previamente cifrado utilizando una contraseña diferente a la registrada para el usuario. Durante el proceso, el sistema intentó cargar y descifrar el keystore del usuario, pero al derivarse una clave incorrecta a partir de la contraseña errónea, AES-GCM no pudo validar la autenticidad de los datos y se generó una excepción InvalidTag. Posteriormente, el sistema lanzó el error. Además, se verificó que el archivo de salida salida_wrong.txt no fuera creado, confirmando que el sistema bloqueó completamente el descifrado cuando se utilizó una contraseña inválida.

<img width="1420" height="521" alt="image" src="https://github.com/user-attachments/assets/6571b35e-918f-4839-8189-5141b776c79c" />


### c) Modified keystore → failure

Se modificó manualmente el archivo keystore.json, alterando uno de los parámetros almacenados dentro de los metadatos del KDF. Esta modificación simula un intento de manipulación no autorizada sobre el keystore protegido del usuario.

<img width="1365" height="120" alt="image" src="https://github.com/user-attachments/assets/84a39648-8bdc-4961-99b9-af5e9b85fe72" />

Después se intentó descifrar el contenedor utilizando la contraseña correcta del usuario. Durante la validación, AES-GCM detectó que los datos autenticados ya no coincidían y generó la excepción InvalidTag. Posteriormente, el sistema rechazó el acceso demostrando que cualquier alteración del keystore es detectada automáticamente.

<img width="1391" height="521" alt="image" src="https://github.com/user-attachments/assets/628f8b4f-6f5e-4df3-9222-60fbd53216be" />


### d) Backup → restore works

<img width="1406" height="65" alt="image" src="https://github.com/user-attachments/assets/c3833836-f7e3-4ef6-ac75-6431bbcab3fe" />

<img width="1052" height="196" alt="image" src="https://github.com/user-attachments/assets/c893e89b-66d6-450d-aec9-62a50e02a83a" />

<img width="1390" height="286" alt="image" src="https://github.com/user-attachments/assets/e274b2a0-482e-458d-a043-bef8e03a6562" />

<img width="978" height="192" alt="image" src="https://github.com/user-attachments/assets/64a61d01-6b75-42bf-b84b-6fae667cb871" />

<img width="1387" height="90" alt="image" src="https://github.com/user-attachments/assets/236c6262-cfaf-49d3-9ffb-ecb557e3487b" />

### e) Stolen keystore alone → cannot decrypt

## Referencias 

Authenticated encryption — Cryptography 49.0.0.dev1 documentation. (s. f.). https://cryptography.io/en/latest/hazmat/primitives/aead

Welcome to pyca/cryptography — Cryptography 49.0.0.dev1 documentation. (s. f.). https://cryptography.io/en/latest

Cybersecurity Framework | NIST. (2026, 8 mayo). NIST. https://www.nist.gov/cyberframework

Biryukov, A., Dinu, D., Khovratovich, D., & Josefsson, S. (2021, 1 septiembre). RFC 9106: Argon2 Memory-Hard Function for Password Hashing and Proof-of-Work Applications. https://www.rfc-editor.org/rfc/rfc9106.html

Barker, E. (Mayo, 2020). Recommendation for Key Management: Part 1 – General. NIST. https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final


