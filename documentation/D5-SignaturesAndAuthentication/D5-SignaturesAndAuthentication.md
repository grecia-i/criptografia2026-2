# Digital Signatures

Contribuyentes:

- Castillo Soto Jacqueline,
- Meneses Calderas Grecia Irais,
- Pérez Osorio Luis Eduardo,
- Rivas Gil María Lucía.

## Diseño de firmado

### ¿Por qué se utilizó RSA-PSS para las firmas digitales?

Se escogió este algoritmo más que nada por la estructura existente. Al haber realizado el par de llaves de cifrado con RSA, hubo una mayor compatibilidad al integrar las nuevas funcionalidades y con ese mismo par de llaves se realiza la firma digital, en lugar de tener más llaves a las que dar gestión para un sólo usuario. A estándares de hoy en día, no es un algoritmo eficiente y ocupa una mayor cantidad de espacio, pero lo consideramos apto. Se podría cambiar esto en futuras versiones.

### ¿Qué datos se firman?

Los datos que se firman después de cifrar son los metadatos junto con el texto cifrado, esto para garantizar la integridad de que estos mismos no han sido manipulados después de cifrarlos, nadie cambió el remitente, la hora en que se creó, etc. y se evita que el atacante reemplace el mensaje. Igualmente, sólo se firma el hash de estos datos puesto que es un proceso computacionalmente lento. Por último, se garantiza no repudio al colocar en los metadatos quien está cifrando el mensaje, para quiénes y con qué.

### ¿Por qué es necesario hacer hashing antes de firmar?

Es necesario aplicar una función hash antes de firmar porque la firma digital no se realiza directamente sobre el mensaje completo, sino sobre un resumen criptográfico de tamaño fijo (digest). Este resumen se obtiene mediante una función hash segura y posteriormente se firma con la llave privada del emisor. Este enfoque mejora la eficiencia del proceso, ya que permite firmar datos de cualquier tamaño de manera práctica, y garantiza la integridad de la información, debido a que cualquier modificación, incluso mínima, en los datos originales produce un cambio completamente distinto en el hash. En consecuencia, si el contenido es alterado, la verificación de la firma falla, permitiendo detectar manipulaciones de forma confiable.

## Consideraciones de seguridad

### ¿Por que se cifra el texto cifrado y no el texto en plano?
Se firma el texto cifrado porque es la versión que realmente se almacena y se comparte dentro del contenedor. Así, la firma protege exactamente lo que recibirá el destinatario: el archivo cifrado y sus metadatos. Si se firmara solo el texto plano, habría que descifrar primero para verificar la firma, lo cual podría obligar al sistema a procesar información no autenticada. En cambio, al firmar el texto cifrado, el receptor puede comprobar antes de aceptar el contenido que el contenedor no fue alterado y que proviene del emisor esperado. Además, este enfoque mantiene la confidencialidad, porque la firma no revela el contenido original del archivo.

### ¿Qué pasa si no se verifica la firma primero?
Si no se verifica la firma primero, el sistema podría procesar un archivo que no ha sido autenticado. Esto significa que podría intentar descifrar o aceptar un contenedor alterado, falso o creado por una persona no autorizada. Por lo que se pierde la garantía de origen e integridad: ya no se puede asegurar quién creó el archivo ni si el contenido o los metadatos fueron modificados. Además, manejar datos sin verificar puede provocar fallos, validaciones tardías o incluso vulnerabilidades, ya que el sistema estaría operando sobre información alterada antes de detectar el problema. Por ello, es fundamental comprobar la firma antes de confiar en cualquier contenido del contenedor.

### ¿Qué pasa si se excluyen los metadatos?

Si no se incluyen los metadatos en la firma, solo se está protegiendo el contenido cifrado, pero no la información que lo acompaña. Por ejemplo, podrían alterarse datos como el nombre del archivo, el tamaño, el algoritmo usado, el identificador del emisor, la lista de destinatarios o cualquier información de control sin invalidar la firma. Esto permitiría manipular el contexto del archivo aunque el ciphertext no cambie. Por eso es importante que los metadatos también estén protegidos: así, cualquier cambio en esa información hace que la verificación falle y el archivo sea rechazado.

## Pruebas
Para confirmar las pruebas se ejecutaron en consola y el resultado fue el esperado. Al igual que las pruebas se encuentran automatizadas en nuestro repositorio.
<img width="1107" height="261" alt="image" src="https://github.com/user-attachments/assets/9728e716-03d0-4eab-9799-fa820933541a" />

## Referencias

Dworkin, M. (2007). Recommendation for block cipher modes of operation : https://doi.org/10.6028/nist.sp.800-38d

The cryptographic doom principle. (2011, 13 diciembre). Moxie Marlinspike. https://moxie.org/2011/12/13/the-cryptographic-doom-principle.html

RFC 5116: An Interface and Algorithms for Authenticated Encryption. (s. f.). IETF Datatracker. https://datatracker.ietf.org/doc/html/rfc5116





