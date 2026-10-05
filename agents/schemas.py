from pydantic import BaseModel, Field
from typing import List

class SectionDetail(BaseModel):
    section_number: int = Field(description="Número de la sección")
    title: str = Field(description="Título de la sección")
    content: str = Field(description="Contenido técnico detallado de la sección")

class PedagogicalReportSchema(BaseModel):
    title: str = Field(description="Título general del resumen técnico")
    profile: str = Field(description="Perfil del destinatario (ej. tech_lead)")
    format_type: str = Field(description="Formato del documento (ej. resumen_ejecutivo)")
    key_concepts: List[str] = Field(description="Lista de conceptos clave extraídos")
    prerequisites: List[str] = Field(description="Prerrequisitos técnicos necesarios")
    estimated_time: str = Field(description="Tiempo estimado de adopción o estudio")
    sections: List[SectionDetail] = Field(description="Secciones estructuradas del informe técnico")