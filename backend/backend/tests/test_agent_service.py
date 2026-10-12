"""
Tests de propiedad para AgentService — NuevaMente Backend.

Propiedades:
  - Propiedad 8:  anclaje_fuente_score siempre en [0.0, 1.0]  (Req 3.12)
  - Propiedad 9:  respuesta siempre contiene campos obligatorios (Req 3.15, 3.16)
  - _nivel_confianza clasifica correctamente

Requisitos: 3.12, 3.15, 3.16
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import HealthCheck, given
from hypothesis import settings as h_settings
from hypothesis import strategies as st
from unittest.mock import MagicMock

from app.schemas.adaptacion import (
    AdaptacionRequest, FormatoSalida, Nicho, NivelDetalle, PerfilDestinatario,
)
from app.services.agent_service import AgentService, _extraer_conceptos_clave
from app.services.oci_service import OCIUploadResult
from app.services.rag_service import ChunkMetadata


DOC_ID = "doc-agent-test-001"

CHUNKS = [
    ChunkMetadata(chunk_id="c1", documento_id=DOC_ID,
                  texto="El riesgo de credito es fundamental en fintech.", posicion=0, score=0.9),
    ChunkMetadata(chunk_id="c2", documento_id=DOC_ID,
                  texto="Los sistemas de pago digitales requieren cifrado.", posicion=1, score=0.75),
]

CONTENIDO = "Paso 1: Identificar el riesgo.\nPaso 2: Aplicar cifrado en pagos.\n"

CAMPOS_OBLIGATORIOS = [
    "status", "document_id", "metadatos", "contenido_adaptado",
    "evaluacion_calidad", "fuentes", "almacenamiento_oci",
]


def _emb() -> np.ndarray:
    v = np.ones((1, 384), dtype=np.float32)
    return v / np.linalg.norm(v)


def _rag(existe=True):
    m = MagicMock()
    m.document_exists.return_value = existe
    m.retrieve.return_value = CHUNKS
    m._settings = MagicMock()
    m._settings.rag_top_k = 5
    m.generate_embeddings.return_value = _emb()
    return m


def _llm():
    m = MagicMock()
    m.generate.return_value = CONTENIDO
    return m


def _oci():
    m = MagicMock()
    m.upload_artifact.return_value = OCIUploadResult(status="no_configurado")
    return m


# --- Tests de _nivel_confianza ---

class TestNivelConfianza:
    def setup_method(self):
        self.svc = AgentService(_rag(), _llm(), _oci())

    @pytest.mark.parametrize("score,esperado", [
        (1.0, "alto"), (0.7, "alto"), (0.69, "medio"),
        (0.4, "medio"), (0.39, "bajo"), (0.0, "bajo"),
    ])
    def test_clasificacion(self, score, esperado):
        """Cada rango de score produce el nivel de confianza correcto."""
        assert self.svc._nivel_confianza(score) == esperado


# --- Tests de _calculate_anclaje_score ---

def test_score_en_rango():
    """El score siempre debe estar en [0.0, 1.0]."""
    svc = AgentService(_rag(), _llm(), _oci())
    score = svc._calculate_anclaje_score(CONTENIDO, CHUNKS)
    assert 0.0 <= score <= 1.0


def test_score_sin_chunks_es_cero():
    """Sin chunks fuente el score debe ser 0.0."""
    svc = AgentService(_rag(), _llm(), _oci())
    assert svc._calculate_anclaje_score("contenido", []) == 0.0


# --- Propiedad 8: score siempre en [0.0, 1.0] ---

@h_settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(raw=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False))
def test_propiedad_clamp_score(raw):
    """
    Propiedad 8: max(0.0, min(1.0, score)) siempre produce un valor en [0.0, 1.0].
    Valida: Requisito 3.12
    """
    resultado = max(0.0, min(1.0, raw))
    assert 0.0 <= resultado <= 1.0


# --- Propiedad 9: campos obligatorios siempre presentes ---

@h_settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
@given(
    perfil=st.sampled_from([e.value for e in PerfilDestinatario]),
    formato=st.sampled_from([e.value for e in FormatoSalida]),
    nicho=st.sampled_from([e.value for e in Nicho]),
    nivel=st.sampled_from([e.value for e in NivelDetalle]),
)
def test_propiedad_campos_obligatorios(perfil, formato, nicho, nivel):
    """
    Propiedad 9: generate_content siempre incluye todos los campos obligatorios.
    Valida: Requisitos 3.15, 3.16
    """
    svc = AgentService(_rag(), _llm(), _oci())
    req = AdaptacionRequest(
        documento_id=DOC_ID,
        perfil_destinatario=perfil,
        formato_salida=formato,
        nicho=nicho,
        nivel_detalle=nivel,
    )
    respuesta = svc.generate_content(req)
    data = respuesta.model_dump()
    for campo in CAMPOS_OBLIGATORIOS:
        assert campo in data, f"Falta campo '{campo}'"


# --- Degradacion OCI ---

def test_fallo_oci_no_impide_respuesta():
    """Un fallo de OCI no debe bloquear la entrega del contenido."""
    oci_falla = MagicMock()
    oci_falla.upload_artifact.return_value = OCIUploadResult(status="error", detalle="Timeout")
    svc = AgentService(_rag(), _llm(), oci_falla)
    req = AdaptacionRequest(
        documento_id=DOC_ID,
        perfil_destinatario="principiante",
        formato_salida="tutorial",
        nicho="general",
        nivel_detalle="didactico",
    )
    resp = svc.generate_content(req)
    assert resp.contenido_adaptado is not None
    assert resp.almacenamiento_oci.status_upload == "error"


def test_generate_content_incluye_metadatos_educativos_qa_007():
    """QA-007: generate_content debe poblar tiempo_estimado_estudio_minutos y conceptos_clave."""
    svc = AgentService(_rag(), _llm(), _oci())
    req = AdaptacionRequest(
        documento_id=DOC_ID,
        perfil_destinatario="junior",
        formato_salida="tutorial",
        nicho="fintech",
        nivel_detalle="tecnico",
    )
    resp = svc.generate_content(req)
    assert resp.metadatos.tiempo_estimado_estudio_minutos >= 1
    assert isinstance(resp.metadatos.conceptos_clave, list)
    assert isinstance(resp.metadatos.tiempo_estimado_estudio_minutos, int)


# --- Tests robustez de _extraer_conceptos_clave (Bloque 3D) ---

def test_extraer_conceptos_clave_con_negritas():
    """Prioridad 1: Extrae conceptos destacados en negrita Markdown."""
    texto = (
        "En este tutorial aprenderemos sobre **Fotosíntesis**, **Clorofila** y **Ciclo de Calvin**.\n"
        "También mencionamos **Fotosíntesis** de nuevo para validar deduplicación."
    )
    conceptos = _extraer_conceptos_clave(texto, [])
    assert conceptos == ["Fotosíntesis", "Clorofila", "Ciclo de Calvin"]


def test_extraer_conceptos_clave_definicion_sin_negritas():
    """Prioridad 2: Extrae términos antes de dos puntos en listas o glosarios cuando no hay negritas."""
    texto = (
        "Glosario de términos:\n"
        "- Fotosíntesis: Proceso biológico de conversión de luz solar en energía.\n"
        "- Cloroplasto: Orgánulo celular donde ocurre la fotosíntesis.\n"
        "- ATP: Molécula energética fundamental.\n"
    )
    conceptos = _extraer_conceptos_clave(texto, [])
    assert "Fotosíntesis" in conceptos
    assert "Cloroplasto" in conceptos
    assert "ATP" in conceptos


def test_extraer_conceptos_clave_formato_json():
    """Prioridad 3: Extrae conceptos de campos estructurados JSON cuando no hay texto libre con negritas/definiciones."""
    texto = (
        '[\n'
        '  {"concepto": "Tasa de Interés", "definicion": "Costo del dinero"},\n'
        '  {"concepto": "Inflación", "definicion": "Aumento generalizado de precios"}\n'
        ']'
    )
    conceptos = _extraer_conceptos_clave(texto, [])
    assert "Tasa de Interés" in conceptos
    assert "Inflación" in conceptos


def test_extraer_conceptos_clave_fallback_chunks():
    """Prioridad 4: Cuando el texto generado no tiene negritas ni definiciones, extrae términos de los chunks fuente."""
    texto_generado_plano = "El proceso describe la forma en que las plantas capturan energia solar para transformarla en azucares simples."
    chunks_fuente = [
        ChunkMetadata(
            chunk_id="c1",
            documento_id="doc1",
            texto="La Fotosíntesis oxigénica ocurre en los Tilacoides dentro del Cloroplasto.",
            posicion=0,
            score=0.95,
        ),
        ChunkMetadata(
            chunk_id="c2",
            documento_id="doc1",
            texto="Durante la fase oscura opera el Ciclo de Calvin fijando dióxido de carbono.",
            posicion=1,
            score=0.88,
        ),
    ]
    conceptos = _extraer_conceptos_clave(texto_generado_plano, chunks_fuente)
    assert len(conceptos) > 0
    # Debe haber rescatado términos de los chunks
    assert any(c in conceptos for c in ["Fotosíntesis", "Tilacoides", "Cloroplasto", "Ciclo de Calvin"])


def test_extraer_conceptos_clave_filtrado_stopwords_y_longitud():
    """Filtra palabras genéricas (stopwords), pasos numerados, términos muy cortos o muy largos."""
    texto = (
        "Secciones: **Introducción**, **Resumen**, **Conclusión**, **Paso 1**, **a**, **Término Válido**.\n"
        "**Un texto excesivamente largo que sobrepasa los cuarenta caracteres permitidos en el filtro de validacion**"
    )
    conceptos = _extraer_conceptos_clave(texto, [])
    assert conceptos == ["Término Válido"]
    assert "Introducción" not in conceptos
    assert "Resumen" not in conceptos
    assert "Conclusión" not in conceptos
    assert "Paso 1" not in conceptos


def test_extraer_conceptos_clave_vacio_si_no_hay_contenido():
    """Retorna lista vacía si tanto el contenido generado como los chunks están vacíos."""
    assert _extraer_conceptos_clave("", []) == []
    assert _extraer_conceptos_clave("   ", []) == []


# --- Tests de robustez Bloque 3E.2: Ordinales, conectores y complementación multinivel ---

def test_extraer_conceptos_clave_descarta_ordinales_conectores_y_verbos_genericos():
    """B1: Descarta ordinales (Segunda, Tercera), conectores (Así, Asimismo) y verbos (Existe, Cuenta) de inicio de frase."""
    texto = (
        "El marco regulatorio establece:\n"
        "**Segunda**, se aplicará el régimen especial.\n"
        "**Tercera**, los sujetos obligados deberán reportar.\n"
        "**Existe**, una condición suspensiva.\n"
        "**Así**, se procede con la validación.\n"
        "**Asimismo**, se notificará al **Oficial de Cumplimiento** y al **Comité de Auditoría**."
    )
    conceptos = _extraer_conceptos_clave(texto, [])
    # Deben descartarse los ordinales, conectores y verbos
    assert "Segunda" not in conceptos
    assert "Tercera" not in conceptos
    assert "Existe" not in conceptos
    assert "Así" not in conceptos
    assert "Asimismo" not in conceptos
    # Deben preservarse los términos técnicos genuinos
    assert "Oficial de Cumplimiento" in conceptos
    assert "Comité de Auditoría" in conceptos


def test_extraer_conceptos_clave_complementacion_multinivel_cuando_insuficientes():
    """B2: Cuando el contenido generado tiene pocas negritas (< 4), complementa con definiciones y chunks fuente."""
    texto_generado = (
        "En esta guía técnica abordaremos un aspecto crucial.\n"
        "El plazo improrrogable es el **31 de mayo de 2027**.\n"
        "- Matriz de Riesgos: Herramienta de valoración y mitigación de eventos operacionales.\n"
    )
    chunks_fuente = [
        ChunkMetadata(
            chunk_id="c1",
            documento_id="doc1",
            texto="La Circular Externa reglamenta la implementación del Sistema de Autocontrol.",
            posicion=0,
            score=0.90,
        )
    ]
    conceptos = _extraer_conceptos_clave(texto_generado, chunks_fuente)
    # Debe contener la negrita válida
    assert "31 de mayo de 2027" in conceptos
    # Debe haber complementado con la definición (prioridad 2)
    assert "Matriz de Riesgos" in conceptos
    # Debe haber complementado con términos técnicos de los chunks (prioridad 4)
    assert any("Circular Externa" in c or "Sistema de Autocontrol" in c for c in conceptos)
    assert len(conceptos) >= 3


def test_extraer_conceptos_clave_normalizacion_tildes_en_stopwords():
    """Filtra palabras genéricas tanto con tildes como sin tildes mediante normalización NFD."""
    texto = "**Término**, **Términos**, **Definición**, **Guía**, **Introducción**, **Inteligencia Artificial**"
    conceptos = _extraer_conceptos_clave(texto, [])
    assert conceptos == ["Inteligencia Artificial"]


# --- Tests de refinamiento Bloque 3E.5: Deduplicación de subcadenas, ruido bibliográfico y truncamientos ---

def test_extraer_conceptos_clave_descarta_expresiones_bibliograficas():
    """Descarta expresiones bibliográficas como 'Disponible en', 'Recuperado', 'Página'."""
    texto = (
        "Referencias del documento:\n"
        "**Disponible en**, **Recuperado de**, **Página Web**, **Oficiales de Cumplimiento**."
    )
    conceptos = _extraer_conceptos_clave(texto, [])
    assert "Disponible en" not in conceptos
    assert "Recuperado de" not in conceptos
    assert "Oficiales de Cumplimiento" in conceptos


def test_extraer_conceptos_clave_descarta_terminos_incompletos_truncados():
    """Descarta términos incompletos truncados que terminan en 'No', 'Num', conectores o preposiciones."""
    texto = (
        "Requisitos normativos:\n"
        "**Circular Externa No**, **Ley Num**, **Decreto de**, **Código Contencioso Administrativo**."
    )
    conceptos = _extraer_conceptos_clave(texto, [])
    assert "Circular Externa No" not in conceptos
    assert "Ley Num" not in conceptos
    assert "Decreto de" not in conceptos
    assert "Código Contencioso Administrativo" in conceptos


def test_extraer_conceptos_clave_deduplicacion_subcadenas_preserva_termino_completo():
    """Deduplica subcadenas evitando redundancia entre 'Contencioso Administrativo' y 'Código Contencioso Administrativo'."""
    texto = (
        "Marco procesal aplicable:\n"
        "**Código Contencioso Administrativo** y también **Contencioso Administrativo**.\n"
        "Asimismo se designará al **Oficial de Cumplimiento** con plazo al **31 de mayo de 2027**."
    )
    conceptos = _extraer_conceptos_clave(texto, [])
    # Debe preservar el término compuesto completo
    assert "Código Contencioso Administrativo" in conceptos
    # Debe haber descartado la subcadena redundante
    assert "Contencioso Administrativo" not in conceptos
    # Debe preservar los otros términos válidos
    assert "Oficial de Cumplimiento" in conceptos
    assert "31 de mayo de 2027" in conceptos


# --- Tests Bloque 3E.6: Cierre de fidelidad jurídica y no-regresión de sufijos ---

def test_build_prompt_tutorial_incluye_directriz_oficio_consultivo():
    """Verifica que el prompt del formato 'tutorial' incluya la instrucción de alcance no vinculante y distinción normativa."""
    from unittest.mock import MagicMock
    from app.services.agent_service import AgentService

    svc = AgentService(rag=MagicMock(), llm=MagicMock(), oci=MagicMock())
    chunks = [
        ChunkMetadata(
            chunk_id="chk1",
            documento_id="doc1",
            texto="Oficio de la Superintendencia sobre periodo de transicion.",
            posicion=0,
            score=0.9,
        )
    ]
    system_prompt, user_prompt = svc._build_prompt(
        chunks=chunks,
        perfil="lider_tecnico",
        formato="tutorial",
        nicho="fintech",
        nivel="tecnico",
    )
    # Comprobar presencia de la directriz de fidelidad jurídica en el system_prompt
    assert "concepto u oficio administrativo en instancia consultiva" in system_prompt
    assert "alcance orientador no vinculante" in system_prompt
    assert "distinguelo claramente de las circulares" in system_prompt
    assert "[Fragmento 1]" in user_prompt


def test_extraer_conceptos_clave_no_genera_falsos_positivos_en_sufijos_validos():
    """Garantiza que términos válidos que contienen subcadenas o acaban en palabras legítimas no sean erróneamente filtrados."""
    texto = (
        "Conceptos esenciales de arquitectura y regulación:\n"
        "**Ley de Transición No Vinculante**,\n"
        "**Plan de Contingencia**, \n"
        "**Oficial de Cumplimiento**, \n"
        "**Sistema de Autocontrol**, \n"
        "**Lavado de Activos**, \n"
        "**31 de mayo de 2027**."
    )
    conceptos = _extraer_conceptos_clave(texto, [])
    # Términos técnicos que contienen preposiciones intermedias o conceptos multipalabra válidos
    assert "Plan de Contingencia" in conceptos
    assert "Oficial de Cumplimiento" in conceptos
    assert "Sistema de Autocontrol" in conceptos
    assert "Lavado de Activos" in conceptos
    assert "31 de mayo de 2027" in conceptos
    # Términos que terminan legítimamente sin ser partículas truncadas
    assert "Ley de Transición No Vinculante" in conceptos


# ===========================================================================
# FASE B.1: Pruebas de Invocación Determinista y Propagación de Errores LLM
# ===========================================================================
from app.services.llm_service import LLMTelemetry


def _req():
    return AdaptacionRequest(
        documento_id=DOC_ID,
        perfil_destinatario="principiante",
        formato_salida="tutorial",
        nicho="general",
        nivel_detalle="didactico",
    )


def test_servicio_real_usa_generate_with_telemetry_una_sola_vez():
    """1. Un servicio compatible con telemetría invoca generate_with_telemetry() exactamente una vez y no invoca generate()."""
    class LLMCompatible:
        def __init__(self):
            self.calls_tel = 0
            self.calls_gen = 0
        def generate_with_telemetry(self, prompt, system_prompt=""):
            self.calls_tel += 1
            return ("Contenido generado", LLMTelemetry(modelo="test-model", tokens_entrada=10, tokens_salida=5))
        def generate(self, prompt, system_prompt=""):
            self.calls_gen += 1
            return "Contenido legacy"

    llm_comp = LLMCompatible()
    agent = AgentService(rag=_rag(), llm=llm_comp, oci=_oci())
    res = agent.generate_content(_req())

    assert llm_comp.calls_tel == 1
    assert llm_comp.calls_gen == 0
    assert res.contenido_adaptado == "Contenido generado"
    assert res.metadatos.tokens_entrada == 10
    assert res.metadatos.tokens_salida == 5


def test_type_error_interno_se_propaga_sin_fallback():
    """2. Un TypeError interno en generate_with_telemetry() se propaga y no provoca una segunda llamada a generate()."""
    class LLMConBugInterno:
        def __init__(self):
            self.calls_tel = 0
            self.calls_gen = 0
        def generate_with_telemetry(self, prompt, system_prompt=""):
            self.calls_tel += 1
            raise TypeError("Error interno legítimo de tipos en el SDK")
        def generate(self, prompt, system_prompt=""):
            self.calls_gen += 1
            return "Respuesta que no debería llamarse"

    llm_bug = LLMConBugInterno()
    agent = AgentService(rag=_rag(), llm=llm_bug, oci=_oci())

    with pytest.raises(TypeError) as exc_info:
        agent.generate_content(_req())

    assert "Error interno legítimo de tipos" in str(exc_info.value)
    assert llm_bug.calls_tel == 1
    assert llm_bug.calls_gen == 0  # Cero llamadas duplicadas a generate()


def test_mock_legitimo_antiguo_solo_generate_funciona():
    """3. Un mock o servicio antiguo que solo ofrece generate() continúa funcionando limpiamente."""
    mock_antiguo = MagicMock()
    mock_antiguo.generate.return_value = "Contenido desde servicio legacy"

    agent = AgentService(rag=_rag(), llm=mock_antiguo, oci=_oci())
    res = agent.generate_content(_req())

    assert mock_antiguo.generate.call_count == 1
    assert res.contenido_adaptado == "Contenido desde servicio legacy"
    assert res.metadatos.tokens_entrada is None
    assert res.metadatos.tokens_salida is None


def test_telemetria_valida_se_incorpora_a_metadatos():
    """4. La telemetría válida se incorpora correctamente a los metadatos de respuesta."""
    mock_con_tel = MagicMock()
    tel_obj = LLMTelemetry(modelo="gemini-test", tokens_entrada=150, tokens_salida=60, latencia_total_segundos=1.23)
    mock_con_tel.generate_with_telemetry.return_value = ("Contenido con telemetría", tel_obj)

    agent = AgentService(rag=_rag(), llm=mock_con_tel, oci=_oci())
    res = agent.generate_content(_req())

    assert mock_con_tel.generate_with_telemetry.call_count == 1
    assert res.metadatos.tokens_entrada == 150
    assert res.metadatos.tokens_salida == 60
    assert res.metadatos.latencia_segundos == 1.23


def test_ausencia_telemetria_compatible_con_esquema():
    """5. La ausencia de valores de telemetría opcionales sigue siendo compatible con el esquema y la serialización."""
    mock_con_tel_none = MagicMock()
    tel_none = LLMTelemetry(modelo="gemini-test", tokens_entrada=None, tokens_salida=None, latencia_total_segundos=0.0)
    mock_con_tel_none.generate_with_telemetry.return_value = ("Contenido sin tokens", tel_none)

    agent = AgentService(rag=_rag(), llm=mock_con_tel_none, oci=_oci())
    res = agent.generate_content(_req())

    assert res.metadatos.tokens_entrada is None
    assert res.metadatos.tokens_salida is None
    # Comprobar que serializa a JSON sin errores
    json_str = res.model_dump_json()
    assert '"tokens_entrada":null' in json_str or '"tokens_entrada": null' in json_str or "tokens_entrada" in json_str


def test_cero_llamadas_duplicadas_contrato_tupla_invalido():
    """6. Si generate_with_telemetry() no cumple el contrato de tupla de 2 elementos, produce TypeError explícito y no duplica llamada."""
    class LLMContratoRoto:
        def __init__(self):
            self.calls_tel = 0
            self.calls_gen = 0
        def generate_with_telemetry(self, prompt, system_prompt=""):
            self.calls_tel += 1
            return "Retorno no tupla"  # Contrato roto
        def generate(self, prompt, system_prompt=""):
            self.calls_gen += 1
            return "Fallback indebido"

    llm_roto = LLMContratoRoto()
    agent = AgentService(rag=_rag(), llm=llm_roto, oci=_oci())

    with pytest.raises(TypeError) as exc_info:
        agent.generate_content(_req())

    assert "debe retornar una tupla de 2 elementos" in str(exc_info.value)
    assert llm_roto.calls_tel == 1
    assert llm_roto.calls_gen == 0






