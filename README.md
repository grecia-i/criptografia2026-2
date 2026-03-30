# Bóveda Digital

Proyecto para la clase de Criptografía

El objetivo principal del sistema es proteger, compartir y verificar documentos digitales mediante técnicas criptográficas modernas. Debe permitir a los usuarios cifrar archivos, compartirlos de forma segura con destinatarios seleccionados, verificar su autenticidad y gestionar sus claves criptográficas de forma responsable.

Contribuyentes:

- Castillo Soto Jacqueline,
- Meneses Calderas Grecia Irais,
- Pérez Osorio Luis Eduardo,
- Rivas Gil María Lucía.

## Cifrado simétrico ( D2 )

El modulo de cifrado simétrico implementa un esquema AEAD (Authenticated Encryption with Associated Data) por medio de AES-GCM para cifrar archivos en un contenedor seguro ```\src\vault_container\```.

El reporte de este modulo está disponible en:

[SecureSymEncryptionModule](documentation/D2-SecureSymEncryptionModule/FileEncryptionModule.md)

## Cifrado híbrido ( D3 )

El modulo de cifrado híbrido implementa un mecanismo de cifrado de llave privada para el almacenamiento seguro de las llaves simétricas utilizadas por el modulo anterior, la llave simétrica es cifrada utilizando las llaves publicas de los receptores autorizados, estos receptores pueden entonces descifrar la llave simétrica utilizando su llave privada.

El reporte de este modulo está disponible en:

[Hybrid Encryption](documentation/D3%20-%20Hybrid%20Encryption/HybridEncryption.md)

Uso del programa:

### Creación de usuarios

``main.py create-user <usuario>``

En este punto del desarrollo de se ha implementado un mecanismo para transmitir llaves, todos los usuarios deben ser creados localmente.

### Cifrado de archivos

``main.py encrypt <ruta del archivo a cifrar> --to <Lista de usuarios>``

La lista de usuarios es una serie de nombres de usuario separada por espacios.

### Descifrado de archivos

``main.py decrypt --user <nombre> <ruta destino> <ruta objetivo>``

Ruta objetivo es el archivo a descifrar, ejemplo ``"\vault_container\test.txt"``

Ruta destino es la ruta donde se creara el archivo descifrado
