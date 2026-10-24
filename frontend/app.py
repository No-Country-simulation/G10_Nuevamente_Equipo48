import json
import os
import requests

try:
    import streamlit as st
except ImportError:
    st = None

# --- CONFIGURACIÓN DE CONEXIÓN CON EL BACKEND FASTAPI ---
API_BASE_URL = (
    os.getenv("API_BASE_URL") or os.getenv("BACKEND_URL") or "http://localhost:8000"
)
TIMEOUT_UPLOAD_SECONDS = 60
TIMEOUT_ADAPTACION_SECONDS = 360

# Mapeos de opciones visuales a los contratos y Enums exactos de FastAPI
class _PerfilOptionsDict(dict):
    _LEGACY_ALIASES = {
        "Principiante / Transición": "Principiante / Básico",
        "Desarrollador Junior": "Intermedio / Junior",
        "Líder Técnico / Arquitecto": "Avanzado / Especialista",
        "Público General / Ejecutivo": "Público General / Directivo",
    }

    def __getitem__(self, key):
        if key not in self and key in self._LEGACY_ALIASES:
            return self[self._LEGACY_ALIASES[key]]
        return super().__getitem__(key)


PERFIL_OPTIONS = _PerfilOptionsDict({
    "Principiante / Básico": "principiante",
    "Intermedio / Junior": "junior",
    "Avanzado / Especialista": "lider_tecnico",
    "Público General / Directivo": "ejecutivo",
})

CAMPO_OPTIONS = [
    "🌐 Todos los campos",
    "💻 Desarrollo de Software y Datos",
    "🛡️ Infraestructura, Redes y Seguridad",
    "⚙️ Ingeniería y Tecnologías Aplicadas",
    "🔬 Ciencias Básicas y Energía",
]

DOMINIO_A_CAMPO = {
    # 💻 Desarrollo de Software y Datos
    "Bases de datos": "💻 Desarrollo de Software y Datos",
    "Programación": "💻 Desarrollo de Software y Datos",
    "Estructuras de datos / sistemas": "💻 Desarrollo de Software y Datos",
    "Gráficos por computador": "💻 Desarrollo de Software y Datos",
    "Cloud / Desarrollo móvil": "💻 Desarrollo de Software y Datos",
    # 🛡️ Infraestructura, Redes y Seguridad
    "Redes": "🛡️ Infraestructura, Redes y Seguridad",
    "Ciberseguridad": "🛡️ Infraestructura, Redes y Seguridad",
    "Tecnología / sistemas": "🛡️ Infraestructura, Redes y Seguridad",
    "Rendimiento / sistemas": "🛡️ Infraestructura, Redes y Seguridad",
    # ⚙️ Ingeniería y Tecnologías Aplicadas
    "Electrónica": "⚙️ Ingeniería y Tecnologías Aplicadas",
    "Ingeniería / confiabilidad": "⚙️ Ingeniería y Tecnologías Aplicadas",
    "Ingeniería industrial": "⚙️ Ingeniería y Tecnologías Aplicadas",
    "GIS / Geoespacial": "⚙️ Ingeniería y Tecnologías Aplicadas",
    "IoT / Microcontroladores": "⚙️ Ingeniería y Tecnologías Aplicadas",
    "Robótica": "⚙️ Ingeniería y Tecnologías Aplicadas",
    # 🔬 Ciencias Básicas y Energía
    "Energía / Física aplicada": "🔬 Ciencias Básicas y Energía",
    "Energía renovable": "🔬 Ciencias Básicas y Energía",
    "Química": "🔬 Ciencias Básicas y Energía",
    "Física": "🔬 Ciencias Básicas y Energía",
}


FORMATO_OPTIONS = {
    "Tutorial Paso a Paso": "tutorial",
    "Flashcards Interactivas": "flashcards",
    "Quiz con Justificaciones": "quiz",
    "Resumen Ejecutivo": "resumen_ejecutivo",
    "Guión de Clase": "guion_clase",
}

NICHO_OPTIONS = {
    "General / Transversal": "general",
    "FinTech y Banca Digital": "fintech",
    "Salud y Tecnologías Médicas": "salud",
    "E-Commerce y Retail": "ecommerce",
}

NIVEL_OPTIONS = {
    "Didáctico (Fundamentos y conceptos)": "didactico",
    "Intermedio (Práctico y contextualizado)": "intermedio",
    "Técnico (Avanzado y exhaustivo)": "tecnico",
}


# --- FUNCIONES DE CLIENTE HTTP Y COMUNICACIÓN CON FASTAPI ---

def extract_error_message(response: requests.Response) -> str:
    """Extrae un mensaje de error legible del cuerpo de respuesta HTTP."""
    try:
        body = response.json()
        detail = body.get("detail")
        if isinstance(detail, dict):
            err = detail.get("error", "")
            det = detail.get("detalle", "")
            if err and det:
                return f"{err} ({det})"
            return err or det or str(detail)
        elif isinstance(detail, list):
            msgs = []
            for item in detail:
                if isinstance(item, dict):
                    loc = " -> ".join(str(x) for x in item.get("loc", []))
                    msg = item.get("msg", "")
                    msgs.append(f"{loc}: {msg}")
            return "; ".join(msgs) if msgs else str(detail)
        elif detail:
            return str(detail)
        elif "error" in body:
            return str(body["error"])
        return response.text or f"Código de error HTTP {response.status_code}"
    except Exception:
        return response.text or f"Código de error HTTP {response.status_code}"


def upload_file_to_backend(
    base_url: str,
    filename: str,
    file_bytes: bytes,
    mime_type: str | None = None,
    timeout: int = TIMEOUT_UPLOAD_SECONDS,
) -> dict:
    """
    Envía el archivo seleccionado a POST /api/v1/files/upload de FastAPI.
    Retorna el diccionario con la respuesta (documento_id, chunks_indexados, etc.).
    """
    url = f"{base_url.rstrip('/')}/api/v1/files/upload"

    if not mime_type or mime_type == "application/octet-stream":
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        mime_map = {
            "pdf": "application/pdf",
            "md": "text/markdown",
            "txt": "text/plain",
        }
        mime_type = mime_map.get(ext, "application/octet-stream")

    files = {
        "file": (filename, file_bytes, mime_type)
    }

    response = requests.post(url, files=files, timeout=timeout)
    if not response.ok:
        error_msg = extract_error_message(response)
        raise requests.exceptions.HTTPError(
            f"Fallo en la carga del archivo ({response.status_code}): {error_msg}",
            response=response,
        )
    return response.json()


def fetch_corpus_documents(base_url: str, timeout: int = 10) -> list[dict]:
    """
    Obtiene la lista consolidada de documentos del corpus desde GET /api/v1/files/corpus,
    con fallback automático al inventario CSV si el endpoint no responde.
    """
    url = f"{base_url.rstrip('/')}/api/v1/files/corpus"
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.ok:
            data = resp.json()
            if data:
                return data
    except Exception:
        pass

    # Fallback al archivo CSV de inventario de Data Analytics
    import csv
    from pathlib import Path
    csv_candidates = [
        Path("data_analyst/inventario/inventario_corpus.csv"),
        Path("../data_analyst/inventario/inventario_corpus.csv"),
        Path(__file__).resolve().parent.parent / "data_analyst" / "inventario" / "inventario_corpus.csv",
    ]
    for c in csv_candidates:
        if c.is_file():
            try:
                with open(c, encoding="utf-8-sig") as f:
                    rows = list(csv.DictReader(f))
                    return [
                        {
                            "identificador_documento": r.get("identificador_documento", "").strip(),
                            "titulo": r.get("titulo", "").strip(),
                            "dominio": r.get("dominio", "General").strip(),
                            "tema": r.get("tema", "").strip(),
                            "descripcion": r.get("descripcion", "").strip(),
                            "resultado_evaluacion": r.get("resultado_evaluacion", "APTO").strip(),
                            "licencia": r.get("licencia", "").strip(),
                            "fuente": r.get("fuente", "").strip(),
                            "archivo_disponible": True,
                            "esta_procesado": False,
                            "chunks_indexados": 0,
                            "estado_flujo": "DISPONIBLE_APTO",
                        }
                        for r in rows
                        if r.get("identificador_documento")
                    ]
            except Exception:
                pass
    return []


def ingest_corpus_document(base_url: str, documento_id: str, timeout: int = 30) -> dict:
    """
    Solicita la ingesta bajo demanda de un documento del corpus a POST /api/v1/files/corpus/{id}/ingest.
    """
    url = f"{base_url.rstrip('/')}/api/v1/files/corpus/{documento_id}/ingest"
    resp = requests.post(url, timeout=timeout)
    if not resp.ok:
        error_msg = extract_error_message(resp)
        raise requests.exceptions.HTTPError(
            f"Fallo al indexar documento del corpus ({resp.status_code}): {error_msg}",
            response=resp,
        )
    return resp.json()


def request_adaptation(
    base_url: str,
    documento_id: str | None = None,
    perfil: str = "principiante",
    formato: str = "tutorial",
    nicho: str = "general",
    nivel: str = "didactico",
    documento_ids: list[str] | None = None,
    tema_o_pregunta: str | None = None,
    timeout: int = TIMEOUT_ADAPTACION_SECONDS,
) -> dict:
    """
    Envía la solicitud de adaptación pedagógica a POST /api/v1/adaptacion.
    Soporta modo singular (documento_id), multi-documento (documento_ids) y tema/pregunta orientadora.
    Retorna el diccionario con la respuesta estructurada completa.
    """
    url = f"{base_url.rstrip('/')}/api/v1/adaptacion"
    payload = {
        "perfil_destinatario": perfil,
        "formato_salida": formato,
        "nicho": nicho,
        "nivel_detalle": nivel,
    }
    if documento_ids is not None:
        payload["documento_ids"] = documento_ids
    if documento_id is not None:
        payload["documento_id"] = documento_id
    if tema_o_pregunta and tema_o_pregunta.strip():
        payload["tema_o_pregunta"] = tema_o_pregunta.strip()

    response = requests.post(url, json=payload, timeout=timeout)
    if not response.ok:
        error_msg = extract_error_message(response)
        raise requests.exceptions.HTTPError(
            f"Fallo en la adaptación pedagógica ({response.status_code}): {error_msg}",
            response=response,
        )
    return response.json()


# --- INTERFAZ STREAMLIT ---

def main() -> None:
    if st is None:
        raise RuntimeError(
            "Streamlit no se encuentra instalado en este intérprete. "
            "Ejecuta la app con un entorno que tenga Streamlit (ej: py -3.12 -m streamlit run frontend/app.py)."
        )

    st.set_page_config(
        page_title="NuevaMente - Motor Educativo", page_icon="🧠", layout="wide"
    )

    # --- ESTILOS VISUALES Y DISEÑO DE INTERFAZ ---
    st.html(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');

        html, body, [class*="st"]:not([class*="material-icons"]):not([data-testid*="Icon"]) {
            font-family: 'Montserrat', sans-serif;
        }

        /* Proteger los iconos nativos de Streamlit para que rendericen flechas en vez de texto montado */
        [data-testid="stExpanderToggleIcon"],
        [data-testid="stIconMaterial"],
        .material-symbols-rounded,
        .material-symbols-sharp,
        .material-symbols-outlined,
        .material-icons,
        span:has(> svg) {
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        }

        /* Fondo principal general oscuro para toda la app */
        .stApp {
            background-color: #05070c;
            color: #f1f5f9;
        }
        
        /* Barra lateral colapsable (Panel de control del sistema) */
        [data-testid="stSidebar"] {
            background-color: rgba(9, 11, 16, 0.98);
            border-right: 1px solid rgba(0, 242, 255, 0.2);
        }
        
        /* Contenedor de la pantalla principal */
        .main .block-container {
            background-image: linear-gradient(to bottom, rgba(5, 7, 12, 0.75), rgba(5, 7, 12, 0.95)), url('fondo.jpg');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            padding: 3rem 2.5rem;
            border-radius: 20px;
            border: 1px solid rgba(0, 210, 255, 0.2);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }

        /* Título principal */
        .titulo-principal {
            font-size: 3.8rem !important;
            font-weight: 900 !important;
            background: linear-gradient(135deg, #ffffff 0%, #38bdf8 50%, #fde047 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.0;
            margin-bottom: 8px;
            letter-spacing: -1.5px;
            text-transform: uppercase;
        }
        
        /* Subtítulo descriptivo */
        .subtitulo-principal {
            color: #cbd5e1;
            font-size: 1.05rem;
            font-weight: 400;
            margin-top: 0;
        }

        /* Textos y etiquetas del panel lateral */
        [data-testid="stSidebar"] h2 {
            color: #38bdf8 !important;
            font-weight: 800;
        }
        
        [data-testid="stSidebar"] label {
            color: #e2e8f0 !important;
            font-weight: 600;
        }

        /* Selectores y cajas desplegables del panel lateral */
        .stSelectbox > div > div {
            background-color: #11141d !important;
            border: 1px solid #1e293b !important;
            border-radius: 10px !important;
            color: #ffffff !important;
        }

        /* Componente de carga de archivos */
        [data-testid="stFileUploader"] {
            background-color: transparent !important;
        }
        
        [data-testid="stFileUploader"] section {
            background-color: #11141d !important;
            border: 1px solid #1e293b !important;
            border-radius: 10px !important;
            padding: 10px !important;
            box-shadow: none !important;
        }

        [data-testid="stFileUploader"] section div.uploadedFile {
            color: #ffffff !important;
        }

        [data-testid="stFileUploader"] section button {
            background-color: #1e293b !important;
            color: #38bdf8 !important;
            border-radius: 8px !important;
            border: 1px solid #334155 !important;
            font-weight: 700 !important;
            width: 100% !important;
        }
        [data-testid="stFileUploader"] section button:hover {
            background-color: #334155 !important;
            border-color: #38bdf8 !important;
            color: #ffffff !important;
        }

        /* Botón de ejecución principal */
        .stButton>button {
            background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%);
            color: #ffffff;
            border-radius: 12px;
            border: none;
            font-weight: 800;
            padding: 0.85rem 1.2rem;
            box-shadow: 0 4px 20px rgba(6, 182, 212, 0.35);
            transition: all 0.3s ease;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(2, 132, 199, 0.5);
        }
        
        /* Tarjetas de resultados y contenedores informativos */
        .resultado-card {
            background: rgba(17, 20, 29, 0.85);
            backdrop-filter: blur(16px);
            padding: 28px;
            border-radius: 18px;
            border: 1px solid rgba(56, 189, 248, 0.3);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            margin-bottom: 24px;
        }
        
        .info-box {
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(10px);
            border-left: 4px solid #38bdf8;
            padding: 22px;
            border-radius: 0 12px 12px 0;
            color: #cbd5e1;
            margin-top: 20px;
        }
        </style>
        """
    )

    # --- GESTIÓN DE RECURSOS (LOGOTIPO) ---
    logo_path = "logo.jpg"
    if not os.path.exists(logo_path):
        if os.path.exists("logo.png"):
            logo_path = "logo.png"

    # --- ENCABEZADO DE LA APLICACIÓN ---
    col_img, col_txt = st.columns([1, 4.5])

    with col_img:
        if os.path.exists(logo_path):
            st.image(logo_path, width=160)
        else:
            st.markdown(
                "<div style='font-size: 3rem; text-align: center;'>🤖🧠</div>",
                unsafe_allow_html=True,
            )

    with col_txt:
        st.markdown(
            '<p class="titulo-principal">NuevaMente</p>', unsafe_allow_html=True
        )
        st.markdown(
            '<p class="subtitulo-principal">Motor Educativo Inteligente para'
            " transformar documentación técnica en experiencias de aprendizaje"
            " personalizadas y dinámicas.</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<hr style='border-color: rgba(56, 189, 248, 0.2); margin: 25px 0;'>",
        unsafe_allow_html=True,
    )

    # --- PANEL DE CONTROL LATERAL ---
    st.sidebar.markdown("## ⚙️ Panel de Control")
    st.sidebar.markdown(
        "<p style='font-size: 0.85rem; color: #94a3b8;'>Configura los parámetros"
        " de transformación para el documento.</p>",
        unsafe_allow_html=True,
    )

    # ── Modo de origen del documento ──────────────────────────────────────────
    modo_origen = st.sidebar.radio(
        "Origen del documento:",
        ["📚 Catálogo del Corpus", "📁 Cargar Archivo Nuevo"],
        index=0,
        help="Elige si quieres trabajar con documentos ya indexados o subir uno nuevo.",
    )

    selected_corpus_ids: list[str] = []
    archivo_subido = None

    if modo_origen == "📚 Catálogo del Corpus":
        corpus_docs = fetch_corpus_documents(API_BASE_URL)
        if corpus_docs:
            # 1. Seleccionar el campo de aplicación
            campo_aplicacion = st.sidebar.selectbox(
                "🎯 1. Campo de aplicación:",
                options=CAMPO_OPTIONS,
                index=0,
                help="Filtra el catálogo documental según el campo de aplicación de interés.",
            )

            # Filtrar documentos por campo de aplicación seleccionado
            if campo_aplicacion != "🌐 Todos los campos":
                docs_filtrados = [
                    d
                    for d in corpus_docs
                    if DOMINIO_A_CAMPO.get(d.get("dominio")) == campo_aplicacion
                ]
            else:
                docs_filtrados = corpus_docs

            # 2. Mostrar el catálogo documental existente
            corpus_options = {}
            for i, doc in enumerate(docs_filtrados):
                doc_id = (
                    doc.get("identificador_documento")
                    or doc.get("documento_id")
                    or doc.get("id")
                    or f"doc_{i}"
                )
                doc_title = doc.get("titulo") or doc.get("nombre") or f"Documento {doc_id}"
                eval_status = doc.get("resultado_evaluacion")
                status_tag = f" [{eval_status}]" if eval_status and eval_status != "APTO" else ""
                corpus_options[doc_id] = f"{doc_id} — {doc_title}{status_tag}"

            # 3. Seleccionar entre uno y tres documentos
            selected_labels = st.sidebar.multiselect(
                "📑 2. Catálogo (selecciona 1 a 3 docs):",
                options=list(corpus_options.keys()),
                format_func=lambda k: f"📄 {corpus_options[k]}",
                max_selections=3,
                help="Elige de 1 a 3 documentos base del catálogo para el estudio focalizado.",
            )
            selected_corpus_ids = selected_labels

            # 4. Mostrar temas derivados del contenido real de los documentos seleccionados
            temas_derivados = []
            for doc in corpus_docs:
                d_id = doc.get("identificador_documento") or doc.get("documento_id")
                if d_id in selected_corpus_ids:
                    t_val = (doc.get("tema") or "").strip()
                    if t_val and t_val not in temas_derivados:
                        temas_derivados.append(t_val)

            # 5. Elegir el tema orientador (extraído de los documentos seleccionados)
            tema_input = (
                st.sidebar.selectbox(
                    "💡 3. Tema disponible:",
                    options=temas_derivados,
                    help="Tema orientador extraído de los documentos seleccionados.",
                )
                or ""
            )
        else:
            st.sidebar.info(
                "ℹ️ No se encontraron documentos en el catálogo del corpus. "
                "Verifica que el backend esté corriendo o cambia a 'Cargar Archivo Nuevo'."
            )
            tema_input = ""
    else:
        archivo_subido = st.sidebar.file_uploader(
            "📁 Sube tu archivo", type=["pdf", "txt", "md"]
        )
        st.sidebar.markdown(
            "<p style='font-size: 0.75rem; color: #94a3b8; margin-top: -5px;'>Máx. 50MB"
            " • PDF, TXT, MD</p>",
            unsafe_allow_html=True,
        )
        st.sidebar.markdown(
            "<p style='font-size: 0.8rem; color: #94a3b8; margin-top: 12px; margin-bottom: 2px;'>"
            "📝 <b>Tema o pregunta orientadora</b> <i>(opcional)</i></p>",
            unsafe_allow_html=True,
        )
        tema_input = st.sidebar.text_area(
            label="tema_o_pregunta_hidden",
            label_visibility="collapsed",
            placeholder="Ej: ¿Cómo funciona la autenticación JWT? / Explica el ciclo de vida de una petición HTTP.",
            max_chars=500,
            help="Especifica el tema o pregunta que quieres que oriente el contenido generado. "
                 "El motor RAG priorizará fragmentos relacionados con este enfoque.",
        )

    # ── Parámetros pedagógicos ────────────────────────────────────────────────
    st.sidebar.markdown(
        "<hr style='border-color: rgba(56, 189, 248, 0.15); margin: 10px 0;'>",
        unsafe_allow_html=True,
    )

    perfil_label = st.sidebar.selectbox(
        "Perfil del destinatario:",
        list(PERFIL_OPTIONS.keys()),
    )

    formato_label = st.sidebar.selectbox(
        "Formato de salida:",
        list(FORMATO_OPTIONS.keys()),
    )

    nivel_label = st.sidebar.selectbox(
        "Nivel de profundidad:",
        list(NIVEL_OPTIONS.keys()),
    )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown(
        f"<div style='font-size: 0.75rem; color: #64748b; margin-bottom: 8px;'>"
        f"🔗 Backend API: <code>{API_BASE_URL}</code></div>",
        unsafe_allow_html=True,
    )

    generar_btn = st.sidebar.button("✨ Procesar con IA")

    # Normalizar tema: None si está vacío
    tema_limpio: str | None = tema_input.strip() if tema_input and tema_input.strip() else None

    # --- FLUJO PRINCIPAL DE PROCESAMIENTO E INTEGRACIÓN CON FASTAPI ---
    if generar_btn:
        # ── Validar tema orientador ───────────────────────────────────────────
        if tema_limpio and len(tema_limpio) > 500:
            st.error("⚠️ El tema o pregunta orientadora no puede exceder los 500 caracteres.")
            st.stop()

        # ── Validaciones según modo ───────────────────────────────────────────
        if modo_origen == "📚 Catálogo del Corpus":
            if not selected_corpus_ids:
                st.error(
                    "⚠️ Selecciona al menos un documento del catálogo del corpus para iniciar el procesamiento."
                )
                st.stop()
            if len(selected_corpus_ids) > 3:
                st.error("⚠️ Puedes seleccionar un máximo de 3 documentos del corpus.")
                st.stop()
        else:
            if archivo_subido is None:
                st.error(
                    "⚠️ Por favor, sube un documento técnico (.pdf, .txt o .md) en la barra lateral para"
                    " iniciar el procesamiento."
                )
                st.stop()
            file_bytes = archivo_subido.getvalue()
            file_name = archivo_subido.name
            if len(file_bytes) > 50 * 1024 * 1024:
                st.error(
                    f"⚠️ El archivo '{file_name}' excede el límite máximo permitido de 50 MB "
                    f"({len(file_bytes) / (1024 * 1024):.2f} MB)."
                )
                st.stop()
            if len(file_bytes) == 0:
                st.error(f"⚠️ El archivo '{file_name}' está vacío. Por favor selecciona un documento válido.")
                st.stop()

        try:
            adapt_res: dict = {}
            doc_ids_usados: list[str] = []

            if modo_origen == "📚 Catálogo del Corpus":
                # ── Caso Corpus: indexar bajo demanda y enviar multi-doc ────────
                total = len(selected_corpus_ids)
                with st.spinner(f"📚 Indexando {total} documento(s) del corpus en FAISS..."):
                    for doc_id in selected_corpus_ids:
                        try:
                            ingest_corpus_document(API_BASE_URL, doc_id)
                        except requests.exceptions.HTTPError as exc_ing:
                            st.warning(
                                f"⚠️ No se pudo indexar el documento `{doc_id}`: {exc_ing}. "
                                "Se intentará usar los fragmentos ya disponibles en el índice."
                            )
                doc_ids_usados = selected_corpus_ids
                st.toast(
                    f"✅ {total} documento(s) del corpus listos para el pipeline RAG",
                    icon="📚",
                )

                with st.spinner("🧠 Orquestando pipeline RAG multi-documento y generando contenido adaptado..."):
                    adapt_res = request_adaptation(
                        base_url=API_BASE_URL,
                        documento_ids=doc_ids_usados,
                        perfil=PERFIL_OPTIONS[perfil_label],
                        formato=FORMATO_OPTIONS[formato_label],
                        nicho="general",
                        nivel=NIVEL_OPTIONS[nivel_label],
                        tema_o_pregunta=tema_limpio,
                    )
            else:
                # ── Caso Upload: subir archivo y enviar un solo doc ─────────────
                with st.spinner("📤 Paso 1/2: Subiendo archivo e indexando fragmentos en FAISS..."):
                    upload_res = upload_file_to_backend(
                        base_url=API_BASE_URL,
                        filename=file_name,
                        file_bytes=file_bytes,
                        mime_type=archivo_subido.type,
                    )

                documento_id = upload_res.get("documento_id")
                chunks_indexados = upload_res.get("chunks_indexados", 0)
                doc_ids_usados = [documento_id] if documento_id else []
                st.toast(f"✅ Ingesta completada ({chunks_indexados} fragmentos indexados)", icon="📦")

                with st.spinner("🧠 Paso 2/2: Orquestando pipeline RAG y generando contenido adaptado..."):
                    adapt_res = request_adaptation(
                        base_url=API_BASE_URL,
                        documento_id=documento_id,
                        perfil=PERFIL_OPTIONS[perfil_label],
                        formato=FORMATO_OPTIONS[formato_label],
                        nicho="general",
                        nivel=NIVEL_OPTIONS[nivel_label],
                        tema_o_pregunta=tema_limpio,
                    )

            st.success("🎉 ¡Documento procesado y adaptado exitosamente por el motor NuevaMente!")

            # --- RENDERIZADO DE RESULTADOS REALES ---
            metadatos = adapt_res.get("metadatos", {})
            evaluacion = adapt_res.get("evaluacion_calidad", {})
            contenido = adapt_res.get("contenido_adaptado")
            fuentes = adapt_res.get("fuentes", [])
            oci_info = adapt_res.get("almacenamiento_oci", {})
            es_multidoc = len(doc_ids_usados) > 1

            st.markdown("### 📊 Métricas Pedagógicas y Evaluación")

            # Badge de tema orientador (si se ingresó)
            if tema_limpio:
                st.markdown(
                    f"<div style='background: rgba(56,189,248,0.12); border-left: 3px solid #38bdf8; "
                    f"padding: 8px 14px; border-radius: 6px; margin-bottom: 12px; font-size: 0.9rem;'>"
                    f"🎯 <b>Tema orientador:</b> {tema_limpio}</div>",
                    unsafe_allow_html=True,
                )

            # Badge de documentos usados (multi-doc)
            if es_multidoc:
                docs_badge = " · ".join(f"`{d}`" for d in doc_ids_usados)
                st.markdown(
                    f"<div style='background: rgba(99,102,241,0.12); border-left: 3px solid #818cf8; "
                    f"padding: 8px 14px; border-radius: 6px; margin-bottom: 12px; font-size: 0.85rem;'>"
                    f"📚 <b>Documentos combinados ({len(doc_ids_usados)}):</b> {docs_badge}</div>",
                    unsafe_allow_html=True,
                )

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Perfil Aplicado", metadatos.get("perfil_destinatario", perfil_label))
            with c2:
                tiempo_estudio = metadatos.get("tiempo_estimado_estudio_minutos", 10)
                st.metric("Tiempo Estimado", f"{tiempo_estudio} min")
            with c3:
                score = evaluacion.get("anclaje_fuente_score", 0.0)
                confianza = evaluacion.get("nivel_confianza", "N/A")
                st.metric("Fidelidad a Fuentes", f"{score:.2f}", help=f"Nivel de confianza: {confianza}")
            with c4:
                st.metric("Fragmentos Usados", f"{metadatos.get('fragmentos_usados', len(fuentes))}")

            # Conceptos clave identificados
            conceptos_clave = metadatos.get("conceptos_clave", [])
            if conceptos_clave:
                tags = " • ".join(f"`{c}`" for c in conceptos_clave)
                st.markdown(f"**🏷️ Conceptos Clave:** {tags}")

            st.markdown("<hr style='border-color: rgba(56, 189, 248, 0.2); margin: 20px 0;'>", unsafe_allow_html=True)
            st.markdown(f"### 📚 Contenido Adaptado — {formato_label}")

            # Visualización adaptable según el tipo de dato devuelto
            if isinstance(contenido, list):
                st.info(f"Se generaron {len(contenido)} elementos para el formato solicitado:")
                for idx, item in enumerate(contenido, 1):
                    if isinstance(item, dict):
                        titulo_item = (
                            item.get("pregunta")
                            or item.get("frente")
                            or item.get("titulo")
                            or f"Elemento #{idx}"
                        )
                        with st.expander(f"🔹 {titulo_item}", expanded=(idx == 1)):
                            for k, v in item.items():
                                if k not in ("pregunta", "frente", "titulo"):
                                    label = k.replace("_", " ").capitalize()
                                    st.markdown(f"**{label}:** {v}")
                    else:
                        st.markdown(f"- {item}")
            elif isinstance(contenido, dict):
                with st.expander("Estructura estructurada del contenido", expanded=True):
                    st.json(contenido)
            else:
                st.markdown(
                    f"""
                    <div class="resultado-card">
                        <div style="white-space: pre-wrap; font-size: 1rem; line-height: 1.6;">{contenido}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Persistencia OCI y Descarga
            st.markdown("<hr style='border-color: rgba(56, 189, 248, 0.2); margin: 20px 0;'>", unsafe_allow_html=True)
            col_oci, col_dl = st.columns(2)
            # Nombre de archivo para descarga (usa primer doc_id si existe)
            _dl_prefix = doc_ids_usados[0][:8] if doc_ids_usados else "resultado"
            with col_oci:
                st.markdown("#### ☁️ Persistencia OCI")
                status_oci = oci_info.get("status_upload", "no_configurado")
                if status_oci in ("exitoso", "completado"):
                    st.success(f"Estado: **{status_oci}**")
                    if oci_info.get("url_objeto"):
                        st.caption(f"URL: {oci_info.get('url_objeto')}")
                elif status_oci == "no_configurado":
                    st.info("Estado: **no_configurado** (modo degradado local activo)")
                else:
                    st.warning(f"Estado: **{status_oci}** ({oci_info.get('detalle', 'Sin detalle')})")

            with col_dl:
                st.markdown("#### 💾 Exportar Resultado")
                st.download_button(
                    label="📥 Descargar Paquete Educativo (JSON)",
                    data=json.dumps(adapt_res, indent=2, ensure_ascii=False),
                    file_name=f"nuevamente_adaptacion_{_dl_prefix}.json",
                    mime="application/json",
                )

            # Trazabilidad RAG: Fragmentos fuente con origen por documento
            if fuentes:
                titulo_fuentes = (
                    f"🔍 Fragmentos fuente — {len(fuentes)} fragmento(s)"
                    + (f" de {len(doc_ids_usados)} documentos" if es_multidoc else "")
                )
                with st.expander(titulo_fuentes):
                    for frag in fuentes:
                        score_f = frag.get("score_relevancia", 0.0)
                        frag_doc_id = frag.get("documento_id", "")
                        header_parts = [f"**Fragmento #{frag.get('posicion', 0) + 1}**"]
                        if frag_doc_id and es_multidoc:
                            header_parts.append(f"📄 `{frag_doc_id}`")
                        header_parts.append(f"Relevancia: `{score_f:.4f}`")
                        st.markdown(" — ".join(header_parts))
                        st.text(frag.get("texto", ""))
                        st.markdown("---")

            # Inspección técnica de JSON
            with st.expander("🛠️ Ver respuesta JSON bruta de la API"):
                st.json(adapt_res)

        except requests.exceptions.ConnectionError:
            st.error(
                f"🔌 **Error de conexión:** No fue posible conectar con el backend en `{API_BASE_URL}`. "
                "Verifica que el servidor FastAPI esté iniciado en esa dirección y puerto."
            )
        except requests.exceptions.Timeout:
            st.error(
                "⏱️ **Tiempo de espera agotado:** La solicitud excedió el tiempo límite configurado. "
                "Intenta con un fragmento más corto o verifica la carga del servidor."
            )
        except requests.exceptions.HTTPError as exc:
            st.error(f"⚠️ **Error HTTP devuelto por el servidor:** {exc}")
        except Exception as exc:
            st.error(f"❌ **Error inesperado durante la ejecución:** {type(exc).__name__}: {exc}")

    else:
        st.markdown(
            """
            <div class="info-box">
                <b>👋 ¡Bienvenida a NuevaMente!</b><br>
                Despliega o utiliza la barra lateral izquierda para elegir el origen del documento
                (catálogo del corpus o archivo nuevo), configurar los parámetros pedagógicos y
                hacer clic en <b>Procesar con IA</b> para comenzar.
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()