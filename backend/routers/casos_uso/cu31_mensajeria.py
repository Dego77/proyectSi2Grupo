from typing import Optional, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database_empresa import get_session_empresa
from utils.seguridad_roles import requerir_roles
from utils.bitacora import registrar_bitacora
from models import Bitacora


router = APIRouter(
    prefix="/casos-uso/cu31/mensajes",
    tags=["CU31 - Mensajería Interna y Cliente"]
)


class EnviarMensajeRequest(BaseModel):
    destinatario: Optional[str] = None
    asunto: Optional[str] = None
    mensaje: str = Field(..., min_length=1)


@router.post("")
def enviar_mensaje_interno_cliente(
    datos: EnviarMensajeRequest,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    registrar_bitacora(
        session=session,
        id_usuario=usuario_actual["usuario"].id_usuarios,
        modulo="CU31 - Mensajería",
        accion="Mensaje enviado",
        descripcion=(
            f"Destinatario: {datos.destinatario or 'No especificado'}. "
            f"Asunto: {datos.asunto or 'Sin asunto'}. "
            f"Mensaje: {datos.mensaje}"
        ),
    )

    return {
        "mensaje": "Mensaje registrado correctamente en bitácora.",
        "destinatario": datos.destinatario,
        "asunto": datos.asunto,
        "detalle": datos.mensaje
    }


@router.get("", response_model=List[Bitacora])
def listar_mensajes_bitacora(
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    return session.exec(
        select(Bitacora)
        .where(Bitacora.modulo == "CU31 - Mensajería")
        .order_by(Bitacora.fecha_hora.desc())
    ).all()