import os
import streamlit as st

# Configuración inicial de la página del motor educativo
st.set_page_config(
    page_title="NuevaMente - Motor Educativo", page_icon="🧠", layout="wide"
)

# --- ESTILOS VISUALES Y DISEÑO DE INTERFAZ ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');

    html, body, [class*="st"] {
        font-family: 'Montserrat', sans-serif;
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

    /* --- COMPONENTE DE CARGA DE ARCHIVOS --- */
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
""",
    unsafe_allow_html=True,
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

archivo_subido = st.sidebar.file_uploader(
    "📁 Sube tu archivo", type=["pdf", "txt", "md"]
)
st.sidebar.markdown(
    "<p style='font-size: 0.75rem; color: #94a3b8; margin-top: -5px;'>Máx. 200MB"
    " • PDF, TXT, MD</p>",
    unsafe_allow_html=True,
)

perfil = st.sidebar.selectbox(
    "Perfil del destinatario:",
    [
        "Principiante / Transición",
        "Desarrollador Junior",
        "Líder Técnico / Arquitecto",
        "Público General",
    ],
)

formato = st.sidebar.selectbox(
    "Formato de salida:",
    [
        "Flashcards Interactivas",
        "Quiz con Justificaciones",
        "Guía Práctica Paso a Paso",
    ],
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

st.sidebar.markdown(
    "<div style='font-size: 0.8rem; color: #94a3b8; margin-bottom: 8px;'>💡"
    " <b>Procesar con IA:</b> Analiza el archivo y genera el contenido"
    " adaptado según el perfil y formato seleccionados.</div>",
    unsafe_allow_html=True,
)

generar_btn = st.sidebar.button("✨ Procesar con IA")

# --- FLUJO PRINCIPAL DE PROCESAMIENTO ---
if generar_btn:
  if archivo_subido is not None:
    with st.spinner(
        "⚡ El motor de IA está procesando y estructurando el documento..."
    ):
      st.success("¡Documento analizado y adaptado exitosamente!")

      st.markdown("### 📚 Resultados Generados")
      st.markdown(
          """
            <div class="resultado-card">
                <h3 style="color: #38bdf8; margin-top: 0;">💡 Concepto Clave Extraído</h3>
                <p><b>Explicación adaptada al perfil seleccionado:</b> Aquí se presentarán los conceptos desglosados con el nivel de complejidad adecuado, listos para su estudio o divulgación.</p>
                <hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>
                <p style="color: #fde047; margin-bottom: 0; font-size: 0.95rem;">🎯 <b>Pista del Tutor Inteligente:</b> Conecta este concepto con la arquitectura general del sistema para afianzar el aprendizaje.</p>
            </div>
            """,
          unsafe_allow_html=True,
      )
  else:
    st.error(
        "⚠️ Por favor, sube un documento técnico en la barra lateral para"
        " iniciar el procesamiento."
    )
else:
  st.markdown(
      """
        <div class="info-box">
            <b>👋 ¡Bienvenida a NuevaMente!</b><br>
            Despliega o utiliza la barra lateral izquierda para subir el archivo, configurar el perfil de aprendizaje y hacer clic en <b>Procesar con IA</b> para comenzar.
        </div>
        """,
      unsafe_allow_html=True,
  )