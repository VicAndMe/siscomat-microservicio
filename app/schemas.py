from pydantic import BaseModel, Field
from typing import List


class PeticionValidacionPlantilla(BaseModel):
    plantilla_base64: str = Field(..., description="PDF base codificado en Base64")

class RespuestaValidacionPlantilla(BaseModel):
    es_valida: bool
    placeholders_encontrados: List[str]
    placeholders_faltantes: List[str]


class PeticionPrevisualizacion(BaseModel):
    nombre_curso: str = Field(..., max_length=60, example="Introducción a R (Prueba)")
    nombre_participante: str = Field(..., max_length=60, example="Nombre Apellido de Prueba")
    plantilla_base64: str = Field(..., description="PDF base codificado en Base64")


class PeticionGeneracionIndividual(BaseModel):
    nombre_curso: str = Field(..., max_length=60, example="Introducción a R")
    nombre_participante: str = Field(..., max_length=60, example="Víctor Andrés Horta Félix")
    url_validacion: str = Field(..., example="https://siscomat.com/validar/XYZ123")
    plantilla_base64: str = Field(..., description="PDF base codificado en Base64")

class RespuestaIndividual(BaseModel):
    estado: str = Field(..., example="completado")
    mensaje: str = Field(..., example="Constancia generada exitosamente")
    archivo_base64: str