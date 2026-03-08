# D2 - Secure Symmetric Encryption Module

## Encryption Design Section

- Selected AEAD algorithm
- Key size
- Nonce strategy
- Metadata authentication strategy

Para el módulo de encriptacion se escoge el algoritmo de cifrado de bloques AES-256-GCM que proporciona la biblioteca de cryptography, porque es un algoritmo estandarizado por parte del NIST y cuenta con optimización a nivel de hardware en CPUs modernos, y su modalidad con CGM le añade el modo contador (encriptación) y galois (autenticación) que cumple el requerimiento AAD.

Se utiliza de tamaño de llave 256 bits, el cual es el tamaño máximo aceptado de llave en el estándar, en su contraparte igualmente se utilizan llaves de 256 bits. 

Para el nonce, se genera un nonce pseudo-aleatorio de 96 bits para cada encriptación de archvio utilizando la biblioteca de secrets, la cual es un generador de números pseudo-aleatorios criptográficamente seguro y que utiliza recursos de hardware para su generación. [ESTRATEGIA DE DONDE SE GUARDO] , generar un nonce por cada encriptación evita enormemente que ocurra la repetición de nonce y mantiene las propiedades de integridad.

## Security Decisions

- Why AEAD instead of encryption + hash?
- What happens if nonce repeats?
- What attacker are you defending against?

Esta implementación busca proteger al sistema de un atacante que no posee la llave, pero que intenta manipular los datos o leerlos, como cambiar el texto cifrado, los metadatos, el nonce, o introducir datos maliciosos. 
