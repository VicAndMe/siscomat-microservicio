from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.schemas import (
    PeticionGeneracionIndividual, RespuestaIndividual,
    PeticionPrevisualizacion, 
    PeticionValidacionPlantilla, RespuestaValidacionPlantilla
)
from app.services.pdf_generator import procesar_pdf, validar_plantilla
import base64

app = FastAPI(
    title="SISCOMAT - API de Generación de Constancias (PDF)",
    version="2.0.0" # Subimos la versión por el cambio de arquitectura
)

API_KEY_SECRETA = "siscomat_token_seguro_2026"
header_scheme = APIKeyHeader(name="X-API-Key")

def validar_api_key(api_key: str = Security(header_scheme)):
    if api_key != API_KEY_SECRETA:
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")
    return api_key

@app.get("/", tags=["Monitoreo"])
def health_check():
    return {"estado": "en linea", "servicio": "Generador de PDFs"}

# --- ENDPOINT 1: VALIDAR PLANTILLA ---
@app.post(
    "/api/v1/constancias/validar-plantilla", 
    response_model=RespuestaValidacionPlantilla,
    tags=["Gestión de Plantillas"]
)
async def validar_plantilla_endpoint(
    peticion: PeticionValidacionPlantilla,
    api_key: str = Depends(validar_api_key)
):
    try:
        plantilla_bytes = base64.b64decode(peticion.plantilla_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Base64 inválido.")

    resultado = validar_plantilla(plantilla_bytes)
    return RespuestaValidacionPlantilla(**resultado)

# --- ENDPOINT 2: PREVISUALIZAR CONSTANCIA ---
@app.post(
    "/api/v1/constancias/previsualizar", 
    response_model=RespuestaIndividual,
    tags=["Gestión de Plantillas"]
)
async def previsualizar_constancia(
    peticion: PeticionPrevisualizacion,
    api_key: str = Depends(validar_api_key)
):
    try:
        plantilla_bytes = base64.b64decode(peticion.plantilla_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Base64 inválido.")

    try:
        # Inyectamos una URL falsa para generar un QR ilustrativo
        pdf_bytes = procesar_pdf(
            nombre=peticion.nombre_participante,
            curso=peticion.nombre_curso,
            url_validacion="https://siscomat.com/validar/EJEMPLO-QR-PREVISUALIZACION",
            plantilla_bytes=plantilla_bytes
        )
        pdf_base64_str = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return RespuestaIndividual(
            estado="completado",
            mensaje="Previsualización generada",
            archivo_base64=pdf_base64_str
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en procesamiento: {str(e)}")

# --- ENDPOINT 3: GENERACIÓN REAL ---
@app.post(
    "/api/v1/constancias/generar-individual", 
    response_model=RespuestaIndividual,
    tags=["Generación"]
)
async def generar_constancia_individual(
    peticion: PeticionGeneracionIndividual,
    api_key: str = Depends(validar_api_key)
):
    try:
        plantilla_bytes = base64.b64decode(peticion.plantilla_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Base64 inválido.")

    try:
        pdf_bytes = procesar_pdf(
            nombre=peticion.nombre_participante,
            curso=peticion.nombre_curso,
            url_validacion=peticion.url_validacion,
            plantilla_bytes=plantilla_bytes
        )
        pdf_base64_str = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return RespuestaIndividual(
            estado="completado",
            mensaje="Constancia generada",
            archivo_base64=pdf_base64_str
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en procesamiento: {str(e)}")