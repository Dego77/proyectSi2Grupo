from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database_empresa import get_session_empresa
from utils.seguridad_roles import requerir_roles
from utils.bitacora import registrar_bitacora
from models import Bitacora


router = APIRouter(
    prefix="/casos-uso/cu10/consultas",
    tags=["CU10 - Consultas / Mensajes a Empresa"]
)


class CrearConsultaEmpresaRequest(BaseModel):
    asunto: str = Field(..., min_length=2)
    mensaje: str = Field(..., min_length=2)


class ResponderConsultaEmpresaRequest(BaseModel):
    id_bitacora: int
    respuesta: str = Field(..., min_length=2)


@router.post("")
def crear_consulta_empresa(
    datos: CrearConsultaEmpresaRequest,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    registrar_bitacora(
        session=session,
        id_usuario=usuario_actual["usuario"].id_usuarios,
        modulo="CU10 - Consulta Empresa",
        accion="Consulta enviada",
        descripcion=f"Asunto: {datos.asunto}. Mensaje: {datos.mensaje}",
    )

    return {
        "mensaje": "Consulta enviada correctamente a la empresa.",
        "asunto": datos.asunto,
        "detalle": datos.mensaje
    }


@router.get("", response_model=List[Bitacora])
def listar_consultas_empresa(
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    return session.exec(
        select(Bitacora)
        .where(Bitacora.modulo == "CU10 - Consulta Empresa")
        .order_by(Bitacora.fecha_hora.desc())
    ).all()


@router.post("/responder")
def responder_consulta_empresa(
    datos: ResponderConsultaEmpresaRequest,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado")),
):
    consulta = session.get(Bitacora, datos.id_bitacora)

    if not consulta:
        raise HTTPException(
            status_code=404,
            detail="Consulta no encontrada."
        )

    registrar_bitacora(
        session=session,
        id_usuario=usuario_actual["usuario"].id_usuarios,
        modulo="CU10 - Consulta Empresa",
        accion="Respuesta a consulta",
        descripcion=f"Respuesta a bitácora ID {datos.id_bitacora}: {datos.respuesta}",
    )

    return {
        "mensaje": "Respuesta registrada correctamente en bitácora.",
        "id_consulta_referenciada": datos.id_bitacora,
        "respuesta": datos.respuesta
    }