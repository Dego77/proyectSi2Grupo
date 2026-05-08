import os
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from utils.ia_gemini import responder_con_gemini
from utils.transcripcion_audio import transcribir_audio


router = APIRouter(
    prefix="/ia",
    tags=["IA - Gemini y Audio"]
)


class PreguntaIARequest(BaseModel):
    pregunta: str = Field(..., min_length=2)


class PreguntaIAResponse(BaseModel):
    tipo: str
    pregunta: str
    respuesta: str


class AudioIAResponse(BaseModel):
    tipo: str
    transcripcion: str
    respuesta: str


@router.post("/preguntar", response_model=PreguntaIAResponse)
def preguntar_ia(datos: PreguntaIARequest):
    try:
        respuesta = responder_con_gemini(datos.pregunta)

        return {
            "tipo": "texto",
            "pregunta": datos.pregunta,
            "respuesta": respuesta
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar Gemini: {str(error)}"
        )


@router.post("/preguntar-audio", response_model=AudioIAResponse)
async def preguntar_ia_con_audio(audio: UploadFile = File(...)):
    extensiones_permitidas = [".mp3", ".wav", ".m4a", ".ogg", ".webm", ".mp4"]

    nombre_original = audio.filename or ""
    extension = Path(nombre_original).suffix.lower()

    if extension not in extensiones_permitidas:
        raise HTTPException(
            status_code=400,
            detail="Formato de audio no permitido. Usa mp3, wav, m4a, ogg, webm o mp4."
        )

    carpeta_temporal = Path("temp_audio")
    carpeta_temporal.mkdir(exist_ok=True)

    nombre_temporal = f"{uuid.uuid4()}{extension}"
    ruta_temporal = carpeta_temporal / nombre_temporal

    try:
        contenido = await audio.read()

        if not contenido:
            raise HTTPException(
                status_code=400,
                detail="El archivo de audio está vacío."
            )

        with open(ruta_temporal, "wb") as archivo:
            archivo.write(contenido)

        transcripcion = transcribir_audio(str(ruta_temporal))

        if not transcripcion or transcripcion == "No se pudo transcribir el audio.":
            raise HTTPException(
                status_code=400,
                detail="No se pudo transcribir el audio."
            )

        pregunta_para_ia = f"""
El usuario envió un audio. Esta es la transcripción:

{transcripcion}

Responde a lo que el usuario pidió en el audio.
"""

        respuesta = responder_con_gemini(pregunta_para_ia)

        return {
            "tipo": "audio",
            "transcripcion": transcripcion,
            "respuesta": respuesta
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el audio con IA: {str(error)}"
        )

    finally:
        if ruta_temporal.exists():
            try:
                os.remove(ruta_temporal)
            except Exception:
                pass