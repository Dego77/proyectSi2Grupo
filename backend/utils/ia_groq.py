import os
from groq import Groq
from dotenv import load_dotenv


load_dotenv()


def obtener_respuesta_groq(mensaje: str, contexto_bd: str = "") -> str:
    api_key = os.getenv("GROQ_API_KEY")
    modelo = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        raise ValueError("Falta GROQ_API_KEY en el archivo .env")

    client = Groq(api_key=api_key)

    system_prompt = f"""
Eres un asistente IA para un sistema de gestión de constructora.

Puedes ayudar al usuario con:
- empresas
- usuarios
- proyectos
- compras
- proveedores
- materiales
- empleados
- planillas
- presupuestos
- pagos
- ventas
- movimientos financieros

Responde en español, claro y directo.

Usa los datos reales del sistema cuando estén disponibles.
Si no tienes datos suficientes, indícalo y pide al usuario que sea más específico.

Contexto actual de PostgreSQL:
{contexto_bd}
"""

    respuesta = client.chat.completions.create(
        model=modelo,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": mensaje
            }
        ],
        temperature=0.3,
        max_tokens=600
    )

    return respuesta.choices[0].message.content