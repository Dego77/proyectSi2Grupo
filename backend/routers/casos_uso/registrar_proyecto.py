from typing import Optional, List
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database_empresa import get_session_empresa
from utils.seguridad_roles import requerir_roles
from utils.bitacora import registrar_bitacora
from models import Proyecto


router = APIRouter(
    prefix="/casos-uso/registrar-proyecto",
    tags=["CU - Registrar Proyecto"]
)


class RegistrarProyectoRequest(BaseModel):
    nombre: str = Field(..., min_length=2)
    ubicacion: str = Field(..., min_length=2)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: str = "En planificación"


class ProyectoResponse(BaseModel):
    id_proyecto: int
    id_usuarios: Optional[int]
    nombre: str
    ubicacion: str
    fecha_inicio: Optional[date]
    fecha_fin: Optional[date]
    estado: str


@router.post("", response_model=ProyectoResponse)
def registrar_proyecto(
    datos: RegistrarProyectoRequest,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado")),
):
    """
    Registra un proyecto en la base de datos de la empresa activa.

    Multiempresa:
    - X-Empresa-Id define la base de datos de la empresa.
    - X-Usuario-Id define el usuario responsable.
    """

    usuario = usuario_actual["usuario"]

    proyecto = Proyecto(
        id_usuarios=usuario.id_usuarios,
        nombre=datos.nombre,
        ubicacion=datos.ubicacion,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        estado=datos.estado,
    )

    session.add(proyecto)
    session.commit()
    session.refresh(proyecto)

    registrar_bitacora(
        session=session,
        id_usuario=usuario.id_usuarios,
        modulo="CU - Registrar Proyecto",
        accion="Registrar proyecto",
        descripcion=f"Se registró el proyecto '{proyecto.nombre}' con ID {proyecto.id_proyecto}.",
    )

    return proyecto


@router.get("", response_model=List[ProyectoResponse])
def listar_proyectos_registrados(
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    """
    Lista proyectos registrados en la empresa activa.
    """

    return session.exec(select(Proyecto)).all()


@router.get("/{id_proyecto}", response_model=ProyectoResponse)
def obtener_proyecto_registrado(
    id_proyecto: int,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    """
    Consulta un proyecto específico dentro de la empresa activa.
    """

    proyecto = session.get(Proyecto, id_proyecto)

    if not proyecto:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado en esta empresa."
        )

    return proyecto