# Bóveda Digital

Proyecto para la clase de Criptografía

El objetivo principal del sistema es proteger, compartir y verificar documentos digitales mediante técnicas criptográficas modernas. Debe permitir a los usuarios cifrar archivos, compartirlos de forma segura con destinatarios seleccionados, verificar su autenticidad y gestionar sus claves criptográficas de forma responsable.

Contribuyentes:
- Castillo Soto Jacqueline, 
- Meneses Calderas Grecia Irais, 
- Pérez Osorio Luis Eduardo, 
- Rivas Gil María Lucía.

## Cifrado simetrico
El modulo de cifrado simétrico implementa un esquema AEAD (Authenticated Encryption with Associated Data) por medio de AES-GCM para cifrar archivos en un contenedor seguro ```\src\vault_container\```.

El sistema permite al usuario cifrar o descifrar un archivo por medio de la linea de comandos, su uso es el siguiente

```python main.py encrypt <archivo fuente>```

```python main.py decrypt <contenedor> <archivo destino>```

El reporte de este modulo está disponible en:

[SecureSymEncryptionModule](documentation/D2-SecureSymEncryptionModule/FileEncryptionModule.md)
