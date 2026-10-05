import os
from dotenv import load_dotenv
from pypdf import PdfReader
from agents.graph import app_graph

load_dotenv()

def cargar_documento(ruta_archivo: str) -> str:
    """Extrae texto de un archivo PDF o de un archivo de texto plano/Markdown."""
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo en: {ruta_archivo}")
    
    # Si es un PDF, usamos PyPDF
    if ruta_archivo.endswith(".pdf"):
        reader = PdfReader(ruta_archivo)
        texto_extraido = ""
        for page in reader.pages:
            texto_extraido += page.extract_text() or ""
        return texto_extraido
    
    # Si es Markdown o texto plano
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        return f.read()

# Apunta a tu PDF real en la carpeta data/raw/
ruta_doc = "data/raw/documento_prueba.pdf"

try:
    texto_real = cargar_documento(ruta_doc)
    print(f"📄 Documento PDF cargado y procesado exitosamente desde: {ruta_doc}")
except Exception as e:
    print(f"⚠️ {e}")
    texto_real = "Guía técnica de arquitectura cloud y microservicios de respaldo."

# Estado inicial para probar los agentes con el texto del PDF
initial_state = {
    "raw_document_text": texto_real,
    "target_profile": "tech_lead",           # Prueba con "principiante", "junior", "tech_lead", "ejecutivo"
    "output_format": "resumen_ejecutivo",    # Prueba con "flashcards", "quiz", "guia_paso_a_paso"
    "retrieved_chunks": [texto_real[:2000]], # Simulamos el fragmento que pasaría el RAG
    "processed_content": "",
    "review_feedback": ""
}

print("\n🚀 Ejecutando flujo de agentes con contenido del PDF...")

result = app_graph.invoke(initial_state)

print("\n--- RESULTADO OBTENIDO (ADAPTADO AL PERFIL) ---")
print(result["processed_content"])

print("\n--- REVISIÓN DEL AGENTE CRÍTICO ---")
print(result["review_feedback"])