import os
import time
import sys
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState

load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0.2,
    max_tokens=1500,
    timeout=60,
    max_retries=1
)

def update_progress(percent: int, message: str):
    """Muestra una barra de progreso dinámica con porcentaje en la terminal."""
    bar_length = 25
    filled = int(bar_length * percent // 100)
    bar = '█' * filled + '-' * (bar_length - filled)
    sys.stdout.write(f'\r[{bar}] {percent}% - {message}')
    sys.stdout.flush()
    if percent == 100:
        print()

def limpiar_y_parsear_json(texto_respuesta: str):
    """Limpia bloques de Markdown y repara posibles saltos de línea para asegurar un JSON válido."""
    texto_limpio = texto_respuesta.strip()
    # Remover bloques de código markdown si los trae el LLM
    texto_limpio = re.sub(r"^```json\s*", "", texto_limpio, flags=re.IGNORECASE)
    texto_limpio = re.sub(r"^```\s*", "", texto_limpio, flags=re.IGNORECASE)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)
    texto_limpio = texto_limpio.strip()
    
    return json.loads(texto_limpio)

def pedagogical_writer_node(state: AgentState):
    """
    Agente Redactor Inteligente (NuevaMente RAG): 
    Genera un paquete educativo compacto y estructurado en formato json 
    para ajustarse con seguridad al límite de tokens.
    """
    print(f"\n🚀 [Agente Redactor] Generando paquete educativo estructurado (Hackathon ONE)...")
    
    update_progress(20, "Analizando parámetros y perfil del estudiante...")
    profile = state.get("target_profile", "Principiante")
    format_type = state.get("output_format", "Flashcards")
    nicho = state.get("nicho_sector", "General")
    
    raw_chunks = state.get("retrieved_chunks", [""])
    full_text = "\n".join(raw_chunks)
    
    update_progress(50, "Procesando contenido técnico y adaptando didácticamente...")
    
    system_prompt = SystemMessage(content=f"""
    Eres el Agente Redactor Pedagógico de la plataforma 'NuevaMente' (Oracle Next Education & Alura).
    Transforma el documento técnico en un paquete educativo estructurado estrictamente en formato json. No incluyas texto antes ni después del json.
    
    Parámetros:
    - Perfil: {profile}
    - Formato: {format_type}
    - Sector / Población: {nicho}
    
    REGLA DE TAMAÑO: Mantén las descripciones concisas, directas y de alto impacto técnico para garantizar que el json cierre correctamente sin superar los tokens. No uses comillas dobles sin escapar dentro de los textos.
    
    Devuelve EXTREMADAMENTE limpio un objeto json que siga esta estructura exacta:
    
    {{
    "status": "exito",
    "metadatos": {{
    "perfil_aplicado": "{profile}",
    "formato_generado": "{format_type}",
    "nicho_sector": "{nicho}",
    "tiempo_estimado_estudio_minutos": 10,
    "conceptos_clave": ["concepto1", "concepto2"]
    }},
    "contenido_adaptado": {{
    "titulo": "Título adaptado al perfil",
    "introduccion_contextualizada": "Breve introducción o analogía alineada al nivel del estudiante.",
    "items": [
        {{
        "frente": "Concepto, pregunta o paso principal",
        "dorso": "Explicación técnica precisa basada en la fuente",
        "pista_didactica": "Analogía o pista conceptual breve"
        }},
        {{
        "frente": "Segundo concepto o paso clave",
        "dorso": "Explicación técnica detallada",
        "pista_didactica": "Pista orientada al perfil"
        }}
    ]
    }},
    "evaluacion_calidad": {{
    "anclaje_fuente_score": 0.98,
    "claridad_pedagogica": "Alta",
    "observaciones": "Contenido adaptado correctamente."
    }},
    "almacenamiento_oci": {{
    "bucket": "nuevamente-contenidos-educativos",
    "objeto_id": "contenido-general-{profile.lower()}-{format_type.lower()}-001.json",
    "status_upload": "completado"
    }}
    }}
    """)
    
    human_prompt = HumanMessage(content=f"Documento fuente:\n\n{full_text[:8000]}")
    
    update_progress(80, "Construyendo esquema JSON oficial...")
    try:
        time.sleep(0.5)
        response = llm.invoke([system_prompt, human_prompt])
        content_str = response.content
        
        # Parseo con la función de limpieza robusta
        parsed_json = limpiar_y_parsear_json(content_str)
        formatted_json_str = json.dumps(parsed_json, indent=2, ensure_ascii=False)
        
        update_progress(100, "¡Paquete educativo generado exitosamente!")
        
        return {
            "processed_content": formatted_json_str,
            "iteration_count": 2
        }
    except Exception as e:
        print(f"\n⚠ [Error en Redactor]: {e}")
        error_payload = {
            "status": "error",
            "error_message": str(e),
            "metadatos": {
                "perfil_aplicado": profile,
                "formato_generado": format_type,
                "nicho_sector": nicho
            }
        }
        return {
            "processed_content": json.dumps(error_payload, indent=2, ensure_ascii=False),
            "iteration_count": 2
        }


def critic_agent_node(state: AgentState):
    """
    Agente Crítico de Calidad: Verifica que el JSON generado contenga la estructura 
    oficial del hackathon y esté completo.
    """
    content = state.get("processed_content", "")
    print("🔍 [Validador / Agente Crítico] Verificando estructura JSON del Hackathon...")
    
    try:
        data = json.loads(content)
        if data.get("status") == "error" or not data.get("contenido_adaptado"):
            print("⚠ [Validador] Estructura incompleta o con errores.")
            feedback = "MEJORA: El JSON no cumple con la estructura oficial requerida."
        else:
            print("✅ [Validador] Estructura JSON del Hackathon verificada y APROBADA.")
            feedback = "APROBADO"
    except Exception as err:
        print(f"⚠️ [Validador] Error al parsear JSON: {err}")
        feedback = "MEJORA: Error de parseo JSON por truncamiento."
        
    return {"review_feedback": feedback}