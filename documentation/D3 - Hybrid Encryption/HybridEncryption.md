# Hybrid Encryption

Contribuyentes:

- Castillo Soto Jacqueline,
- Meneses Calderas Grecia Irais,
- Pérez Osorio Luis Eduardo,
- Rivas Gil María Lucía.

## Explicación del diseño híbrido

### ¿Por qué se utiliza el cifrado híbrido?

El cifrado híbrido se utiliza porque combina la eficiencia del cifrado simétrico con la seguridad y flexibilidad del cifrado asimétrico.
El cifrado simétrico es el más adecuado para proteger archivos, ya que trabaja de forma rápida incluso con grandes volúmenes de datos. En cambio, el cifrado asimétrico no se usa para cifrar el archivo completo, sino únicamente una clave simétrica pequeña.
El sistema híbrido existe porque el cifrado simétrico y el asimétrico tienen cada una sus ventajas. El cifrado simétrico, como AES-GCM, es muy rápido y está pensado para proteger grandes volúmenes de datos; además, GCM es un modo AEAD, es decir, no solo cifra, también protege la integridad de los datos y de los metadatos asociados. En cambio, el cifrado asimétrico, no se usa para cifrar archivos enteros, sino para proteger mensajes pequeños.

El proceso funciona así:

- Se genera una clave simétrica nueva y aleatoria.
- Esa clave se usa para cifrar el archivo o mensaje.
- Luego, la clave simétrica se cifra con la clave pública del destinatario.
- El destinatario usa su clave privada para recuperar la clave simétrica.
- Finalmente, usa esa clave simétrica para descifrar el contenido original.

El resultado es que el archivo solo se cifra una vez, pero la clave que lo abre puede distribuirse de forma segura a varias personas. Si usáramos solo cifrado asimétrico, el sistema sería mucho más lento e ineficiente para archivos grandes. Si usáramos solo cifrado simétrico, se presentaría el problema de cómo compartir esa clave secreta con seguridad entre varios usuarios. El cifrado híbrido resuelve ambos problemas: usa la rapidez del cifrado simétrico para los datos y la facilidad del cifrado asimétrico para el intercambio de claves.

Por lo que el cifrado híbrido tiene ciertas ventajas: es eficiente al usar el cifrado simétrico, ya que es mucho más rápido para procesar archivos completos. Además maneja el intercambio seguro de claves, al usar la criptografía asimétrica permite proteger la clave simétrica sin necesidad de que ya exista un canal secreto previo. Y tiene un mejor control de acceso, porque solo quien posea la clave privada correcta puede recuperar la clave simétrica y, por tanto, abrir el archivo.

### ¿Por qué sigue siendo necesario el cifrado simétrico?

Sigue siendo necesario porque es el mecanismo que realmente permite proteger los datos de forma rápida, eficiente y escalable. Aunque existen sistemas híbridos que combinan cifrado simétrico y asimétrico, el componente simétrico no desaparece, porque es el que hace el trabajo pesado de cifrar el contenido real del archivo o de la comunicación.

El cifrado simétrico usa una misma clave para cifrar y descifrar, y justamente por eso su funcionamiento es mucho más simple y veloz que el del cifrado asimétrico. Además es especialmente adecuada para grandes volúmenes de datos, porque permite cifrar y descifrar rápidamente sin exigir tanta carga computacional. Y su velocidad y eficiencia hacen que siga siendo ampliamente usado en comunicaciones seguras, bases de datos, almacenamiento de archivos y protocolos de red.

Otro punto importante es que el cifrado simétrico no solo sigue vigente por rapidez, sino también por seguridad práctica. El sistema no solo cifra, sino que también protege la integridad del contenido mediante una etiqueta de autenticación, lo que lo vuelve todavía más útil en sistemas reales. Por lo tanto en el sistema híbrido combinan la seguridad del asimétrico con la velocidad del simétrico.

### ¿Por qué es necesario el cifrado de claves por destinatario?

Es necesario porque el archivo puede estar dirigido a varias personas autorizadas, pero no todas comparten la misma clave privada. En criptografía asimétrica, cada usuario tiene su propio par de claves: una pública y una privada. La clave pública puede compartirse, pero la privada solo la posee su dueño. Por eso, si varias personas puedan abrir el mismo archivo de forma segura, debes proteger la clave del archivo por separado para cada una, usando su clave pública correspondiente.

Por lo que, en la cuestión de una clave simétrica el archivo se cifra y esa clave simétrica debe llegar de forma segura a cada usuario autorizado. Y como cada usuario tiene una clave pública distinta, la forma correcta de hacerlo es crear una copia cifrada de la clave de archivo para cada destinatario. Las claves pueden ser simétricas o asimétricas, y que proteger las claves es fundamental porque si alguien obtiene la clave correcta, obtiene también acceso a los datos.

Si no cifras la clave por destinatario, se pueden presentar los siguiente problemas:

- No sería posible controlar con precisión quién puede acceder al archivo, ya que si todos los usuarios dependieran de una única copia de la clave o de un mismo mecanismo de protección, se perdería la asociación directa entre cada usuario y su clave protegida. En cambio, al cifrar la clave del archivo de manera individual para cada destinatario, se establece un vínculo específico entre el usuario y su correspondiente acceso, garantizando que únicamente los usuarios autorizados puedan recuperar la clave y, por lo tanto, descifrar el archivo.

- Evita compartir secretos entre destinatarios. En cifrado simétrico, usar una sola clave compartida entre varios usuarios puede ser problemático porque esa clave tendría que distribuirse por adelantado y, si se filtra, todos los datos protegidos con ella quedan comprometidos.

- En el cifrado simétrico se presenta problemas de escalabilidad cuando muchos usuarios necesitan claves compartidas, porque la administración de claves crece y se vuelve compleja. El cifrado híbrido resuelve esto: el archivo se cifra una sola vez con AES, y luego la clave de archivo se cifra una vez por cada destinatario con su clave pública. Así no hay que volver a cifrar todo el archivo para cada persona.

- Y permite identificar con precisión qué clave corresponde a qué usuario. Esto es importante no solo para funcionamiento, sino para seguridad. Si cada destinatario tiene su propia entrada en el contenedor, con su identificador y su clave cifrada, se evita confusión, intercambio de identidades o errores al descifrar. La gestión de acceso debe garantizar que solo usuarios autenticados y autorizados puedan usar las claves para cifrar y descifrar datos.

## Decisiones de seguridad

### ¿Cómo identifican los destinatarios su llave?

Cada usuario tiene un par de llaves asimétricas (una pública y una privada) estas son generadas al momento de crear su cuenta (uso de la función create_user() ). La llave pública se almacena en users/{username}/public.pem y la privada en users/{username}/private.pem, protegida con su contraseña.

Al cifrar un archivo, el sistema recorre la lista de destinatarios (args.to), carga la llave pública de cada uno y calcula su key_id con (uso de la función get_key_id(pub) ). Este identificador se almacena junto con la llave de archivo cifrada dentro del contenedor, asociando cada copia de la llave al destinatario correspondiente.

Al momento de descifrar, el sistema carga la llave pública del usuario que intenta acceder, calcula su key_id  (uso de la función get_key_id(public_key) ) y lo usa para buscar dentro del contenedor la copia de la llave de archivo que fue cifrada para ese usuario. Si encuentra una coincidencia, usa su llave privada para descifrarla y acceder al contenido, en caso de que no hay coincidencia, el sistema rechaza el acceso con el mensaje #" ERROR: You are not an authorized recipient."

### ¿Qué pasa si un atacante modifica la lista de destinatarios?

AES-256-GCM proporciona autenticación integrada mediante un tag de 16 bytes que verifica tanto la integridad como la autenticidad del contenido cifrado. Si se llega a realizar cualquier modificación al ciphertext o a los datos autenticados adicionales (AAD) se invalida este tag y hace que el descifrado falle con InvalidTag.

Sin embargo, si la lista de destinatarios o el mapeo de key_id a llave cifrada no está incluido como parte de los datos autenticados (AAD) en el esquema de cifrado, un atacante podría modificar esa estructura sin que la autenticación lo detecte, por consecuente el atacante podría eliminar destinatarios o agregar entradas falsas.

### ¿Qué pasa si la llave pública es incorrecta?

Si se usa una llave pública incorrecta al cifrar, se producen varios problemas; en primer lugar, la llave de archivo se cifrará con una llave pública que no corresponde a ningún usuario legítimo del sistema, esto significa que ningún usuario podrá descifrarla con su llave privada, ya que no habría coincidencias entre las llaves.

En segundo lugar, el key_id calculado a partir de la llave pública incorrecta no coincidirá con el key_id de ningún usuario registrado, por lo tanto, al intentar descifrar, el sistema no encontrará una entrada válida para el usuario y rechazará el acceso.

En tercer lugar, aunque el usuario verdadero intente descifrar con su llave privada correcta, la operación fallará criptográficamente porque la llave de archivo fue cifrada con una llave pública diferente, esto generará un error de autenticación como "ERROR: Incorrect password, could not decrypt key".

El resultado final es que el archivo cifrado queda inaccesible para todos, incluyendo el usuario que lo cifró originalmente, ya que no existe ninguna llave privada que corresponda a la llave pública incorrecta usada.

## Ejecución de pruebas

<img width="1242" height="337" alt="image" src="https://github.com/user-attachments/assets/5bc63133-5378-4c13-861b-ee4b3a33d6a1" />

## Referencias

- Chandan, S. (2025, 5 septiembre). ¿Qué es el cifrado simétrico? | Consultoría de cifrado. Encryption Consulting. <https://www.encryptionconsulting.com/es/education-center/what-is-symmetric-encryption/>

- Amazon Web Services. (s. f.). ¿Qué es la criptografía? Amazon Web Services, Inc. <https://aws.amazon.com/es/what-is/cryptography/>

- ¿Qué es la encriptación híbrida? - Términos y definiciones de ciberseguridad. (s. f.). <https://www.vpnunlimited.com/es/help/cybersecurity/hybrid-encryption?srsltid=AfmBOopCqt3fDttV13cSlURL-q0UdRuSkgyejIjlTcuPV6ptgruGqOyo>

- Dworkin, M. J. (2007). Recommendation for block cipher modes of operation : <https://doi.org/10.6028/nist.sp.800-38d>
Encriptación híbrida. (s. f.). Google For Developers. <https://developers.google.com/tink/hybrid?hl=es-419>

- Bengtsson, J. (2024, 7 noviembre). What is Symmetric Encryption? Nexus IN Groupe. <https://nexus.ingroupe.com/what-is-symmetric-encryption/>
