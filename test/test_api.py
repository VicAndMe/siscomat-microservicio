import pytest
from fastapi.testclient import TestClient
from app.main import app

# Inicializamos el cliente de pruebas de FastAPI
client = TestClient(app)

# Variables globales para las pruebas
HEADERS_VALIDOS = {"X-API-Key": "siscomat_token_seguro_2026"}
# Un PDF en blanco muy pequeño codificado en Base64 para no saturar el código
DUMMY_PDF_BASE64 = "JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0ZURlY29kZT4+CnN0cmVhbQp4nDPQM1Qo5ypUMFAwALJMLU31jBQsTAz1LBSKUrnCtRTyuVJFHEpTizLT0xWcE0tSihhAgAEAAH8IygplbmRzdHJlYW0KZW5kb2JqCgozIDAgb2JqCjQxCmVuZG9iagoKNCAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3ggWzAgMCA1OTUuMjggODQxLjg5XS9QYXJlbnQgNSAwIFIvUmVzb3VyY2VzPDwvUHJvY1NldFsvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJXT4+L0NvbnRlbnRzIDIgMCBSPj4KZW5kb2JqCgo1IDAgb2JqCjw8L1R5cGUvUGFnZXMvS2lkc1s0IDAgUl0vQ291bnQgMT4+CmVuZG9iagoKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgNSAwIFI+PgplbmRvYmoKCjYgMCBvYmoKPDwvUHJvZHVjZXIoQ2FudmEpL0NyZWF0aW9uRGF0ZShEOjIwMjExMTE1MTgyMzEzKzAwJzAwJyk+PgplbmRvYmoKCnhyZWYKMCA3CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDI3MyAwMDAwMCBuIAowMDAwMDAwMDIyIDAwMDAwIG4gCjAwMDAwMDAxMjIgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjE0IDAwMDAwIG4gCjAwMDAwMDAzMjAgMDAwMDAgbiAKdHJhaWxlcgo8PC9TaXplIDcvUm9vdCAxIDAgUi9JbmZvIDYgMCBSPj4Kc3RhcnR4cmVmCjQxMwolJUVPRgo="

def test_health_check():
    """Prueba que el servidor responda correctamente (E2E básico)."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"estado": "en linea", "servicio": "Generador de PDFs"}

def test_seguridad_api_key_faltante():
    """Prueba de Seguridad: Petición sin el header X-API-Key."""
    response = client.post("/api/v1/constancias/generar-individual", json={})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_generacion_individual_exito():
    """Prueba de Integración: Generación al vuelo exitosa."""
    payload = {
        "nombre_curso": "Pruebas de Software",
        "nombre_participante": "Víctor Andrés Horta Félix",
        "url_validacion": "https://siscomat.com/validar/TEST01",
        "plantilla_base64": DUMMY_PDF_BASE64
    }
    response = client.post("/api/v1/constancias/generar-individual", json=payload, headers=HEADERS_VALIDOS)
    
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "completado"
    assert "archivo_base64" in data
    assert len(data["archivo_base64"]) > 100 # Verificamos que realmente devolvió contenido

def test_generacion_lote_base64_invalido():
    """Prueba de Severidad Alta: Fallo al intentar decodificar un PDF corrupto."""
    payload = {
        "nombre_curso": "Semana de Matemáticas",
        "plantilla_base64": "ESTO_NO_ES_UN_BASE_64_VALIDO!@#",
        "participantes": []
    }
    response = client.post("/api/v1/constancias/generar-lote", json=payload, headers=HEADERS_VALIDOS)
    
    assert response.status_code == 400
    assert "Base64 inválido" in response.json()["detail"]

def test_generacion_lote_multi_status():
    """Prueba de Regla de Negocio: Código 207 y procesamiento iterativo correcto."""
    payload = {
        "nombre_curso": "Semana de Matemáticas",
        "plantilla_base64": DUMMY_PDF_BASE64,
        "participantes": [
            {
                "id_participante": 101,
                "nombre_completo": "Víctor Andrés Horta Félix",
                "url_validacion": "https://test.com/1"
            },
            {
                "id_participante": 102,
                "nombre_completo": "Ana Martínez",
                "url_validacion": "https://test.com/2"
            }
        ]
    }
    response = client.post("/api/v1/constancias/generar-lote", json=payload, headers=HEADERS_VALIDOS)
    
    assert response.status_code == 207 # Verificamos nuestro Multi-Status
    data = response.json()
    assert data["total_procesados"] == 2
    assert len(data["resultados"]) == 2
    
    # Verificamos que el mapeo de la base de datos sea íntegro
    assert data["resultados"][0]["id_participante"] == 101
    assert data["resultados"][0]["estado"] == "completado"
    assert "archivo_base64" in data["resultados"][0]