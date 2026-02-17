# Arquitectura y análisis de amenazas

## 1. Descripción del sistema

## 2. Arquitectura del sistema

## 3. Requerimientos de seguridad



## 4. Modelo de amenaza

Versión de Aplicación: 1.0

Descripción: La bóveda digital es provee a de un lugar donde almacenar y compartir sus documentos personales. Como esta es la primera implementación del servicio, la funcionalidad será limitada. Se tienen en cuenta los siguientes tipos de usuario:

- Administrador del sistema
- Usuario Propietario 
- Usuario Receptor

El usuario y administrador serán capaces de ingresar y encontrar sus documentos, subir nuevos, y recibir documentos de otros usuarios.  

### Activos
Se consideran los siguientes activos: 

| ID | Nombre | Descripción | Nivel de Confianza |
|----|--------|-------------|--------------------|
| A-1 | Archivos digitales | Los documentos
| A-2 | Llaves privadas |
| A-3 | Llaves públicas |
| A-4 | Respaldo de documentos |
| A-5 | Respaldo de llaves |
| A-6 | Metadatos |
| A-7 | Logs de auditoría |
| A-8 | Cuentas del usuario |
| A-9 | Permisos |


### Modelo STRIDE.
(S) Suplantación de identidad, (T) Manipulación, (R) Repudio, (I) Divulgación de información, (D) Denegación de servicio, (E) Elevación de privilegios 

| ID |  Amenaza  | Definición | Mitigación |
|----|-----------|------------|------------|
| T-1 | S | El atacante usurpa la identidad de un usuario registrado para poder acceder al sistema. | Autenticación de dos factores, la contraseña en texto plano nunca es recibida por el servidor, terminar la sesión cuando se excede cierto tiempo. |
| T-2 | S | El atacante cambia la llave pública del usuario. | Integridad en llaves públicas haciendo que estén firmadas por el servidor, logs. |
| T-3 | T | El atacante modifica el documento almacenado o cuando está en el canal siendo transmitido | Encriptación AEAD para detectar cualquier cambio, logs. |
| T-4 | T | Substitución de la clave cifrada por otra de autoría del atacante. | Firma digital utilizando la clave privada del emisor antes de la transmisión. |
| T-5 | T | Modificación no autorizada en el respaldo de llaves | Hash criptográfico, AEAD, verificación antes de restauración si se requiere. |
| T-6 | R | El usuario emisor denega haber compartido un documento | Firma digital con timestamp para logs. | 
| T-7 | R | Se eliminan logs | Logs firmados digitalmente. |
| T-8 | I | Acceso no autorizado a los documentos almacenados | Cifrado con esquema híbrido, las claves privadas se cifran en el cliente. |
| T-9 | I | El atacante roba el respaldo de la clave privada | Utilizar un generador pseudo-aleatorio con una entropía decente, o alta utilizando la guía SP 800-90B del NIST. |
| T-10 | D | Se bloquea el acceso a los documentos almacenados | Implementar redundancia. |
| T-11 | D | Se bloquea la función de restauración de llaves | Al restaurar se intenta descifrar usando cifrado simétrico, y se verifica la integridad de la llave restaurada descifrando  el respaldo. |
| T-12 | E | El atacante modifica el id de un documento para acceder a los de otros usuarios. | Verificar que el usuario autenticado esté permitido el acceso al documento. |
| T-13 | E | El atacante modifica tokens y cambia el rol del usuario | Firmar los tokens. |

## 5. Suposiciones de confianza

## 6. Análisis de superficie de ataque

## 7. Restricciones de diseño