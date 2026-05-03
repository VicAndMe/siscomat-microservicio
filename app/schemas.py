from pydantic import BaseModel, Field
from typing import List, Optional

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

# --- MODELOS PARA GENERACIÓN EN LOTE (CSV INICIAL) ---
class DatosParticipante(BaseModel):
    id_participante: int = Field(..., example=1045, description="ID de BD para que .NET lo rastree")
    nombre_completo: str = Field(..., example="Ana Martínez")
    url_validacion: str = Field(..., example="https://siscomat.com/validar/ABC987")

class PeticionGeneracionLote(BaseModel):
    nombre_curso: str = Field(..., example="Semana de Matemáticas")
    plantilla_base64: str = Field(..., description="PDF base codificado en Base64") 
    participantes: List[DatosParticipante]

class ResultadoParticipante(BaseModel):
    id_participante: int # Crucial para la base de datos de .NET
    estado: str = Field(..., example="completado") 
    mensaje: Optional[str] = None
    archivo_base64: Optional[str] = None 

class RespuestaLote(BaseModel):
    curso: str
    total_procesados: int
    resultados: List[ResultadoParticipante]