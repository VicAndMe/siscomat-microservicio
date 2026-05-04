from pydantic import BaseModel, Field
from typing import List

# --- MODELOS PARA VALIDACIÓN DE PLANTILLA ---
class PeticionValidacionPlantilla(BaseModel):
    plantilla_base64: str = Field(..., description="PDF base codificado en Base64")

class RespuestaValidacionPlantilla(BaseModel):
    es_valida: bool
    placeholders_encontrados: List[str]
    placeholders_faltantes: List[str]

# --- MODELOS PARA PREVISUALIZACIÓN ---
class PeticionPrevisualizacion(BaseModel):
    nombre_curso: str = Field(..., example="Introducción a R (Prueba)")
    nombre_participante: str = Field(..., example="Nombre Apellido de Prueba")
    plantilla_base64: str = Field(..., description="PDF base codificado en Base64")

# --- MODELOS PARA GENERACIÓN INDIVIDUAL (AL VUELO) ---
class PeticionGeneracionIndividual(BaseModel):
    nombre_curso: str = Field(..., example="Introducción a R")
    nombre_participante: str = Field(..., example="Víctor Andrés Horta Félix")
    url_validacion: str = Field(..., example="https://siscomat.com/validar/XYZ123")
    plantilla_base64: str = Field(..., description="PDF base codificado en Base64")

class RespuestaIndividual(BaseModel):
    estado: str = Field(..., example="completado")
    mensaje: str = Field(..., example="Constancia generada exitosamente")
    archivo_base64: str