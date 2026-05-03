from fastapi import FastAPI, status, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.schemas import (
    PeticionGeneracionLote, RespuestaLote, ResultadoParticipante,
    PeticionGeneracionIndividual, RespuestaIndividual
)
from app.services.pdf_generator import procesar_pdf
import base64

app = FastAPI(
    title="SISCOMAT - API de Generación de Constancias (PDF)",
    version="1.0.0"
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

# --- ENDPOINT 1: GENERACIÓN INDIVIDUAL (AL VUELO) ---
@app.post(
    "/api/v1/constancias/generar-individual", 
    response_model=RespuestaIndividual,
    tags=["Generación"]
)
async def generar_constancia_individual(
    peticion: PeticionGeneracionIndividual,
    api_key: str = Depends(validar_api_key)
):
    """
    Genera una única constancia. Ideal para cuando el usuario hace clic en 'Descargar'
    desde el portal público y .NET solicita el archivo al vuelo.
    """
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

# --- ENDPOINT 2: GENERACIÓN EN LOTE (ACCIÓN DEL GESTOR CON CSV) ---
@app.post(
    "/api/v1/constancias/generar-lote", 
    response_model=RespuestaLote,
    status_code=status.HTTP_207_MULTI_STATUS, 
    tags=["Generación"]
)
async def generar_constancias_lote(
    peticion: PeticionGeneracionLote,
    api_key: str = Depends(validar_api_key)
):
    """
    Procesa un lote completo proveniente de un CSV.
    Retorna los archivos y sus IDs para que .NET guarde el registro en PostgreSQL.
    """
    resultados_finales = []
    
    try:
        plantilla_bytes = base64.b64decode(peticion.plantilla_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Base64 inválido.")

    for participante in peticion.participantes:
        try:
            pdf_bytes = procesar_pdf(
                nombre=participante.nombre_completo,
                curso=peticion.nombre_curso,
                url_validacion=participante.url_validacion,
                plantilla_bytes=plantilla_bytes
            )
            pdf_base64_str = base64.b64encode(pdf_bytes).decode('utf-8')

            resultados_finales.append(
                ResultadoParticipante(
                    id_participante=participante.id_participante, # ID de retorno
                    estado="completado",
                    mensaje="Constancia generada",
                    archivo_base64=pdf_base64_str
                )
            )
        except Exception as e:
            resultados_finales.append(
                ResultadoParticipante(
                    id_participante=participante.id_participante,
                    estado="error",
                    mensaje=f"Fallo al generar: {str(e)}"
                )
            )
            
    return RespuestaLote(
        curso=peticion.nombre_curso,
        total_procesados=len(peticion.participantes),
        resultados=resultados_finales
    )