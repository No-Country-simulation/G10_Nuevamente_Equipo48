import os
import argparse
from dotenv import load_dotenv
from agents.graph import app_graph
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

def main():
    parser = argparse.ArgumentParser(
        description="CLI Dinámica para el Sistema Multi-Agente Pedagógico (Proyecto NuevaMente)"
    )
    
    parser.add_argument(
        "--file", 
        type=str, 
        required=True, 
        help="Ruta hacia el archivo PDF fuente (ej. data/raw/documento_prueba.pdf)"
    )
    
    parser.add_argument(
        "--profile", 
        type=str, 
        default="tech_lead",
        choices=["principiante", "junior", "tech_lead", "ejecutivo"],
        help="Perfil objetivo para la adaptación pedagógica"
    )
    
    parser.add_argument(
        "--format", 
        type=str, 
        default="resumen_ejecutivo",
        help="Formato de salida deseado (ej. resumen_ejecutivo, guia_paso_a_paso, analisis_arquitectura)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ [Error] El archivo especificado no existe: {args.file}")
        return

    print(f"📄 Cargando documento PDF desde: {args.file}")
    
    try:
        loader = PyPDFLoader(args.file)
        pages = loader.load()
        # Concatenamos y limitamos a una ventana segura para no romper la cuota de ITPM de Groq (~12k-15k caracteres)
        document_text = "\n".join([page.page_content for page in pages])
        
        # Estrategia de seguridad de tokens de entrada (Truncar a ~12,000 caracteres para respetar el ITPM de 7000 tokens)
        max_chars = 12000
        if len(document_text) > max_chars:
            print(f"⚠️ [Optimizador] El documento es muy extenso ({len(document_text)} chars). Truncando a los primeros {max_chars} caracteres para respetar el límite de ITPM de Groq...")
            document_text = document_text[:max_chars]
            
        print(f"✅ PDF procesado y fragmentado exitosamente. Páginas leídas: {len(pages)}")
    except Exception as e:
        print(f"❌ [Error al procesar PDF]: {e}")
        return

    initial_state = {
        "pdf_path": args.file,
        "target_profile": args.profile,
        "output_format": args.format,
        "retrieved_chunks": [document_text],
        "processed_content": "",
        "review_feedback": "",
        "iteration_count": 0
    }

    print(f"\n🚀 Ejecutando flujo de agentes [Perfil: {args.profile.upper()} | Formato: {args.format}]...")
    print("-" * 60)

    try:
        final_state = app_graph.invoke(initial_state)
        
        print("\n" + "=" * 60)
        print("--- RESULTADO OBTENIDO (ADAPTADO AL PERFIL) ---")
        print("=" * 60)
        print(final_state.get("processed_content", "Sin contenido generado."))
        
        print("\n" + "=" * 60)
        print("--- REVISIÓN DEL AGENTE CRÍTICO (ESTADO FINAL) ---")
        print("=" * 60)
        print(final_state.get("review_feedback", "Sin feedback registrado."))
        print("-" * 60)
        
    except Exception as e:
        print(f"\n⚠️ [Error crítico en la ejecución del grafo]: {e}")

if __name__ == "__main__":
    main()
