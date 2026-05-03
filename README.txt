# SISCOMAT - Microservicio de Generación de Constancias (PDF)

Este es un microservicio *stateless* (sin estado) construido con **Python y FastAPI**. Su responsabilidad exclusiva es generar constancias académicas en formato PDF, estampando datos dinámicos y un código QR de validación sobre una plantilla proporcionada al vuelo.

Este componente forma parte de la arquitectura de microservicios del proyecto **SISCOMAT**, y está diseñado para ser consumido por el backend principal en **.NET**.

## 🚀 Arquitectura y Funcionamiento

El microservicio utiliza un enfoque **"On-the-fly" (Generación al vuelo)** para optimizar los recursos del servidor y evitar la saturación del disco duro:

1. **Recepción:** El backend en .NET envía una petición HTTP que incluye la plantilla base del PDF codificada en **Base64** y los datos de los participantes (Nombres, Curso, URL de validación).
2. **Procesamiento Inteligente:** Utilizando `PyMuPDF`, el microservicio lee el PDF directamente en la memoria RAM y escanea el documento buscando tres etiquetas específicas:
   - `{{NOMBRE COMPLETO PARTICIPANTE}}`
   - `{{CURSO}}`
   - `{{QR}}`
3. **Estampado:** Calcula las coordenadas exactas de las etiquetas, las oculta y estampa la información real, incluyendo un código QR generado dinámicamente.
4. **Retorno:** Devuelve el archivo PDF final codificado en Base64 para que el backend en .NET se encargue de guardarlo en la base de datos PostgreSQL.

## 🛠️ Tecnologías Principales

*   **Framework:** FastAPI
*   **Motor PDF:** PyMuPDF (`fitz`)
*   **Generador QR:** `qrcode`
*   **Contenedores:** Docker & Docker Compose
*   **Pruebas Automáticas:** Pytest & HTTPX

## 🔒 Seguridad

Todos los *endpoints* de generación están protegidos. Las peticiones deben incluir el siguiente *header* para ser autorizadas por el microservicio:

*   **Header:** `X-API-Key`
*   **Valor:** `siscomat_token_seguro_2026` (Configurable según el entorno).

---

## 📡 Endpoints Disponibles

La documentación interactiva completa de los esquemas y modelos (Swagger UI) está disponible en `http://localhost:8000/docs` una vez que el servidor está en ejecución.

### 1. Health Check
Verifica que el contenedor y el servicio estén funcionando.
* **Ruta:** `GET /`
* **Respuesta:** `200 OK`

### 2. Generación Individual (Al vuelo)
Ideal para cuando un usuario final hace clic en "Descargar Constancia" desde el portal público.
* **Ruta:** `POST /api/v1/constancias/generar-individual`
* **Body (JSON):**
  ```json
  {
    "nombre_curso": "Semana de Matemáticas",
    "nombre_participante": "Víctor Andrés Horta Félix",
    "url_validacion": "[https://siscomat.com/validar/XYZ123](https://siscomat.com/validar/XYZ123)",
    "plantilla_base64": "JVBERi0xLjQKJcOkw7z..."
  }