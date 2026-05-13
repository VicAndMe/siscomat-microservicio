# SISCOMAT - MICROSERVICIO CONSTANCIAS

## REQUISITOS PARA PRUEBAS LOCALES
- Instalar [Docker](https://www.docker.com/products/docker-desktop/)

## Para ejecutar todo el proyecto con Docker
### Paso 1: Crear red compartida
El microservicio necesita comunicarse con el backend. Ejecuta este comando en tu terminal para crear la red compartida (solo es necesario hacerlo una vez):
```bash
docker network create siscomat_network
```

### Paso 2: Levantar el microservicio
```bash
docker compose up -d --build
```

### Paso 3: Entrar a las interfaces
Una vez que el contenedor esté corriendo, puedes acceder a la documentación interactiva y estado del microservicio en:

http://localhost:8000/docs para Swagger UI (Contratos de la API)

http://localhost:8000/ para el Health Check

## Ejecución de Pruebas (Testing Automático)
El microservicio cuenta con una suite de pruebas en pytest para validar los límites de caracteres, la seguridad y el motor PDF.

Para ejecutar las pruebas mientras el contenedor está en ejecución (en modo detached), corre el siguiente comando en tu terminal:

```Bash
docker exec -it siscomat-pdf python -m pytest -v
```
## Ejecución de Pruebas Manuales (desde http://localhost:8000/docs)

### Paso 1: Acceder a la Interfaz
1. Asegúrate de que el contenedor de Docker esté en ejecución (`docker compose up -d`).
2. Abre tu navegador web y dirígete a: [http://localhost:8000/docs](http://localhost:8000/docs)

### Paso 2: Autenticación (API Key)
Por seguridad, los *endpoints* están protegidos.
1. [cite_start]Haz clic en el botón verde **"Authorize"** (con un ícono de candado) en la parte superior derecha de la pantalla.
2. [cite_start]En el campo emergente, ingresa el token de seguridad configurado en el archivo `.env`.
3. Haz clic en **"Authorize"** y luego cierra esa ventana.

### Paso 3: Preparar la Petición
1. Despliega el *endpoint* que deseas probar (por ejemplo, `POST /api/v1/constancias/previsualizar`).
2. [cite_start]Haz clic en el botón **"Try it out"** (Pruébalo) en la esquina superior derecha del bloque.
3. Se habilitará una caja de texto con un JSON de ejemplo. Modifícalo con tus datos de prueba. 
   *(Nota: Necesitarás convertir un archivo PDF real a Base64 utilizando alguna herramienta web gratuita para llenar el campo `plantilla_base64`)*.

```json
{
  "nombre_curso": "[ESCRIBE AQUÍ EL NOMBRE DEL CURSO]",
  "nombre_participante": "[ESCRIBE AQUÍ UN NOMBRE DEL PARTICIPANTE]",
  "plantilla_base64": " [ESCRIBE AQUÍ EL CODIGO BASE64]"
}
```
### Paso 4: Ejecutar y Validar
1. Presiona el botón azul gigante "Execute".

2. Desplázate hacia abajo hasta la sección "Server response".

3. Verifica que en la columna "Code" aparezca un código 200.

4. En el "Response body", copia la cadena de texto gigante que te devolvió el servidor en el campo archivo_base64.

### Paso 5: Visualizar el PDF
1. Busca en Google una herramienta como "Base64 to PDF".

2. Pega la cadena decodificada y descarga tu documento. Podrás ver el PDF con los textos centrados y el código QR generado.