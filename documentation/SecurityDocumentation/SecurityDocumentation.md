# Security Documentation

Contribuyentes:

- Castillo Soto Jacqueline,
- Meneses Calderas Grecia Irais,
- Pérez Osorio Luis Eduardo,
- Rivas Gil María Lucía.

## Threat model summary

El sistema fue diseñado para proteger archivos digitales confidenciales mediante mecanismos de cifrado híbrido autenticado, firmas digitales y almacenamiento seguro de llaves criptográficas. El objetivo principal del sistema es preservar la confidencialidad, integridad, autenticidad y control de acceso sobre la información protegida.

### Activos protegidos

El sistema protege los siguientes activos:

- Archivos digitales cifrados almacenados dentro de los contenedores de la bóveda.
- Llaves privadas RSA pertenecientes a usuarios registrados.
- Llaves de sesión utilizadas durante el cifrado híbrido.
- Metadata asociada al contenedor cifrado.
- Firmas digitales utilizadas para verificar autenticidad.
. Respaldos de keystores.
  
### Actores de amenaza

El modelo de amenazas considera atacantes con capacidad para:

- Obtener acceso a contenedores cifrados.
- Modificar archivos dentro del vault container.
- Alterar metadatos o listas de destinatarios.
- Modificar nonces o firmas digitales.
- Intentar descifrar contenedores sin autorización.
- Robar archivos keystore.json.
- Realizar ataques de fuerza bruta sobre contraseñas.

También se considera que un atacante podría tener acceso al sistema de archivos donde se almacenan los contenedores cifrados, sin poseer inicialmente la contraseña ni la llave privada del usuario legítimo.

### Objetivos de seguridad

#### Confidencialidad

Solo los usuarios autorizados deben poder recuperar el contenido original de los archivos cifrados.

#### Integridad

Cualquier modificación al ciphertext, metadata, nonce, lista de destinatarios o firmas digitales debe ser detectada antes del descifrado.

#### Autenticidad

El receptor debe poder verificar la identidad del emisor mediante firmas digitales.

#### Control de acceso

Únicamente los usuarios autorizados pueden descifrar el contenedor.

#### Fail-Closed Behavior

 Ante cualquier evidencia de manipulación o error de validación, el sistema debe detener la operación sin exponer información sensible.

### Amenazas consideradas

Las principales amenazas consideradas durante el diseño del sistema fueron:

- Manipulación de metadata.
- Alteración de recipient lists.
- Modificación de nonces.
- Eliminación o modificación de firmas digitales.
- Sustitución de identificadores de llaves públicas.
- Robo de keystores.
- Fuerza bruta sobre contraseñas.
- Filtración de información mediante mensajes de error.
- Procesamiento de contenedores alterados.

### Estrategias de mitigación

Para reducir estas amenazas, el sistema implementa:

- Cifrado autenticado AES-256-GCM.
- Firmas digitales RSA-PSS.
- Cifrado híbrido mediante RSA-OAEP.
- Canonicalización determinística de metadata.
- Verificación de firma antes del descifrado.
- Protección de metadata mediante AAD.
- Protección de llaves privadas con Argon2id y AES-GCM.
- Validaciones fail-closed.
- Uso de mensajes de error genéricos.
- Rotación y revocación de llaves.

### Fuera del alcance

Los siguientes escenarios se consideran fuera del alcance del proyecto:

- Compromiso total del sistema operativo.
- Malware ejecutándose con privilegios del usuario.
- Ataques físicos al hardware.
- Infraestructura multifactor.
Sincronización segura en la nube.


## Cryptographic design decisions

Las decisiones criptográficas fueron tomadas buscando mantener confidencialidad, integridad, autenticidad y compatibilidad entre componentes.

- El contenido de los archivos se cifra utilizando AES-256-GCM. Este algoritmo fue seleccionado debido a que proporciona cifrado autenticado (AEAD), permitiendo proteger simultáneamente la confidencialidad e integridad del contenido.
- AES-GCM permite además autenticar datos adicionales sin cifrarlos directamente mediante el uso de AAD (Additional Authenticated Data). Esto resulta útil para proteger metadata crítica del contenedor.
- Para cada archivo se genera una llave única y aleatoria de 256 bits para evitar reutilizar la misma llave en diferentes contenedores.
- Uso de nonces aleatorios
- El nonce también se protege dentro de los datos autenticados y de la firma digital, permitiendo detectar cualquier modificación antes de descifrar el archivo.

## Firmas digitales mediante RSA-PSS

Las firmas digitales se implementan mediante RSA-PSS con SHA-256.
La firma se calcula sobre:

- Metadata canonicalizada.
- Nonce.
- Ciphertext.

La verificación ocurre antes del descifrado, permitiendo detectar contenedores alterados antes de procesar información sensible.

## Uso de SHA-256

SHA-256 se utiliza como función hash principal dentro del sistema para:

- RSA-OAEP.
- RSA-PSS.
- Generación de identificadores de llaves públicas.

## Formato de serialización

Las llaves privadas no se almacenan en texto plano. Cada llave privada se serializa y posteriormente se protege dentro de un archivo keystore.json.

La llave de cifrado del keystore se deriva a partir de la contraseña del usuario utilizando Argon2id, seleccionado debido a su resistencia frente a ataques de fuerza bruta y ataques acelerados por GPU.

Posteriormente, la llave privada se cifra utilizando AES-GCM.

## Modelo fail-closed

El sistema implementa un modelo fail-closed. Ante cualquier error de validación, autenticación o integridad, el proceso se detiene y no se entrega el archivo original.



## Canonicalization strategy

La estrategia propuesta consiste en canonicalizar los metadatos antes de firmarlos, al igual que el archivo keystore antes de implementar AAD usando una representación JSON estable. Para ello, se ordenan las claves alfabéticamente, se eliminan espacios innecesarios, se utiliza una codificación fija en UTF-8, el carácter pasa directamente de unicode a UTF-8 y no se permiten valores no estándar. De esta forma, metadatos equivalentes generan siempre la misma secuencia de bytes, evitando que cambios de formato, espacios u orden de claves produzcan hashes distintos y rompan la verificación de la firma. Cuando se hace la escritura de algún archivo .json, se especifica que la codificación sea UTF-8.s.

De manera específica, la canonicalización se realiza de la forma:

1. **Ordenación de Claves (sort_keys=True):**
En muchos lenguajes, los diccionarios no mantienen un orden garantizado. Al forzar la ordenación lexicográfica, eliminamos la variabilidad producida por el orden de inserción, asegurando que el JSON sea idéntico siempre.
2. **Compactación Estricta (separators=(',', ':')):**
Por defecto, el serializador de JSON suele añadir espacios después de las comas y los dos puntos para mejorar la legibilidad. Al definir separadores compactos, eliminamos cualquier "ruido" de espacios en blanco, produciendo la representación binaria más densa y predecible posible.
3. **Codificación Determinística (.encode('UTF-8')):**
A diferencia de otros encodings, UTF-8 es un estándar universal donde cada carácter se mapea a una secuencia de bytes específica y constante, independientemente de la plataforma o el sistema operativo del emisor o receptor.
4. **Representación Unicode Determinística (ensure_ascii=False):**
Los caracteres Unicode se escriben directamente en UTF-8, evitando representaciones alternativas y garantizando una serialización consistente y determinística entre distintas implementaciones.
5. **Implementación del estándar JSON (allow_nan=False):**
La serialización falla inmediatamente si existen valores no válidos para JSON, como valores especiales de punto flotante, forzando una representación estándar. Esto evita ambigüedades y garantiza que cualquier JSON generado pueda ser interpretado de manera determinística por sistemas compatibles con el estándar.
6. **Normalización de Campos del Sistema:**
Para evitar ambigüedades, los datos complejos se pre-procesan antes de la serialización:
Listas: La lista de recipients se ordena alfabéticamente.
Fechas: Se utiliza estrictamente el formato ISO 8601 (UTC), evitando variaciones por zonas horarias locales.

La estructura header en encrypt.py y keystore en keystore.py define la organización de los datos. En esta se define un orden fijo para los metadatos y se asegura que todos los campos sean llenados por el sistema, en el caso de la lista de destinatarios se ordena previamente con los métodos internos de python.

#### Estructura header_bytes:

| Campo | Valor |
|-------|-------|         
| algorithm | Algoritmo de cifrado simétrico (ej. AES-256-GCM) |
| key_encryption | Algoritmo de cifrado de clave (RSA-OAEP) |
| signing_algorithm | Algoritmo de firma (RSA-PSS) |
| nonce_size | Tamaño del nonce en bits | 
| sender_id | Identificador del emisor | 
| recipients | Lista de destinatarios (ordenada previamente) |
| file_name | Nombre del archivo original |
| file_size | Tamaño del archivo en bytes |
| key_length | Longitud de la clave | 
| time_creation | Timestamp ISO 8601 con zona horaria |

#### Estructura keystore:
| Campo | Valor |
|-------|-------|
| version | Número de versión del formato de la keystore |
| kdf | Algoritmo de KDF (Derivación de llaves) |
| kdf_parameters.iterations | Iteraciones del algoritmo |
| kdf_parameters.lanes | Número de hilos para paralelización |
| kdf_parameters.memory_cost | Memoria reservada para el procesamiento del algoritmo |
| kdf_parameters.length | Longitud de la llave derivada |
| salt | Valor de entrada aleatorio único del algoritmo |
| nonce | Número único utilizado con el que la misma clave produce resultados diferentes |
| encrypted_key | Llave privada cifrada |
| public_key_id | Identificador del usuario asociado a la llave pública |
| created_at | Fecha y hora de creación de keystore |
| status | Estado de la llave: activada o retirada |

### Ejemplo de implementación para el manejo de llaves:

```
with open(keystore_path, "w", encoding="utf-8") as f:
        json.dump(keystore, f, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
```

## Key management strategy

Se implementó un ciclo de vida para las llaves asimétricas utilizadas para compartir archivos, en conjunto a esto se implemento una serie de mecanismos para administrar de manera segura la generación y almacenamiento de las llaves privadas en un contenedor seguro mediante el uso de una función de derivación de llave (KDF).

El desglose está disponible en:

[Key Management](../D6-KeyManagement/D6-KeyManagement.md)

## Security audit findings
