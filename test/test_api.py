import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Configuración Segura: Leemos la variable inyectada por Docker (.env)
API_KEY = os.environ.get("API_KEY_SECRETA", "token_por_defecto_inseguro")
HEADERS_VALIDOS = {"X-API-Key": API_KEY}
HEADERS_INVALIDOS = {"X-API-Key": "HACKER_KEY_123"}

# Base64 simulado de un PDF mínimo para que FastAPI no falle al intentar decodificar
PDF_DUMMY_BASE64 = "JVBERi0xLjQKJcOkw7zDqwoxIDAgb2JqCjw8L0ZpbHRlci9GbGF0ZURlY29kZS9MZW5ndGggMTE0Pj5zdHJlYW0KeJzLzU/Pz0vMyczLLC7QcE/NTEbSAQkDAwNLQwWDiFADBwMFHQXXvDygVmaOIUjA0EChoCg/pzQnNa9EwT0zOaO4uCQzrwSsu6SkNCdFAT1zXQoKhA1NTKz0DQwNFRwSS1IyizPTM1P1DBUcdT3yS4tSMhJzE8HyAA+UK3UKZW5kc3RyZWFtCmVuZG9iagoyIDAgb2JqCjw8L1R5cGUvUGFnZXMvQ291bnQgMS9LaWRzWzMgMCBSXT4+CmVuZG9iagozIDAgb2JqCjw8L1R5cGUvUGFnZS9NZWRpYUJveFswIDAgNTk1IDg0Ml0vUGFyZW50IDIgMCBSL1Jlc291cmNlczw8L0ZvbnQ8PC9GMSA0IDAgUj4+Pj4vQ29udGVudHMgMSAwIFI+PgplbmRvYmoKNCAwIG9iago8PC9UeXBlL0ZvbnQvU3VidHlwZS9UeXBlMS9CYXNlRm9udC9IZWx2ZXRpY2E+PgplbmRvYmoKNSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKNiAwIG9iago8PC9DcmVhdG9yKFB5TXVQREYgMS4yNC4xMSkvUHJvZHVjZXIoUHlNdVBERiAxLjI0LjExKS9DcmVhdGlvbkRhdGUoRDoyMDI0MTAzMTE4MjU0NFopPj4KZW5kb2JqCnhyZWYKMCA3CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMjAyIDAwMDAwIG4gCjAwMDAwMDAyNTkgMDAwMDAgbiAKMDAwMDAwMDM3NCAwMDAwMCBuIAowMDAwMDAwNDYyIDAwMDAwIG4gCjAwMDAwMDA1MTEgMDAwMDAgbiAKdHJhaWxlcgo8PC9TaXplIDcvUm9vdCA1IDAgUi9JbmZvIDYgMCBSPj4Kc3RhcnR4cmVmCjYzOQolJUVPRgo="

def test_acceso_denegado_sin_token():
    """Valida que el sistema rechace peticiones sin API Key"""
    payload = {
        "nombre_curso": "Curso de Prueba",
        "nombre_participante": "Juan Pérez",
        "plantilla_base64": PDF_DUMMY_BASE64
    }
    response = client.post("/api/v1/constancias/previsualizar", json=payload)
    assert response.status_code == 403

def test_acceso_denegado_token_invalido():
    """Valida que el sistema rechace peticiones con una API Key incorrecta"""
    payload = {
        "nombre_curso": "Curso de Prueba",
        "nombre_participante": "Juan Pérez",
        "plantilla_base64": PDF_DUMMY_BASE64
    }
    response = client.post("/api/v1/constancias/previsualizar", json=payload, headers=HEADERS_INVALIDOS)
    assert response.status_code == 401

def test_limite_caracteres_maximo_permitido():
    """Valida que el sistema ACEPTE un nombre y curso justo en el límite de 152 caracteres"""
    texto_152_chars = "A" * 152
    payload = {
        "nombre_curso": texto_152_chars,
        "nombre_participante": texto_152_chars,
        "plantilla_base64": PDF_DUMMY_BASE64
    }
    response = client.post("/api/v1/constancias/previsualizar", json=payload, headers=HEADERS_VALIDOS)
    # Debería intentar procesarlo (200 OK)
    assert response.status_code == 200

def test_limite_caracteres_excedido_nombre():
    """Valida que el sistema RECHACE un nombre de 153 caracteres antes de procesarlo"""
    payload = {
        "nombre_curso": "Curso de Matemáticas",
        "nombre_participante": "A" * 153, # Supera por 1 el límite
        "plantilla_base64": PDF_DUMMY_BASE64
    }
    response = client.post("/api/v1/constancias/previsualizar", json=payload, headers=HEADERS_VALIDOS)
    # 422 Unprocessable Entity provisto por Pydantic
    assert response.status_code == 422
    assert "nombre_participante" in response.text

def test_limite_caracteres_excedido_curso():
    """Valida que el sistema RECHACE un curso de 153 caracteres antes de procesarlo"""
    payload = {
        "nombre_curso": "A" * 153, # Supera por 1 el límite
        "nombre_participante": "Víctor Andrés Horta",
        "plantilla_base64": PDF_DUMMY_BASE64
    }
    response = client.post("/api/v1/constancias/previsualizar", json=payload, headers=HEADERS_VALIDOS)
    assert response.status_code == 422
    assert "nombre_curso" in response.text

def test_generacion_individual_estructura_respuesta():
    """Valida que el endpoint de generación completa devuelva la estructura JSON correcta"""
    payload = {
        "nombre_curso": "Álgebra Lineal",
        "nombre_participante": "Ana Martínez",
        "url_validacion": "https://siscomat.com/validar/XYZ",
        "plantilla_base64": PDF_DUMMY_BASE64
    }
    response = client.post("/api/v1/constancias/generar", json=payload, headers=HEADERS_VALIDOS)
    assert response.status_code == 200
    
    json_response = response.json()
    # Verificar que los campos prometidos en schemas.py existan
    assert "estado" in json_response
    assert "mensaje" in json_response
    assert "archivo_base64" in json_response
    assert json_response["estado"] == "completado"