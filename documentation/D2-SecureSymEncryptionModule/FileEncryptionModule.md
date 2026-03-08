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


## Pruebas de Seguridad

1. Prueba de autenticación

El programa desarrollado solicita una contraseña para cifrar el archivo y posteriormente requiere la misma contraseña para realizar el descifrado del archivo ya cifrado.

Para esta prueba se eligió una contraseña específica durante el proceso de cifrado. Sin embargo, al intentar descifrar el archivo se ingresó una contraseña diferente.

Como resultado, el sistema generó un bloqueo. Esto ocurrió porque, al intentar descifrar el archivo utilizando una clave incorrecta, el algoritmo AES-GCM detectó que los datos no eran auténticos.

Esto sucede porque, al usar una clave incorrecta, el código de autenticación resultante (TAG) no coincide con el TAG esperado, lo que indica que la autenticación del mensaje ha fallado y evita que se genere cualquier salida de texto plano.
<img width="1241" height="218" alt="Screenshot From 2026-03-07 23-04-02" src="https://github.com/user-attachments/assets/d835378f-c087-4d95-9a44-67cf6cf1bbc1" />



2. Prueba de inyección de errores

Para esta prueba se realizó la inyección de bits basura en un archivo cifrado. En este caso, el archivo hola.txt contenía información sensible: "Información súper secreta".

Después de cifrarlo correctamente, se utilizó el comando dd para sobrescribir el offset 10 del archivo ciphertext con el valor hexadecimal \xff.

Una vez realizada esta modificación, al intentar ejecutar el proceso de descifrado se generó una excepción de tipo cryptography.exceptions.InvalidTag. Esto significa que, durante el descifrado, el algoritmo recalculó el código de autenticación y detectó que no coincidía con el TAG original almacenado al final del archivo.


Como resultado, el sistema detuvo el proceso de descifrado de manera inmediata, antes de producir cualquier salida de texto plano. Esto confirma que el mecanismo de autenticación e integridad del cifrado detecta correctamente modificaciones maliciosas en el archivo cifrado.
<img width="1514" height="353" alt="Screenshot From 2026-03-07 23-02-36" src="https://github.com/user-attachments/assets/c822ba19-7bbe-40b9-840a-d235b5dc6e7a" />



3. Prueba de modificación de metadatos

En esta prueba se realizaron cambios en el archivo header.json. Este archivo contiene la información de los metadatos del archivo cifrado. La modificación se efectuó antes de intentar el proceso de descifrado.

Durante el descifrado, el algoritmo utiliza el contenido del archivo JSON como datos asociados para verificar el TAG de autenticación. Sin embargo, debido a que el archivo header.json ya no es idéntico al que existía en el momento del cifrado, el cálculo del TAG no coincide con el valor original.

Como consecuencia, la librería detecta que los datos asociados han sido modificados. Esto impide que el proceso de descifrado continúe y protege la integridad de la información.
<img width="1208" height="237" alt="Screenshot From 2026-03-07 23-08-04" src="https://github.com/user-attachments/assets/9e3ccdbf-84c1-491a-8888-9446e6619128" />



4. Prueba de consistencia del cifrado y descifrado

Esta prueba tiene como objetivo verificar que no se pierda ni se modifique información durante los procesos de cifrado y descifrado. Se espera que el contenido del archivo original sea exactamente el mismo que el obtenido después de descifrar el archivo previamente cifrado.

Para realizar la prueba se utilizó el archivo Ciframe.txt, cuyo contenido era "HOLA DESCÍFRAME". Posteriormente, se cifró el archivo y luego se realizó el proceso de descifrado. El resultado del descifrado se guardó en un archivo llamado salida.txt.

Al revisar el contenido del archivo salida.txt, se observó que la información coincide completamente con el contenido original, lo que confirma que el proceso de cifrado y descifrado no produjo modificaciones ni pérdida de datos.
<img width="1221" height="533" alt="image" src="https://github.com/user-attachments/assets/f0ac9d25-5eb6-4819-b147-b826a8c06bd0" />

5. Prueba de Cifrados diferentes

Aunque se cifre el mismo archivo 100 veces, no debería generarse la misma salida de cifrado en cada ocasión. Esto se debe al uso de un nonce, que modifica el estado inicial del algoritmo y garantiza que el texto cifrado resultante sea diferente en cada ejecución.

De esta manera se evita la aparición de patrones en los datos cifrados, lo que fortalece la seguridad del sistema. Además, los algoritmos criptográficos modernos presentan el llamado efecto avalancha, lo que significa que si se modifica incluso un solo bit en la entrada, más de la mitad de los bits del resultado final cambian, produciendo un cifrado completamente distinto.

<img width="1085" height="737" alt="image" src="https://github.com/user-attachments/assets/eae02b86-46fb-4cb2-8c72-1f7a9a033457" />

