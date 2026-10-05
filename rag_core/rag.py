import os
import math
from collections import Counter
from langchain_text_splitters import RecursiveCharacterTextSplitter

def build_vector_store_from_text(document_text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Segmenta el documento en chunks semánticos y prepara un almacén ligero 
    utilizando Python puro (sin dependencias externas como scikit-learn o FAISS).
    """
    # 1. Segmentación en chunks semánticos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "]
    )
    docs = text_splitter.create_documents([document_text])
    chunk_texts = [doc.page_content for doc in docs]
    
    return {
        "chunks": chunk_texts
    }

def _tokenize(text: str):
    """Función auxiliar para limpiar y tokenizar texto en palabras."""
    import re
    tokens = re.findall(r'\w+', text.lower())
    return Counter(tokens)

def _cosine_similarity_dict(vec1, vec2):
    """Calcula similitud de coseno entre dos diccionarios de frecuencias de palabras."""
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum(vec1[x] * vec2[x] for x in intersection)
    
    sum1 = sum(v ** 2 for v in vec1.values())
    sum2 = sum(v ** 2 for v in vec2.values())
    
    if sum1 == 0 or sum2 == 0:
        return 0.0
    return numerator / (math.sqrt(sum1) * math.sqrt(sum2))

def retrieve_relevant_context(vector_store: dict, query: str, k: int = 4) -> list[str]:
    """
    Recupera los k chunks más relevantes utilizando similitud de coseno de frecuencias de palabras (Python puro).
    """
    chunks = vector_store.get("chunks", [])
    if not chunks:
        return []
    
    query_vec = _tokenize(query)
    scored_chunks = []
    
    for chunk in chunks:
        chunk_vec = _tokenize(chunk)
        score = _cosine_similarity_dict(query_vec, chunk_vec)
        scored_chunks.append((score, chunk))
    
    # Ordenar de mayor a menor similitud
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    # Retornar los k mejores fragmentos
    return [chunk for score, chunk in scored_chunks[:k]]