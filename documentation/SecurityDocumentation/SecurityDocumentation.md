# Security Documentation

Contribuyentes:

- Castillo Soto Jacqueline,
- Meneses Calderas Grecia Irais,
- Pérez Osorio Luis Eduardo,
- Rivas Gil María Lucía.

## Threat model summary

El sistema fue diseñado para proteger archivos digitales confidenciales mediante mecanismos de cifrado híbrido autenticado, firmas digitales y almacenamiento seguro de llaves criptográficas. El objetivo principal del sistema es preservar la confidencialidad, integridad, autenticidad y control de acceso sobre la información protegida.

### Activos protegidos
### Actores de amenaza
### Objetivos de seguridad

#### Confidencialidad
#### Integridad
#### Autenticidad
#### Control de acceso
#### Fail-Closed Behavior

### Amenazas consideradas
### Estrategias de mitigación
### Fuera del alcance

## Cryptographic design decisions

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



## Security audit findings
