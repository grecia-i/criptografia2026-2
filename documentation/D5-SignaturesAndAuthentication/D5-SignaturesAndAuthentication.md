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

## Consideraciones de seguridad

### ¿Por que se cifra el texto cifrado y no el texto en plano?

### ¿Qué pasa si no se verifica la firma primero?

### ¿Qué pasa si se excluyen los metadatos?

## Pruebas
