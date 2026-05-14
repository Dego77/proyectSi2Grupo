from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from database_empresa import get_session_empresa
from utils.seguridad_roles import requerir_roles
from utils.bitacora import registrar_bitacora
from models import Rol, Permisos, RolPermisos


router = APIRouter(
    prefix="/casos-uso/cu14/perfiles-permisos",
    tags=["CU14 - Gestionar Perfiles y Permisos"]
)


class AsignarPermisoRolRequest(BaseModel):
    id_rol: int
    id_permiso: int


@router.get("")
def listar_perfiles_y_permisos(
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador")),
):
    roles = session.exec(select(Rol)).all()
    permisos = session.exec(select(Permisos)).all()
    relaciones = session.exec(select(RolPermisos)).all()

    perfiles = []

    for rol in roles:
        permisos_del_rol = []

        for relacion in relaciones:
            if relacion.id_rol == rol.id_rol:
                permiso = session.get(Permisos, relacion.id_permiso)

                if permiso:
                    permisos_del_rol.append({
                        "id_permiso": permiso.id_permiso,
                        "descripcion": permiso.descripcion
                    })

        perfiles.append({
            "id_rol": rol.id_rol,
            "rol": rol.rol,
            "descripcion": rol.descripcion,
            "niveljerarquia": rol.niveljerarquia,
            "permisos": permisos_del_rol
        })

    return {
        "total_roles": len(roles),
        "total_permisos": len(permisos),
        "perfiles": perfiles
    }


@router.post("/asignar")
def asignar_permiso_a_rol(
    datos: AsignarPermisoRolRequest,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador")),
):
    rol = session.get(Rol, datos.id_rol)

    if not rol:
        raise HTTPException(
            status_code=404,
            detail="Rol no encontrado."
        )

    permiso = session.get(Permisos, datos.id_permiso)

    if not permiso:
        raise HTTPException(
            status_code=404,
            detail="Permiso no encontrado."
        )

    existente = session.get(RolPermisos, (datos.id_rol, datos.id_permiso))

    if existente:
        return {
            "mensaje": "El permiso ya estaba asignado al rol."
        }

    relacion = RolPermisos(
        id_rol=datos.id_rol,
        id_permiso=datos.id_permiso
    )

    session.add(relacion)
    session.commit()

    registrar_bitacora(
        session=session,
        id_usuario=usuario_actual["usuario"].id_usuarios,
        modulo="CU14 - Perfiles y Permisos",
        accion="Asignar permiso",
        descripcion=f"Se asignó el permiso {datos.id_permiso} al rol {datos.id_rol}.",
    )

    return {
        "mensaje": "Permiso asignado correctamente al rol."
    }


@router.delete("/{id_rol}/{id_permiso}")
def quitar_permiso_a_rol(
    id_rol: int,
    id_permiso: int,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador")),
):
    relacion = session.get(RolPermisos, (id_rol, id_permiso))

    if not relacion:
        raise HTTPException(
            status_code=404,
            detail="La relación rol-permiso no existe."
        )

    session.delete(relacion)
    session.commit()

    registrar_bitacora(
        session=session,
        id_usuario=usuario_actual["usuario"].id_usuarios,
        modulo="CU14 - Perfiles y Permisos",
        accion="Quitar permiso",
        descripcion=f"Se quitó el permiso {id_permiso} al rol {id_rol}.",
    )

    return {
        "mensaje": "Permiso retirado correctamente del rol."
    }