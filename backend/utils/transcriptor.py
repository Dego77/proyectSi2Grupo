import os
import uuid

from fastapi import UploadFile
from faster_whisper import WhisperModel


model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


async def transcribir_audio(audio: UploadFile) -> dict:
    carpeta_temp = "temp_audio"

    os.makedirs(carpeta_temp, exist_ok=True)

    extension = audio.filename.split(".")[-1].lower()

    nombre_archivo = f"{uuid.uuid4()}.{extension}"

    ruta_audio = os.path.join(
        carpeta_temp,
        nombre_archivo
    )

    try:
        contenido = await audio.read()

        with open(ruta_audio, "wb") as archivo:
            archivo.write(contenido)

        segmentos, info = model.transcribe(
            ruta_audio,
            language="es"
        )

        texto = " ".join(
            segmento.text.strip()
            for segmento in segmentos
        )

        return {
            "idioma": info.language,
            "texto": texto
        }

    finally:
        if os.path.exists(ruta_audio):
            os.remove(ruta_audio)