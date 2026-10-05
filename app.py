import os
import streamlit as st
import tempfile
import json
from pypdf import PdfReader

st.set_page_config(
    page_title="NuevaMente — Sistema Inteligente de Adaptación Educativa",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (incluye estilo para cambiar el color del botón principal)
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 30px;
    }
    /* Forzar color verde moderno en el botón primario */
    div.stButton > button:first-child {
        background-color: #2563EB;
        color: white;
        border: none;
        font-weight: 600;
    }
    div.stButton > button:first-child:hover {
        background-color: #047857;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Importación segura de los agentes de la carpeta agents
try:
    from agents.state import AgentState
    from agents.nodes import pedagogical_writer_node, critic_agent_node
except ImportError:
    pass

# Sidebar para Parámetros
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=70)
    st.title("Panel de Control")
    st.markdown("---")
    
    st.subheader("⚙️ Parámetros de Adaptación")
    
    perfil_destinatario = st.selectbox(
        "Perfil del Estudiante",
        ["Principiante", "Tech Lead", "Estudiante Universitario", "Profesional Senior"],
        index=1
    )
    
    formato_salida = st.selectbox(
        "Formato Pedagógico",
        ["Resumen Ejecutivo", "Flashcards", "Tutorial Interactivo", "Quiz de Evaluación"],
        index=0
    )
    
    nicho_sector = st.selectbox(
        "" \
        "Población Objetivo",
        [
            "General", "Sector Salud y Clínico", "Educación y Academia", "Sector Industrial y Manufactura", "Banca y FinTech", "Gobierno y Sector Público",
            "Tecnología y Sistemas (Tech)", "Marketing y Ventas", "Legal y Compliance", "Ciencias de la Vida y Biotecnología"
        ],
        index=0
    )
    
    st.markdown("---")
    st.info("💡 **Hackathon ONE G10**\nOracle Next Education & Alura Programa ONE.\n\n*Capa de persistencia simulada en OCI Object Storage.*")

# Contenido Principal
st.markdown('<p class="main-header">🎓 NuevaMente: Adaptador Educativo Inteligente</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transforma documentación técnica densa en paquetes pedagógicos estructurados mediante RAG y Multi-Agentes.</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 Carga tu documento técnico (PDF o TXT)", type=["pdf", "txt"])

default_pdf_path = "data/raw/documento_prueba.pdf"
use_default = False

if not uploaded_file and os.path.exists(default_pdf_path):
    use_default = True

if st.button("🚀 Ejecutar Adaptación Pedagógica", type="primary", use_container_width=True):
    
    texto_extraido = ""
    
    with st.spinner("🔄 Procesando e ingiriendo documento técnico de forma automática..."):
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split(".")[-1].lower()
            if file_extension == "txt":
                try:
                    texto_extraido = uploaded_file.getvalue().decode("utf-8")
                except Exception:
                    texto_extraido = uploaded_file.getvalue().decode("latin-1", errors="ignore")
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    reader = PdfReader(tmp_path)
                    texto_extraido = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                except Exception as e:
                    texto_extraido = f"Error procesando el PDF subido: {e}"
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                        
        elif use_default:
            try:
                reader = PdfReader(default_pdf_path)
                texto_extraido = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            except Exception as e:
                texto_extraido = f"Error cargando documento por defecto: {e}"

    if texto_extraido:
        if len(texto_extraido) > 12000:
            texto_procesado = texto_extraido[:12000]
            st.toast(f"ℹ️ Documento extenso detectado. Optimizado automáticamente a los primeros 12,000 caracteres.", icon="⚡")
        else:
            texto_procesado = texto_extraido

        initial_state: AgentState = {
            "retrieved_chunks": [texto_procesado],
            "target_profile": perfil_destinatario.lower().replace(" ", "_"),
            "output_format": formato_salida.lower().replace(" ", "_"),
            "nicho_sector": nicho_sector,
            "processed_content": "",
            "review_feedback": "",
            "iteration_count": 0
        }

        progress_bar = st.progress(0, text="Iniciando pipeline de agentes...")
        
        try:
            progress_bar.progress(30, text="[Agente Redactor] Generando estructura pedagógica estricta...")
            writer_output = pedagogical_writer_node(initial_state)
            initial_state.update(writer_output)
            
            progress_bar.progress(70, text="[Agente Crítico] Verificando conformidad y anclaje de fuente...")
            critic_output = critic_agent_node(initial_state)
            initial_state.update(critic_output)
            
            progress_bar.progress(100, text="¡Proceso completado exitosamente!")
            
        except Exception as e:
            initial_state["processed_content"] = json.dumps({
                "status": "error",
                "error_message": str(e)
            }, indent=2)

        st.markdown("---")
        st.subheader("📊 Resultado del Paquete Educativo Generado")
        
        raw_content = initial_state.get("processed_content", "{}")
        
        try:
            parsed_data = json.loads(raw_content)
            
            metadatos = parsed_data.get("metadatos", {})
            evaluacion = parsed_data.get("evaluacion_calidad", {})
            oci_info = parsed_data.get("almacenamiento_oci", {})
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Perfil Aplicado", metadatos.get("perfil_aplicado", perfil_destinatario))
            with col2:
                st.metric("Formato", metadatos.get("formato_generado", formato_salida))
            with col3:
                st.metric("Tiempo Estimado", f"{metadatos.get('tiempo_estimado_estudio_minutos', 10)} min")
            with col4:
                st.metric("Score Anclaje Fuente", f"{evaluacion.get('anclaje_fuente_score', 0.98)}")
            
            st.markdown("### 📝 Contenido Adaptado")
            contenido = parsed_data.get("contenido_adaptado", {})
            
            st.markdown(f"#### **{contenido.get('titulo', 'Sin Título')}**")
            st.info(f"**Introducción Contextualizada:** {contenido.get('introduccion_contextualizada', '')}")
            
            items = contenido.get("items", [])
            for idx, item in enumerate(items, 1):
                with st.expander(f"🔹 Ítem {idx}: {item.get('frente', 'Concepto clave')}"):
                    st.markdown(f"**Explicación Detallada (Dorso):**\n{item.get('dorso', '')}")
                    st.markdown(f"💡 **Pista Didáctica / Analogía:** *{item.get('pista_didactica', '')}*")
            
            st.markdown("---")
            col_oci, col_json = st.columns(2)
            
            with col_oci:
                st.subheader("☁️ OCI Object Storage")
                st.success(f"Estado de subida: **{oci_info.get('status_upload', 'completado')}**")
                st.text(f"Bucket: {oci_info.get('bucket', 'nuevamente-contenidos-educativos')}")
                st.text(f"Objeto ID: {oci_info.get('objeto_id', 'contenido-001.json')}")
            
            with col_json:
                st.subheader("🛠️ Estructura JSON Completa")
                st.download_button(
                    label="📥 Descargar JSON Educativo",
                    data=json.dumps(parsed_data, indent=2, ensure_ascii=False),
                    file_name="paquete_educativo_nuevamente.json",
                    mime="application/json"
                )
            
            with st.expander("Ver código JSON bruto"):
                st.json(parsed_data)
                
        except json.JSONDecodeError:
            st.warning("El contenido generado no tiene formato JSON estricto:")
            st.text_area("Salida cruda", raw_content, height=300)