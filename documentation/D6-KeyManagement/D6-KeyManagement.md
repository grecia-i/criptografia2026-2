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

## Key Management Design

### Selección del KDF y sus parámetros
### Formato de almacenamiento de llaves
### Estrategia de respaldo
### Supuestos de seguridad

## Security Discussion

### ¿Por qué cifrar las llaves privadas?
### ¿Qué pasa si la contraseña es débil?
### ¿Cuáles son las limitaciones de nuestro sistema?

## Referencias 

Authenticated encryption — Cryptography 49.0.0.dev1 documentation. (s. f.). https://cryptography.io/en/latest/hazmat/primitives/aead

Welcome to pyca/cryptography — Cryptography 49.0.0.dev1 documentation. (s. f.). https://cryptography.io/en/latest

Cybersecurity Framework | NIST. (2026, 8 mayo). NIST. https://www.nist.gov/cyberframework

