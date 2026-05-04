import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

HEADERS_VALIDOS = {"X-API-Key": "siscomat_token_seguro_2026"}
DUMMY_PDF_BASE64 = "JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0ZURlY29kZT4+CnN0cmVhbQp4nDPQM1Qo5ypUMFAwALJMLU31jBQsTAz1LBSKUrnCtRTyuVJFHEpTizLT0xWcE0tSihhAgAEAAH8IygplbmRzdHJlYW0KZW5kb2JqCgozIDAgb2JqCjQxCmVuZG9iagoKNCAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3ggWzAgMCA1OTUuMjggODQxLjg5XS9QYXJlbnQgNSAwIFIvUmVzb3VyY2VzPDwvUHJvY1NldFsvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJXT4+L0NvbnRlbnRzIDIgMCBSPj4KZW5kb2JqCgo1IDAgb2JqCjw8L1R5cGUvUGFnZXMvS2lkc1s0IDAgUl0vQ291bnQgMT4+CmVuZG9iagoKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgNSAwIFI+PgplbmRvYmoKCjYgMCBvYmoKPDwvUHJvZHVjZXIoQ2FudmEpL0NyZWF0aW9uRGF0ZShEOjIwMjExMTE1MTgyMzEzKzAwJzAwJyk+PgplbmRvYmoKCnhyZWYKMCA3CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDI3MyAwMDAwMCBuIAowMDAwMDAwMDIyIDAwMDAwIG4gCjAwMDAwMDAxMjIgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjE0IDAwMDAwIG4gCjAwMDAwMDAzMjAgMDAwMDAgbiAKdHJhaWxlcgo8PC9TaXplIDcvUm9vdCAxIDAgUi9JbmZvIDYgMCBSPj4Kc3RhcnR4cmVmCjQxMwolJUVPRgo="

def test_health_check():
    """Prueba que el servidor responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"estado": "en linea", "servicio": "Generador de PDFs"}

def test_seguridad_api_key_faltante():
    """Prueba de Seguridad: Petición sin el header X-API-Key."""
    response = client.post("/api/v1/constancias/generar-individual", json={})
    assert response.status_code == 401

def test_validar_plantilla_vacia():
    """Prueba el endpoint de validación con un PDF en blanco (debe detectar que faltan cosas)."""
    payload = {"plantilla_base64": DUMMY_PDF_BASE64}
    response = client.post("/api/v1/constancias/validar-plantilla", json=payload, headers=HEADERS_VALIDOS)
    
    assert response.status_code == 200
    data = response.json()
    assert data["es_valida"] is False
    assert len(data["placeholders_faltantes"]) == 3
    assert "{{NOMBRE COMPLETO PARTICIPANTE}}" in data["placeholders_faltantes"] # <-- Línea actualizada
    assert "{{CURSO}}" in data["placeholders_faltantes"]
    assert "{{QR}}" in data["placeholders_faltantes"]

def test_previsualizacion_exito():
    """Prueba el endpoint de previsualización."""
    payload = {
        "nombre_curso": "Curso de Prueba",
        "nombre_participante": "Participante de Prueba",
        "plantilla_base64": DUMMY_PDF_BASE64
    }
    response = client.post("/api/v1/constancias/previsualizar", json=payload, headers=HEADERS_VALIDOS)
    
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "completado"
    assert "archivo_base64" in data

def test_generacion_individual_exito():
    """Prueba que la generación individual (el contrato que ya funciona en producción) siga intacto."""
    payload = {
        "nombre_curso": "Introducción a R",
        "nombre_participante": "Víctor Andrés Horta Félix",
        "url_validacion": "https://siscomat.com/validar/TEST01",
        "plantilla_base64": DUMMY_PDF_BASE64
    }
    response = client.post("/api/v1/constancias/generar-individual", json=payload, headers=HEADERS_VALIDOS)
    
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "completado"
    assert "archivo_base64" in data