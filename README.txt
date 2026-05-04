# SISCOMAT - Microservicio de Generación de Constancias (PDF)

Este es un microservicio *stateless* (sin estado) construido con **Python y FastAPI**. Su principal responsabilidad es la gestión, validación y generación al vuelo de constancias académicas en formato PDF para el proyecto **SISCOMAT**.

El servicio procesa plantillas dinámicamente, asegurando que los textos se centren de manera automática y que el código QR de validación mantenga proporciones exactas.

## 🚀 Arquitectura y Funcionamiento

El microservicio utiliza un enfoque **"On-the-fly" (Generación al vuelo)** delegando el almacenamiento a la base de datos de .NET y operando netamente en memoria RAM:

1. **Gestión de Plantillas:** Permite al frontend validar si una plantilla PDF subida por el gestor contiene las etiquetas requeridas, y previsualizar cómo se verá el documento final.
2. **Procesamiento Inteligente:** Utilizando `PyMuPDF`, el motor escanea el PDF en memoria buscando tres cajas de texto (etiquetas):
   - `{{NOMBRE COMPLETO PARTICIPANTE}}`
   - `{{CURSO}}`
   - `{{QR}}`
3. **Estampado Dinámico:** Sustituye las etiquetas asegurando que el texto se alinee perfectamente al centro (horizontal y verticalmente) del espacio designado por el diseñador, y ajusta el código QR al tamaño requerido.

## 🛠️ Tecnologías Principales

*   **Framework:** FastAPI
*   **Motor PDF:** PyMuPDF (`fitz`)
*   **Generador QR:** `qrcode`
*   **Contenedores:** Docker & Docker Compose
*   **Pruebas Automáticas:** Pytest & HTTPX

## 🔒 Seguridad

Todos los *endpoints* están protegidos mediante validación de API Key. Las peticiones HTTP deben incluir el siguiente *header*:

*   **Header:** `X-API-Key`
*   **Valor:** `siscomat_token_seguro_2026` (Configurable por entorno).

---

## 📡 Endpoints Disponibles

La documentación interactiva completa (Swagger UI) está disponible en `http://localhost:8000/docs` una vez levantado el servidor.

### 1. Health Check
Verifica que el servicio y el contenedor estén en línea.
* **Ruta:** `GET /`
* **Respuesta Esperada:** `200 OK`

### 2. Validar Plantilla
Analiza un PDF Base64 para confirmar si cuenta con todos los *placeholders* (`{{NOMBRE COMPLETO PARTICIPANTE}}`, `{{CURSO}}`, `{{QR}}`) o si falta alguno.
* **Ruta:** `POST /api/v1/constancias/validar-plantilla`
* **Body (JSON):**
  ```json
  {
    "plantilla_base64": "JVBERi0xLjQKJcOkw7z..."
  }
  * Respuesta Esperada: 200 OK (Retorna un booleano indicando validez y listas de etiquetas encontradas/faltantes).
  
### 3. Previsualizar Constancia
Genera una prueba visual de la constancia utilizando un código QR ficticio ilustrativo. Ideal para que el gestor valide el diseño antes de guardarlo en el sistema.
* **Ruta: POST /api/v1/constancias/previsualizar
* **Body (JSON):**
  {
    "nombre_curso": "Nombre del Curso (Prueba)",
    "nombre_participante": "Participante de Prueba",
    "plantilla_base64": "JVBERi0xLjQKJcOkw7z..."
  }
 * Respuesta Esperada: 200 OK (Retorna el PDF previsualizado en Base64).

### 4. Generación Individual (Producción)
El endpoint principal utilizado por el sistema para generar la constancia final y real al vuelo cuando un usuario la solicita desde el portal público.
* **Ruta: POST /api/v1/constancias/generar-individual
* **Body (JSON):
  {
    "nombre_curso": "Introducción a R",
    "nombre_participante": "Víctor Andrés Horta Félix",
    "url_validacion": "[https://siscomat.com/validar/XYZ123](https://siscomat.com/validar/XYZ123)",
    "plantilla_base64": "JVBERi0xLjQKJcOkw7z..."
  }
  * Respuesta Esperada: 200 OK (Retorna el PDF final sellado en Base64).