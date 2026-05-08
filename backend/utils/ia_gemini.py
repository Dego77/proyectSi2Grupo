import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH, override=True)


def responder_con_gemini(pregunta: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    modelo = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

    if not api_key:
        raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Eres un asistente inteligente para un sistema multiempresa orientado a construcción.

Tu función es ayudar al usuario con consultas técnicas, administrativas o generales relacionadas con construcción, empresas, materiales, costos, solicitudes, servicios y gestión.

Responde en español, de forma clara, útil y directa.

Pregunta del usuario:
{pregunta}
"""

    respuesta = client.models.generate_content(
        model=modelo,
        contents=prompt
    )

    return respuesta.text or "No se pudo generar una respuesta de IA."