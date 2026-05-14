from typing import Optional, List, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database_empresa import get_session_empresa
from utils.seguridad_roles import requerir_roles
from utils.bitacora import registrar_bitacora
from utils.firebase_push import enviar_push_a_token
from models import Bitacora


router = APIRouter(
    prefix="/casos-uso/hu32/notificaciones",
    tags=["HU-32 - Gestionar Notificaciones Push"]
)


class CrearNotificacionPushRequest(BaseModel):
    destinatario: Optional[str] = None
    fcm_token: str = Field(..., min_length=10)

    titulo: str = Field(..., min_length=2)
    mensaje: str = Field(..., min_length=2)
    tipo: str = "General"

    data: Optional[Dict[str, str]] = None


@router.post("/enviar")
def crear_notificacion_push_real(
    datos: CrearNotificacionPushRequest,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado")),
):
    """
    Envía una notificación push real usando Firebase Cloud Messaging.

    Requiere:
    - X-Empresa-Id
    - X-Usuario-Id
    - fcm_token del dispositivo destino
    """

    try:
        respuesta_firebase = enviar_push_a_token(
            token=datos.fcm_token,
            titulo=datos.titulo,
            mensaje=datos.mensaje,
            data={
                "tipo": datos.tipo,
                "destinatario": datos.destinatario or "",
                **(datos.data or {}),
            },
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo enviar la notificación push: {str(error)}"
        )

    registrar_bitacora(
        session=session,
        id_usuario=usuario_actual["usuario"].id_usuarios,
        modulo="HU-32 - Notificaciones Push",
        accion="Notificación push enviada",
        descripcion=(
            f"Destinatario: {datos.destinatario or 'No especificado'}. "
            f"Título: {datos.titulo}. "
            f"Tipo: {datos.tipo}. "
            f"Mensaje: {datos.mensaje}. "
            f"Respuesta Firebase: {respuesta_firebase}"
        ),
    )

    return {
        "mensaje": "Notificación push enviada correctamente.",
        "firebase_response": respuesta_firebase,
        "destinatario": datos.destinatario,
        "titulo": datos.titulo,
        "tipo": datos.tipo,
    }


@router.get("", response_model=List[Bitacora])
def listar_notificaciones_bitacora(
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    return session.exec(
        select(Bitacora)
        .where(Bitacora.modulo == "HU-32 - Notificaciones Push")
        .order_by(Bitacora.fecha_hora.desc())
    ).all()