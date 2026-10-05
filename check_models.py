import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Inicializamos el cliente oficial de Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

try:
    models = client.models.list()
    print("📋 Modelos actualmente disponibles en tu cuenta de Groq:")
    for model in models.data:
        print(f"  - ID: {model.id}")
except Exception as e:
    print(f"❌ Error al listar los modelos: {e}")