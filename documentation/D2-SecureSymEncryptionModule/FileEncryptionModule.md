# D2 - Secure Symmetric Encryption Module

## Diseño del cifrado

- Selected AEAD algorithm
- Key size
- Nonce strategy
- Metadata authentication strategy

Para el módulo de cifrado se escogió el algoritmo de cifrado de bloques AES-256-GCM que proporciona la biblioteca de cryptography, porque es un algoritmo estandarizado por parte del NIST y cuenta con optimización a nivel de hardware en CPUs modernos, el modo de operación con GCM le añade el modo contador (cifrado) y galois (autenticación) que cumple el requerimiento AAD.

Se utiliza de tamaño de llave 256 bits, el cual es el tamaño máximo aceptado de llave en el estándar, en su contraparte igualmente se utilizan llaves de 256 bits.

Para el nonce, se genera un numero de 96 bits generado al azar, para cada archivo cifrado con el programa se genera un nonce único utilizando la biblioteca de secrets, la cual es un generador de números pseudo-aleatorios criptográficamente seguro y que utiliza recursos de hardware para su generación. cada archivo se almacena en directorio junto con los datos necesarios para descifrarlo , generar un nonce por cada archivo cifrado reduce enormemente el riesgo que ocurra la repetición de nonce y mantiene las propiedades de confidencialidad de la información.

Para la autentificación de metadatos se almacena junto al texto cifrado un header que contiene los metadatos del archivo, estos se utilizan para especificar información relevante del archivo y parámetros del descifrado tales como el tamaño de la llave, el algoritmo usado, el tamaño del nonce, etc, estos metadatos se adjuntan como información autenticada adicional (AAD) para garantizar la integridad y detectar modificaciones de los datos.

## Decisiones de seguridad

- ¿Por que utilizar AEAD en lugar de un esquema de cifrado + hash?

- ¿Qué sucede si se repite un nonce?

- ¿Contra qué tipo de atacante está protegiendo este esquema?

Esta implementación busca proteger al sistema de un atacante que no posee la llave, pero que intenta manipular los datos o leerlos, como cambiar el texto cifrado, los metadatos, el nonce, o introducir datos maliciosos.
