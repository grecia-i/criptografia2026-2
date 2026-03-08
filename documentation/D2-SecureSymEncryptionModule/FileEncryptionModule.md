# D2 - Secure Symmetric Encryption Module

## Diseño del cifrado

### Algoritmo de AEAD

Para el módulo de cifrado se escogió el algoritmo de cifrado de bloques AES-256-GCM que proporciona la biblioteca de cryptography, porque es un algoritmo estandarizado por parte del NIST y cuenta con optimización a nivel de hardware en CPUs modernos, el modo de operación con GCM le añade el modo contador (cifrado) y galois (autenticación) que cumple el requerimiento AAD.

Esta implementación genera una llave para cada archivo cifrado, esta llave de archivo se almacena cifrada en el contenedor del archivo correspondiente, en tiempo de ejecución se realiza un proceso de derivación de llaves a partir de una contraseña de usuario para descifrar las llaves de archivo y posteriormente el contenido de los archivos.

### Tamaño de llave

Para la implementación de AES-GCM se utiliza un tamaño de llave 256 bits, el cual es el tamaño máximo aceptado en el estándar, para la derivación de la llave maestra a partir de la contraseña de usuario se utilizó un algoritmo de hash SHA256 con una llave de 256 bits, estos tamaños se alinean con las recomendaciones del NIST para el cifrado simétrico.

### Estrategia de nonce

Para el nonce, se genera un numero de 96 bits generado al azar, para cada archivo cifrado con el programa se genera un nonce único utilizando la biblioteca secrets, la cual es un generador de números pseudoaleatorios criptográficamente seguro y que utiliza recursos de hardware para su generación. cada archivo se almacena en directorio junto con los datos necesarios para descifrarlo , generar un nonce por cada archivo cifrado reduce enormemente el riesgo que ocurra la repetición de nonce y mantiene las propiedades de confidencialidad de la información.

### Autentificación de metadatos

Para la autentificación de metadatos se almacena junto al texto cifrado un header que contiene los metadatos del archivo, estos se utilizan para especificar información relevante del archivo y parámetros del descifrado tales como el tamaño de la llave, el algoritmo usado, el tamaño del nonce, etc, estos metadatos se adjuntan como información autenticada adicional (AAD) para garantizar la integridad y detectar modificaciones de los datos.

## Decisiones de seguridad

- ¿Por qué utilizar AEAD en lugar de un esquema de cifrado + hash?

El uso de un sistema de cifrado autentificado con datos asociados (AEAD) proporciona un mecanismo de confidencialidad e integridad dentro del mismo proceso de cifrado, el algoritmo, en este caso AES-GCM, simultáneamente hace el cifrado del texto plano y genera una etiqueta de autentificación que se concatena al texto cifrado, el uso de esta etiqueta de autentificación permite garantizar la integridad del texto cifrado y de los metadatos asociados detectando cualquier modificación durante el proceso de descifrado.

Resulta más conveniente este sistema ya que a diferencia de un sistema de cifrado + hash simple es mucho menos susceptible a errores causados por una mala implementación además de reducir los problemas causados por metadatos faltantes mientras simultáneamente garantiza la integridad de estos metadatos. En general podemos decir que el uso de AEAD presenta una solución más robusta y estandarizada para el proceso de  autentificación y verificación de integridad de los datos.

- ¿Qué sucede si se repite un nonce?

Esto representa un fallo crítico para la seguridad del algoritmo AES-GCM, si se repite un nonce junto con una llave privada el flujo de bits generados por el algoritmo se repetirá, de esta manera un atacante podría aplicar una operación XOR a ambos textos cifrados para obtener una parte del texto original.

Además de esto la reutilización de un nonce y una llave privada permite a un atacante recuperar la llave de autentificación, comprometiendo la autentificación de toda la información cifrada con esa llave, de esta manera un atacante podría acceder a la información confidencial además de alterarla sin ser detectado.

- ¿Contra qué tipo de atacante está protegiendo este esquema?

El sistema está diseñado para proteger contra un atacante que puede acceder a y manipular los archivos cifrados almacenados en la bóveda, se considera que un atacante podría intentar leer y alterar el texto cifrado, alterar los metadatos o reemplazar partes del contenedor para burlar los mecanismos de autentificación, confidencialidad e integridad.

Esta implementación asume que el atacante tiene acceso a los archivos de documentos cifrados, pero no conoce la contraseña del usuario o la llave derivada de esta.
