# Arquitectura y análisis de amenazas

## 1. Descripción del sistema

## 2. Arquitectura del sistema

## 3. Requerimientos de seguridad

### Confidencialidad 
La arquitectura del sistema de seguridad garantiza que en caso de que exista alguna vulneración a la bóveda, los respaldos o los canales de comunicación, un atacante no podrá comprometer la confidencialidad de la información; debido a que el contenido se protege mediante un cifrado donde el ver el contenido de los documentos dependerá de si se tiene la llave privada válida de alguno de los usuarios autorizados. 
Dentro del servidor no se almacena información en texto plano, ya que los archivos son cifrados mediante una llave simétrica antes de ser almacenados o compartidos. 


### Integridad, Autenticidad y No repudio
Al utilizar el cifrado AEAD el sistema permite la autenticación de la información y la integridad de la misma, cada mensaje cifrado tendrá un token de autenticación único que únicamente el emisor podrá generar haciendo uso de su llave privada. 
El uso de este tipo de cifrado permite que cualquier intento de manipulación externa en los datos cifrados sea detectado durante el proceso de descifrado ya que si el token de autenticación es diferente, el sistema rechazará la operación antes de procesar los datos, porque en caso de tener información maliciosa se podría comprometer todo el sistema.
En complemento, todos los documentos son firmados digitalmente, esto para validar el origen de cada uno y quien es el autor de los archivos, esto haciendo uso de la llave pública del emisor, asegurando el no repudio de la información, pues los usuarios no pueden negar la autoría ni el envío de los documentos que tengan registrados dentro del sistema, esto se refuerza con el uso de timestamp pues se registra el momento de la carga y el envío desde el origen.   
En la parte de los respaldos, sucede lo mismo, pues así se asegura que en caso de que se quiera realizar alguna alteración al almacenamiento esta sea identificada de forma previa, impidiendo que se recuperen archivos comprometidos que podrían poner en riesgo nuestro sistema.


### Disponibilidad 
Para que el sistema sea resiliente, se implementan los respaldos redundantes para la recuperación inmediata ante fallos críticos. Estos respaldos mantienen los mismos protocolos de cifrado AEAD y firmas digitales mencionadas en el punto de la integridad y autenticidad, al hacer uso de esto en caso de cualquier desastre la restauración no compromete a nuestro sistema pues se podrán retomar las operaciones sobre una base de datos integra y verificada.


La revocación de accesos en tiempo real ocurre cuando a un usuario se le retiran los privilegios de entrada y se le invalida la capacidad de interacción con las llaves de forma inmediata, si ocurre esto el usuario ya no podrá descifrar nuevos documentos ni intercambiar información dentro del canal. Esto se logra mediante la actualización de las listas y el cifrado de las llaves simétricas, generando que el acceso a la información esté actualizado con los permisos vigentes y logrando que se evite la fuga de datos por credenciales obsoletas o revocadas.

### Manejo de llaves
Las llaves privadas cuentan con una vigencia definida de manera explícita, esto para poder forzar la rotación cada cierto tiempo y así reducir riesgos, además así se asegura que no se almacenen en texto plano para mantener su confidencialidad. Esto sucede usando generadores de números pseudoaleatorios criptográficamente seguros (CSPRNG), los cuales proporcionan la entropía necesaria para que las llaves no sean predecibles, 
Finalmente una vez que el usuario termine su relación con el servicio, las llaves que sean asociadas a su identidad son eliminadas de forma segura garantizando que no existan rastros de acceso que puedan comprometer su información a futuro.


### Protección contra la manipulación
Se implementan mecanismos de verificación de integridad de metadatos, diseñados para detectar alteraciones no autorizadas en el flujo de la información, esto haciendo uso de los esquemas de autenticación y las firmas digitales, el sistema identifica si los datos han sido manipulados para después rechazar o marcar el contenido como alterado para avisar a los administradores del sistema. Esto impide que un atacante realice cambios en los datos del destinatario o los parámetros de una llave con el fin de redirigir el acceso a un tercero. Si llegara a haber algún intento de suplantación o reenvío malicioso se rompería la cadena de confianza y validez de los tokens de autenticación, resultando en un bloqueo del acceso antes de que la información se vea comprometida.


## 4. Modelo de amenaza

**Versión de Aplicación:** 0.3

**Descripción:** La bóveda digital es provee a de un lugar donde almacenar y compartir sus documentos personales. Como esta es la primera implementación del servicio, la funcionalidad será limitada. Se tienen en cuenta los siguientes tipos de usuario:

- Administrador del sistema
- Usuario Propietario 
- Usuario Receptor

Los usuarios serán capaces de ingresar y encontrar sus documentos, subir nuevos, así como mandar y recibir documentos de otros usuarios.  

### Activos
Se consideran los siguientes activos: 

| ID | Nombre |
|----|--------|
| A-1 | Archivos digitales | 
| A-2 | Llaves privadas |
| A-3 | Llaves públicas |
| A-4 | Respaldo de documentos |
| A-5 | Respaldo de llaves |
| A-6 | Metadatos |
| A-7 | Logs de auditoría |
| A-8 | Cuentas del usuario |
| A-9 | Permisos |


### Modelo STRIDE.
El acrónimo STRIDE desglosado significa, (S) Suplantación de identidad, (T) Manipulación, (R) Repudio, (I) Divulgación de información, (D) Denegación de servicio, (E) Elevación de privilegios.

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