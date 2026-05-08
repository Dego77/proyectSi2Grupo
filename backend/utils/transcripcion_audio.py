import os
from functools import lru_cache
from dotenv import load_dotenv
from faster_whisper import WhisperModel


load_dotenv()


@lru_cache(maxsize=1)
def obtener_modelo_whisper() -> WhisperModel:
    modelo = os.getenv("WHISPER_MODEL", "base")
    dispositivo = os.getenv("WHISPER_DEVICE", "cpu")
    tipo_calculo = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

    return WhisperModel(
        modelo,
        device=dispositivo,
        compute_type=tipo_calculo
    )


def transcribir_audio(ruta_audio: str) -> str:
    modelo = obtener_modelo_whisper()

    segmentos, info = modelo.transcribe(
        ruta_audio,
        language="es",
        beam_size=5,
        vad_filter=True
    )

    texto = " ".join(segmento.text.strip() for segmento in segmentos)

    if not texto.strip():
        return "No se pudo transcribir el audio."

    return texto.strip()