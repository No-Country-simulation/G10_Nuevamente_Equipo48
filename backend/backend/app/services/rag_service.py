"""
RAG Service — NuevaMente Backend.

Responsabilidades:
  - Chunking de texto con tiktoken (cl100k_base, ventanas con overlap de 50 tokens)
  - Generación de embeddings reales (SentenceTransformer o OpenAI)
  - Ingesta de documentos en un índice FAISS (IndexFlatIP con vectores normalizados L2)
  - Recuperación semántica de chunks por similitud coseno

Nota sobre modelos de embedding:
  El modelo usado en la búsqueda DEBE coincidir con el usado en la ingesta.
  Cambiar LLM_PROVIDER entre operaciones puede producir resultados incorrectos.

Esta tarea implementa únicamente las partes de chunking y embeddings.
Los métodos ingest_document, retrieve y document_exists se añaden en la tarea 5.2.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

import numpy as np
import tiktoken

from app.core.config import Settings
from app.core.exceptions import DocumentNotFoundError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constante de overlap entre chunks consecutivos (en tokens)
# ---------------------------------------------------------------------------
_OVERLAP_TOKENS = 50


# ---------------------------------------------------------------------------
# Dataclass: metadata de un chunk individual
# ---------------------------------------------------------------------------

@dataclass
class ChunkMetadata:
    """
    Representa un fragmento de texto extraído de un documento.

    Attributes:
        chunk_id:     Identificador único (UUID) del fragmento.
        documento_id: ID del documento padre del que proviene el fragmento.
        texto:        Contenido textual del fragmento.
        posicion:     Índice ordinal del chunk dentro del documento (base 0).
        score:        Puntuación de similitud semántica; solo se rellena en
                      los resultados de una búsqueda (retrieve). Valor por
                      defecto 0.0 durante la ingesta.
    """

    chunk_id: str
    documento_id: str
    texto: str
    posicion: int
    score: float = field(default=0.0)


# ---------------------------------------------------------------------------
# RAG Service
# ---------------------------------------------------------------------------


class RAGService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

        self._chunks: list[ChunkMetadata] = []
        self._index = None
        self._dimension: int = 0

        # --- Cargar modelo de embeddings ---
        # Los embeddings se generan localmente con SentenceTransformer.
        # El proveedor LLM (OpenAI/Gemini) se utiliza posteriormente
        # para la generación/adaptación de contenido y no determina
        # el motor de embeddings.

        self._use_openai_embeddings = False
        self._sentence_transformer = self._cargar_sentence_transformer(
            settings.embedding_model
        )

        logger.info(
            "RAGService: usando embeddings locales SentenceTransformer (modelo=%s)",
            settings.embedding_model,
        )
    # ------------------------------------------------------------------
    # Método auxiliar privado: carga del modelo local
    # ------------------------------------------------------------------

    @staticmethod
    def _cargar_sentence_transformer(modelo: str):
        """
        Carga y retorna una instancia de SentenceTransformer para el modelo dado.

        Args:
            modelo: Nombre del modelo sentence-transformers (p. ej. "all-MiniLM-L6-v2").

        Returns:
            Instancia de SentenceTransformer lista para codificar textos.
        """
        try:
            from sentence_transformers import SentenceTransformer  # noqa: PLC0415
            transformer = SentenceTransformer(modelo)
            logger.info("RAGService: SentenceTransformer cargado (modelo=%s)", modelo)
            return transformer
        except Exception as exc:
            logger.error(
                "RAGService: no se pudo cargar SentenceTransformer '%s': %s",
                modelo,
                exc,
            )
            raise

    # ------------------------------------------------------------------
    # chunk_text: segmentación de texto en fragmentos de tamaño controlado
    # ------------------------------------------------------------------

    def chunk_text(self, text: str, chunk_size: int) -> list[str]:
        """
        Segmenta el texto en fragmentos de hasta `chunk_size` tokens.

        Estrategia:
          1. Tokenizar el texto completo con tiktoken (encoding cl100k_base).
          2. Deslizar una ventana de `chunk_size` tokens con un overlap de
             _OVERLAP_TOKENS tokens entre ventanas consecutivas.
          3. Reconstruir el texto de cada ventana decodificando los tokens.

        Un texto vacío retorna una lista vacía. Si el texto tiene menos
        tokens que `chunk_size`, se retorna como un único chunk.

        Args:
            text:       Texto plano de entrada (puede ser largo).
            chunk_size: Número máximo de tokens por chunk. Debe ser > 0.

        Returns:
            Lista de strings, cada uno representando un fragmento del texto.
        """
        if not text or not text.strip():
            return []

        if chunk_size <= 0:
            raise ValueError(f"chunk_size debe ser mayor que 0; recibido: {chunk_size}")

        # Codificador compatible con los modelos GPT de OpenAI y con
        # sentence-transformers (se usa solo para contar/dividir tokens)
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens_completos: list[int] = encoding.encode(text)

        # Si el texto cabe en un solo chunk, retornar directamente
        if len(tokens_completos) <= chunk_size:
            return [text]

        chunks: list[str] = []
        inicio = 0
        avance = max(1, chunk_size - _OVERLAP_TOKENS)  # paso efectivo entre ventanas

        while inicio < len(tokens_completos):
            fin = min(inicio + chunk_size, len(tokens_completos))
            ventana_tokens = tokens_completos[inicio:fin]

            # Reconstruir el texto del fragmento decodificando los tokens
            texto_chunk = encoding.decode(ventana_tokens)
            chunks.append(texto_chunk)

            if fin == len(tokens_completos):
                # Se procesaron todos los tokens → terminar
                break

            inicio += avance

        return chunks

    # ------------------------------------------------------------------
    # generate_embeddings: vectores semánticos normalizados L2
    # ------------------------------------------------------------------

    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        """
        Genera embeddings reales para la lista de textos dada.

        Selección de backend:
          - Si self._use_openai_embeddings es True: llama a
            openai.embeddings.create() con el modelo configurado en settings.
          - En caso contrario: usa self._sentence_transformer.encode().

        Los vectores resultantes se normalizan en norma L2 antes de retornar.
        Esta normalización permite usar FAISS IndexFlatIP (producto interno)
        para calcular similitud coseno de manera eficiente.

        División por cero: si un vector tiene norma 0 (vector nulo), se deja
        sin modificar para evitar NaN; es una situación anómala que no debería
        ocurrir con textos no vacíos.

        Args:
            texts: Lista de strings a vectorizar. No debe estar vacía.

        Returns:
            Array numpy de dtype float32 con forma (N, dim), normalizado L2.
            N = len(texts), dim = dimensión del modelo de embeddings.

        Raises:
            ValueError: Si `texts` está vacío.
        """
        if not texts:
            raise ValueError("La lista de textos para generar embeddings no puede estar vacía.")

        if self._use_openai_embeddings:
            vectores = self._embeddings_openai(texts)
        else:
            vectores = self._embeddings_sentence_transformer(texts)

        # Normalización L2: vector / ||vector||₂
        # Forma: (N, dim) / (N, 1) → cada fila se divide entre su propia norma
        normas = np.linalg.norm(vectores, axis=1, keepdims=True)

        # Reemplazar normas cero por 1.0 para evitar división por cero (NaN);
        # los vectores nulos permanecen como cero, lo cual es aceptable.
        normas_seguras = np.where(normas == 0.0, 1.0, normas)
        vectores_normalizados = vectores / normas_seguras

        return vectores_normalizados.astype(np.float32)

    # ------------------------------------------------------------------
    # Backends privados de generación de embeddings
    # ------------------------------------------------------------------

    def _embeddings_openai(self, texts: list[str]) -> np.ndarray:
        """
        Genera embeddings usando la API de OpenAI.

        Usa el modelo indicado en settings.embedding_model.
        Requiere que LLM_API_KEY esté configurada; de lo contrario, la API
        de OpenAI lanzará un error de autenticación.

        Args:
            texts: Lista de strings a vectorizar.

        Returns:
            Array numpy de dtype float32 con forma (N, dim).
        """
        import openai  # noqa: PLC0415

        cliente = openai.OpenAI(api_key=self._settings.llm_api_key)
        respuesta = cliente.embeddings.create(
            model=self._settings.embedding_model,
            input=texts,
        )

        # La respuesta contiene una lista de objetos Embedding ordenados por índice
        vectores = np.array(
            [item.embedding for item in respuesta.data],
            dtype=np.float32,
        )
        return vectores

    def _embeddings_sentence_transformer(self, texts: list[str]) -> np.ndarray:
        """
        Genera embeddings usando SentenceTransformer (local, sin costos de API).

        Args:
            texts: Lista de strings a vectorizar.

        Returns:
            Array numpy de dtype float32 con forma (N, dim).
        """
        vectores = self._sentence_transformer.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return np.array(vectores, dtype=np.float32)

    # ------------------------------------------------------------------
    # document_exists: verificación de existencia de un documento en el índice
    # ------------------------------------------------------------------

    def document_exists(self, documento_id: str) -> bool:
        """
        Verifica si existe al menos un chunk del documento indicado en el índice.

        Args:
            documento_id: Identificador del documento a buscar.

        Returns:
            True si hay al menos un chunk con ese documento_id; False si no hay ninguno.
        """
        return any(c.documento_id == documento_id for c in self._chunks)

    # ------------------------------------------------------------------
    # ingest_document: ingesta de un documento en el índice FAISS
    # ------------------------------------------------------------------

    def ingest_document(self, text: str, documento_id: str) -> int:
        """
        Ingesta un documento en el índice FAISS.

        Proceso:
          1. Segmentar el texto con chunk_text usando el tamaño configurado.
          2. Si no hay chunks (texto vacío), retornar 0 sin modificar el índice.
          3. Generar embeddings normalizados L2 de todos los chunks.
          4. Si el índice FAISS aún no existe, inicializarlo con la dimensión real
             de los embeddings (IndexFlatIP).
          5. Agregar los vectores al índice y los metadatos a _chunks.
          6. Retornar el número de chunks indexados.

        Args:
            text:         Texto plano del documento a ingestar.
            documento_id: Identificador único del documento (se asocia a cada chunk).

        Returns:
            Número de chunks añadidos al índice. Puede ser 0 si el texto está vacío.
        """
        chunks_texts = self.chunk_text(text, self._settings.rag_chunk_size)

        if not chunks_texts:
            logger.info(
                "ingest_document: texto vacío para documento_id=%s; nada que ingestar.",
                documento_id,
            )
            return 0

        vectores = self.generate_embeddings(chunks_texts)

        # Inicializar el índice FAISS la primera vez (la dimensión depende del modelo)
        if self._index is None:
            import faiss  # noqa: PLC0415

            self._dimension = vectores.shape[1]
            self._index = faiss.IndexFlatIP(self._dimension)
            logger.info(
                "ingest_document: índice FAISS inicializado con dimension=%d",
                self._dimension,
            )

        self._index.add(vectores)

        nuevos_chunks: list[ChunkMetadata] = [
            ChunkMetadata(
                chunk_id=str(uuid.uuid4()),
                documento_id=documento_id,
                texto=chunk_texto,
                posicion=i,
            )
            for i, chunk_texto in enumerate(chunks_texts)
        ]
        self._chunks.extend(nuevos_chunks)

        logger.info(
            "ingest_document: %d chunks indexados para documento_id=%s",
            len(nuevos_chunks),
            documento_id,
        )
        return len(nuevos_chunks)

    # ------------------------------------------------------------------
    # retrieve: recuperación semántica de chunks relevantes
    # ------------------------------------------------------------------

    def retrieve(self, query: str, documento_id: str, top_k: int) -> list[ChunkMetadata]:
        """
        Recupera los top_k chunks más relevantes del documento indicado.

        Proceso:
          1. Verificar que el documento existe en el índice; lanzar
             DocumentNotFoundError si no existe.
          2. Verificar que el índice FAISS no es None.
          3. Generar el embedding normalizado de la query.
          4. Buscar los top_k * 3 vecinos más cercanos en el índice FAISS
             (se busca más para poder filtrar por documento_id).
          5. Filtrar únicamente los chunks pertenecientes al documento_id dado
             e ignorar índices -1 (FAISS los devuelve cuando no hay suficientes resultados).
          6. Ordenar por score descendente y tomar los top_k mejores.
          7. Retornar la lista con el campo score asignado.

        Args:
            query:        Texto de la consulta semántica.
            documento_id: ID del documento en el que buscar.
            top_k:        Número máximo de chunks a retornar.

        Returns:
            Lista de ChunkMetadata ordenada por similitud descendente (máximo top_k elementos).

        Raises:
            DocumentNotFoundError: Si no existe ningún chunk con el documento_id dado,
                                   o si el índice FAISS no ha sido inicializado.
        """
        if not self.document_exists(documento_id):
            raise DocumentNotFoundError(
                message=f"El documento '{documento_id}' no existe en el índice.",
                detail="El documento no fue ingestado o el servidor fue reiniciado.",
            )

        if self._index is None:
            raise DocumentNotFoundError(
                message="El índice FAISS no ha sido inicializado.",
                detail="No se ha ingestado ningún documento todavía.",
            )

        query_embedding = self.generate_embeddings([query])  # shape (1, dim)

        candidatos = top_k * 3
        distances, indices = self._index.search(query_embedding, candidatos)

        # distances e indices tienen shape (1, candidatos) → aplanar
        distancias_flat = distances[0]
        indices_flat = indices[0]

        # Filtrar por documento_id y descartar índices inválidos (-1)
        resultados: list[tuple[float, ChunkMetadata]] = []
        for idx, score in zip(indices_flat, distancias_flat):
            if idx < 0:
                continue
            chunk = self._chunks[idx]
            if chunk.documento_id == documento_id:
                resultados.append((float(score), chunk))

        # Ordenar por score descendente y tomar los top_k
        resultados.sort(key=lambda x: x[0], reverse=True)
        resultados = resultados[:top_k]

        # Construir ChunkMetadata con score asignado
        return [
            ChunkMetadata(
                chunk_id=chunk.chunk_id,
                documento_id=chunk.documento_id,
                texto=chunk.texto,
                posicion=chunk.posicion,
                score=score,
            )
            for score, chunk in resultados
        ]
