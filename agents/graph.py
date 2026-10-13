from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import pedagogical_writer_node, critic_agent_node

def should_continue(state: AgentState):
    """
    Función de enrutamiento condicional: decide si el grafo termina 
    o si devuelve el trabajo al redactor para correcciones.
    """
    feedback = state.get("review_feedback", "")
    iterations = state.get("iteration_count", 0)
    
    # Si el crítico pide mejoras y no hemos excedido los 2 intentos permitidos
    if "MEJORA:" in feedback and iterations < 2:
        print(f"🔄 [Grafo] El crítico solicitó mejoras (Iteración {iterations}/2). Redirigiendo al Redactor...")
        return "retry"
    
    # De lo contrario, el proceso finaliza con éxito
    print("✅ [Grafo] Proceso pedagógico aprobado o límite de iteraciones alcanzado. Finalizando.")
    return "end"

# Construcción del Grafo
workflow = StateGraph(AgentState)

# 1. Añadir nodos
workflow.add_node("writer", pedagogical_writer_node)
workflow.add_node("critic", critic_agent_node)

# 2. Definir el punto de entrada
workflow.set_entry_point("writer")

# 3. Flujo lineal inicial: Writer -> Critic
workflow.add_edge("writer", "critic")

# 4. Añadir aristas condicionales salientes del Critic
workflow.add_conditional_edges(
    "critic",
    should_continue,
    {
        "retry": "writer", # Si necesita corrección, vuelve al redactor
        "end": END         # Si está aprobado o excede intentos, termina
    }
)

# Compilación obligatoria expuesta globalmente
app_graph = workflow.compile()