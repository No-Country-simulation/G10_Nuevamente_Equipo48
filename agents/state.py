from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    raw_document_text: str       # Texto extraído del documento técnico
    target_profile: str          # "principiante", "junior", "tech_lead", "ejecutivo"
    output_format: str           # "flashcards", "quiz", "guia_paso_a_paso", "resumen_ejecutivo"
    retrieved_chunks: List[str]  # Fragmentos recuperados por el RAG
    processed_content: str       # El resultado final adaptado
    review_feedback: str         # Comentarios del agente crítico para correcciones
    iteration_count: int         # Para controlar los bucles y evitar loops infinitos

    # Nuevos campos de Metadatos (Corpus y Aprendizaje)
    metadata_corpus: Dict[str, Any]
    learning_metadata: Dict[str, Any]