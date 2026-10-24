"""
Document Service — NuevaMente Backend.

Responsabilidad única: extraer texto plano de archivos en formato PDF,
Markdown o TXT, sin generar contenido simulado ni hardcodeado.

Tipos MIME soportados:
  - application/pdf  → extracción mediante PyMuPDF (fitz)
  - text/markdown    → parsing con markdown-it-py + fallback regex
  - text/plain       → decodificación UTF-8 / latin-1

Excepciones:
  - ExtractionError  → se lanza ante cualquier fallo de extracción
"""

from __future__ import annotations

import re

import fitz  # PyMuPDF
from markdown_it import MarkdownIt

from app.core.exceptions import ExtractionError

# ---------------------------------------------------------------------------
# Tipos MIME aceptados por el servicio
# ---------------------------------------------------------------------------
_MIME_PDF = "application/pdf"
_MIME_MARKDOWN = "text/markdown"
_MIME_PLAIN = "text/plain"

_SUPPORTED_MIMES = {_MIME_PDF, _MIME_MARKDOWN, _MIME_PLAIN}


class DocumentService:
    """
    Servicio de extracción de texto para NuevaMente Backend.

    Expone un único método público `extract_text` que actúa como dispatcher
    hacia los métodos privados especializados por tipo de archivo.
    """

    # ------------------------------------------------------------------
    # Método público principal
    # ------------------------------------------------------------------

    def extract_text(self, file_bytes: bytes, mime_type: str) -> str:
        """
        Extrae el texto plano del archivo según su tipo MIME.

        Args:
            file_bytes: Contenido binario del archivo.
            mime_type:  Tipo MIME del archivo (sin parámetros adicionales).

        Returns:
            String con el texto extraído, listo para procesar.

        Raises:
            ExtractionError: Si el tipo MIME no está soportado, el archivo
                             está vacío, corrupto o no contiene texto extraíble.
        """
        # Normalizar: descartar parámetros adicionales como "; charset=utf-8"
        mime_base = mime_type.split(";")[0].strip().lower()

        if mime_base == _MIME_PDF:
            return self._extract_pdf(file_bytes)
        elif mime_base == _MIME_MARKDOWN:
            return self._extract_markdown(file_bytes)
        elif mime_base == _MIME_PLAIN:
            return self._extract_txt(file_bytes)
        else:
            raise ExtractionError(
                message=(
                    f"Tipo de archivo '{mime_base}' no soportado. "
                    f"Tipos permitidos: {', '.join(sorted(_SUPPORTED_MIMES))}."
                ),
                detail=f"mime_type recibido: {mime_type!r}",
            )

    def extract_structure(self, file_bytes: bytes, mime_type: str) -> list[dict]:
        """
        Extrae la estructura documental (títulos, subtítulos y apartados)
        según el tipo MIME del archivo.

        Args:
            file_bytes: Contenido binario del archivo.
            mime_type:  Tipo MIME del archivo.

        Returns:
            Lista de diccionarios con formato:
            [{"titulo": "...", "nivel": 1, "pagina": 5}, ...]
            Retorna lista vacía si el documento no tiene estructura recuperable.
        """
        mime_base = mime_type.split(";")[0].strip().lower()
        if mime_base == _MIME_PDF:
            return self._extract_pdf_structure(file_bytes)
        elif mime_base == _MIME_MARKDOWN:
            return self._extract_markdown_structure(file_bytes)
        elif mime_base == _MIME_PLAIN:
            return self._extract_txt_structure(file_bytes)
        return []

    # ------------------------------------------------------------------
    # Extracción de PDF
    # ------------------------------------------------------------------

    def _extract_pdf(self, file_bytes: bytes) -> str:
        """
        Extrae el texto real de un archivo PDF usando PyMuPDF (fitz).

        Itera sobre todas las páginas del documento y concatena el texto
        de cada una. Lanza ExtractionError si el PDF está corrupto, protegido
        con contraseña, no tiene páginas, o todo el texto extraído está vacío.

        Args:
            file_bytes: Contenido binario del archivo PDF.

        Returns:
            Texto plano concatenado de todas las páginas.

        Raises:
            ExtractionError: Ante cualquier fallo de apertura o extracción.
        """
        try:
            documento = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as exc:
            raise ExtractionError(
                message="No se pudo abrir el archivo PDF. Puede estar corrupto o protegido.",
                detail=str(exc),
            ) from exc

        if documento.page_count == 0:
            raise ExtractionError(
                message="El archivo PDF no contiene páginas.",
                detail=f"page_count={documento.page_count}",
            )

        partes: list[str] = []
        for numero_pagina in range(documento.page_count):
            pagina = documento.load_page(numero_pagina)
            texto_pagina = pagina.get_text()
            partes.append(texto_pagina)

        texto_completo = "\n".join(partes)

        if not texto_completo.strip():
            raise ExtractionError(
                message=(
                    "El archivo PDF no contiene texto seleccionable. "
                    "Puede ser un PDF de solo imágenes sin OCR."
                ),
                detail=f"Páginas procesadas: {documento.page_count}",
            )

        return texto_completo

    # ------------------------------------------------------------------
    # Extracción de Markdown
    # ------------------------------------------------------------------

    def _extract_markdown(self, file_bytes: bytes) -> str:
        """
        Extrae el texto de un archivo Markdown eliminando la sintaxis de marcado.

        Estrategia principal:
          1. Decodifica los bytes a string UTF-8.
          2. Parsea el documento con markdown-it-py para obtener el AST.
          3. Recorre el árbol de tokens extrayendo únicamente el contenido
             de los nodos de tipo 'inline' (texto visible).

        Fallback (si el parsing produce resultado vacío):
          Aplica expresiones regulares para eliminar la sintaxis de Markdown
          más común: encabezados, negrita, cursiva, enlaces, código en línea
          y bloques de código.

        Args:
            file_bytes: Contenido binario del archivo Markdown.

        Returns:
            Texto plano sin sintaxis de Markdown.

        Raises:
            ExtractionError: Si el resultado final está vacío.
        """
        contenido_raw = file_bytes.decode("utf-8", errors="replace")

        # --- Estrategia principal: markdown-it-py AST ---
        texto_ast = self._extraer_texto_ast(contenido_raw)

        if texto_ast.strip():
            return texto_ast

        # --- Fallback: limpieza con expresiones regulares ---
        texto_regex = self._limpiar_markdown_regex(contenido_raw)

        if not texto_regex.strip():
            raise ExtractionError(
                message="No se pudo extraer texto del archivo Markdown.",
                detail="El archivo puede estar vacío o contener solo sintaxis de marcado.",
            )

        return texto_regex

    def _extraer_texto_ast(self, contenido: str) -> str:
        """
        Usa el AST de markdown-it-py para extraer únicamente los nodos de texto.

        Recorre la lista plana de tokens producida por el parser y recolecta
        el contenido de los tokens de tipo 'inline', que contiene el texto
        visible del documento (sin decoradores de bloque como heading_open, etc.).

        Args:
            contenido: String con el documento Markdown completo.

        Returns:
            Texto visible concatenado, separado por saltos de línea.
        """
        md = MarkdownIt()
        tokens = md.parse(contenido)

        fragmentos: list[str] = []

        for token in tokens:
            # Los tokens 'inline' contienen el texto real visible
            if token.type == "inline" and token.children:
                for hijo in token.children:
                    if hijo.type == "text" or hijo.type == "softbreak":
                        fragmentos.append(hijo.content if hijo.type == "text" else " ")
                    elif hijo.type == "code_inline":
                        # Preservar el contenido del código en línea sin los backticks
                        fragmentos.append(hijo.content)
            elif token.type == "fence" or token.type == "code_block":
                # Preservar el contenido de bloques de código
                fragmentos.append(token.content)

        return "\n".join(line for line in " ".join(fragmentos).splitlines() if line.strip())

    def _limpiar_markdown_regex(self, contenido: str) -> str:
        """
        Elimina la sintaxis de Markdown usando expresiones regulares.

        Patrones eliminados:
          - Bloques de código con triple backtick (``` ... ```)
          - Encabezados: líneas que comienzan con uno o más '#'
          - Negrita con '__texto__' y '**texto**'
          - Cursiva con '_texto_' y '*texto*'
          - Código en línea: `texto`
          - Imágenes: ![alt](url)
          - Enlaces: [texto](url)  →  conserva el texto del enlace
          - Tags HTML básicos: <tag> y </tag>

        Args:
            contenido: String con el documento Markdown.

        Returns:
            String con el texto limpio.
        """
        texto = contenido

        # Bloques de código (``` ... ```) — eliminar todo el bloque
        texto = re.sub(r"```[\s\S]*?```", "", texto)

        # Encabezados: ## Título → Título
        texto = re.sub(r"^#{1,6}\s+", "", texto, flags=re.MULTILINE)

        # Negrita: **texto** o __texto__ → texto
        texto = re.sub(r"\*\*(.+?)\*\*", r"\1", texto)
        texto = re.sub(r"__(.+?)__", r"\1", texto)

        # Cursiva: *texto* o _texto_ → texto
        texto = re.sub(r"\*(.+?)\*", r"\1", texto)
        texto = re.sub(r"_(.+?)_", r"\1", texto)

        # Imágenes: ![alt](url) → eliminar
        texto = re.sub(r"!\[.*?\]\(.*?\)", "", texto)

        # Enlaces: [texto](url) → texto
        texto = re.sub(r"\[(.+?)\]\(.*?\)", r"\1", texto)

        # Código en línea: `texto` → texto
        texto = re.sub(r"`(.+?)`", r"\1", texto)

        # Tags HTML simples
        texto = re.sub(r"<[^>]+>", "", texto)

        # Limpiar líneas vacías múltiples consecutivas
        texto = re.sub(r"\n{3,}", "\n\n", texto)

        return texto.strip()

    # ------------------------------------------------------------------
    # Extracción de TXT
    # ------------------------------------------------------------------

    def _extract_txt(self, file_bytes: bytes) -> str:
        """
        Lee el contenido de un archivo de texto plano.

        Intenta decodificar en UTF-8 primero. Si la proporción de caracteres
        de reemplazo (U+FFFD) es mayor al 5%, reintenta con latin-1, que
        es una codificación más permisiva para archivos legacy.

        Args:
            file_bytes: Contenido binario del archivo TXT.

        Returns:
            Texto completo del archivo.

        Raises:
            ExtractionError: Si el archivo está vacío.
        """
        if not file_bytes:
            raise ExtractionError(
                message="El archivo de texto está vacío.",
                detail="El archivo no contiene ningún byte.",
            )

        # Intento UTF-8 con reemplazo de caracteres inválidos
        texto_utf8 = file_bytes.decode("utf-8", errors="replace")

        # Calcular proporción de caracteres de reemplazo para detectar
        # archivos que no son realmente UTF-8
        proporcion_reemplazo = texto_utf8.count("\ufffd") / max(len(texto_utf8), 1)

        if proporcion_reemplazo > 0.05:
            # Demasiados caracteres de reemplazo → intentar latin-1
            texto = file_bytes.decode("latin-1", errors="replace")
        else:
            texto = texto_utf8

        if not texto.strip():
            raise ExtractionError(
                message="El archivo de texto está vacío o solo contiene espacios en blanco.",
                detail=f"Bytes recibidos: {len(file_bytes)}",
            )

        return texto

    # ------------------------------------------------------------------
    # Extracción de estructura documental
    # ------------------------------------------------------------------

    def _extract_pdf_structure(self, file_bytes: bytes) -> list[dict]:
        """
        Extrae la estructura jerárquica de un PDF a partir de marcadores internos (TOC)
        o mediante análisis de índices impresos y encabezados del documento.
        """
        try:
            documento = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception:
            return []

        if documento.page_count == 0:
            return []

        # 1. Marcadores internos (TOC / Outlines)
        try:
            toc = documento.get_toc()
            if toc:
                sections = []
                for lvl, title, page in toc:
                    t = (title or "").strip()
                    if t and not t.startswith("_Hlk") and len(t) > 2:
                        sections.append({
                            "titulo": t,
                            "nivel": int(lvl),
                            "pagina": int(page),
                        })
                if sections:
                    return sections
        except Exception:
            pass

        # 2. Búsqueda de índice impreso en las primeras páginas
        index_re = re.compile(
            r"^(?:[ií]ndice|tabla de contenido|contenido|tabla de contenidos|table of contents)\b",
            re.IGNORECASE,
        )
        sec_num_line_re = re.compile(r"^(\d+(\.\d+){1,4})\s*[\t\. ]+(.+)$")
        sec_num_only_re = re.compile(r"^(\d+(\.\d+){1,4})$")
        chap_re = re.compile(r"^(?:cap[íi]tulo|m[óo]dulo|unidad)\s+\d+[:\.\s]*(.*)", re.IGNORECASE)

        sections: list[dict] = []
        seen: set[str] = set()
        in_index = False

        for pno in range(min(20, documento.page_count)):
            try:
                pagina = documento.load_page(pno)
                text = pagina.get_text()
            except Exception:
                continue

            lines = [l.strip() for l in text.splitlines() if l.strip()]
            i = 0
            while i < len(lines):
                line = lines[i]
                if not in_index and index_re.match(line):
                    in_index = True
                    i += 1
                    continue

                if in_index:
                    # Título de capítulo
                    if chap_re.match(line):
                        t = line
                        if i + 1 < len(lines) and not sec_num_only_re.match(lines[i + 1]) and not lines[i + 1].isdigit():
                            t = f"{line}: {lines[i + 1]}"
                            i += 1
                        if t not in seen and len(t) < 120:
                            seen.add(t)
                            sections.append({"titulo": t, "nivel": 1, "pagina": pno + 1})
                        i += 1
                        continue

                    # Número en línea i, título en línea i+1
                    m_only = sec_num_only_re.match(line)
                    if m_only and i + 1 < len(lines) and not sec_num_only_re.match(lines[i + 1]) and not lines[i + 1].isdigit():
                        num = m_only.group(1)
                        t = f"{num} {lines[i + 1]}"
                        if t not in seen and len(t) < 120:
                            seen.add(t)
                            sections.append({"titulo": t, "nivel": max(1, min(num.count(".") + 1, 3)), "pagina": pno + 1})
                        i += 2
                        continue

                    # Número + título en la misma línea
                    m_num = sec_num_line_re.match(line)
                    if m_num:
                        num = m_num.group(1)
                        t = f"{num} {m_num.group(3).strip()}"
                        if t not in seen and len(t) < 120:
                            seen.add(t)
                            sections.append({"titulo": t, "nivel": max(1, min(num.count(".") + 1, 3)), "pagina": pno + 1})
                        i += 1
                        continue

                    # Título ... Página en la misma línea
                    m_dot = re.match(r"^(.+?)(?:[\t\.]{2,}|\s{3,}|\t+)(\d+)$", line)
                    if m_dot:
                        t = m_dot.group(1).strip()
                        pg = int(m_dot.group(2))
                        if len(t) > 2 and len(t) < 120 and t not in seen:
                            seen.add(t)
                            lvl = (t.count(".") + 1) if t[0].isdigit() else 1
                            sections.append({"titulo": t, "nivel": max(1, min(lvl, 3)), "pagina": pg})
                        i += 1
                        continue

                    # Título en línea i, página en línea i+1
                    if i + 1 < len(lines) and lines[i + 1].isdigit() and not line.isdigit() and len(line) > 2 and len(line) < 120:
                        t = line.strip()
                        pg = int(lines[i + 1])
                        if t not in seen:
                            seen.add(t)
                            lvl = (t.count(".") + 1) if t[0].isdigit() else 1
                            sections.append({"titulo": t, "nivel": max(1, min(lvl, 3)), "pagina": pg})
                        i += 2
                        continue

                i += 1

            if sections and in_index and pno > 10 and not any(sec_num_only_re.match(l) or chap_re.match(l) for l in lines):
                break

        if sections:
            return sections

        # 3. Fallback: búsqueda de encabezados en el cuerpo del documento
        for pno in range(min(40, documento.page_count)):
            try:
                pagina = documento.load_page(pno)
                text = pagina.get_text()
            except Exception:
                continue

            lines = [l.strip() for l in text.splitlines() if l.strip()]
            for line in lines:
                if chap_re.match(line) and len(line) < 100 and line not in seen:
                    seen.add(line)
                    sections.append({"titulo": line, "nivel": 1, "pagina": pno + 1})
                elif sec_num_line_re.match(line) and len(line) < 100:
                    m = sec_num_line_re.match(line)
                    t = f"{m.group(1)} {m.group(3).strip()}"
                    if t not in seen:
                        seen.add(t)
                        sections.append({"titulo": t, "nivel": max(1, min(m.group(1).count(".") + 1, 3)), "pagina": pno + 1})

        return sections

    def _extract_markdown_structure(self, file_bytes: bytes) -> list[dict]:
        """Extrae encabezados Markdown (# Título, ## Subtítulo)."""
        try:
            texto = file_bytes.decode("utf-8", errors="replace")
        except Exception:
            return []

        heading_re = re.compile(r"^(#{1,6})\s+(.+)$")
        sections: list[dict] = []
        for line in texto.splitlines():
            m = heading_re.match(line.strip())
            if m:
                lvl = len(m.group(1))
                t = m.group(2).strip()
                if t:
                    sections.append({"titulo": t, "nivel": lvl, "pagina": None})
        return sections

    def _extract_txt_structure(self, file_bytes: bytes) -> list[dict]:
        """Extrae encabezados de texto plano."""
        try:
            texto = file_bytes.decode("utf-8", errors="replace")
        except Exception:
            return []

        chap_re = re.compile(
            r"^(?:cap[íi]tulo|m[óo]dulo|unidad|\d+(\.\d+)+)\s+([A-ZÁÉÍÓÚÑ].*)",
            re.IGNORECASE,
        )
        sections: list[dict] = []
        for line in texto.splitlines():
            line_s = line.strip()
            if chap_re.match(line_s) and len(line_s) < 100:
                sections.append({"titulo": line_s, "nivel": 1, "pagina": None})
        return sections

