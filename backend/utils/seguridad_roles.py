from fastapi import Depends, Header, HTTPException
from sqlmodel import Session

from database_empresa import get_session_empresa
from models import Usuario, Rol


def obtener_usuario_actual_empresa(
    x_usuario_id: int = Header(..., alias="X-Usuario-Id"),
    session: Session = Depends(get_session_empresa),
):
    usuario = session.get(Usuario, x_usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado en la empresa actual."
        )

    rol = session.get(Rol, usuario.id_rol)

    if not rol:
        raise HTTPException(
            status_code=403,
            detail="El usuario no tiene un rol válido asignado."
        )

    return {
        "usuario": usuario,
        "rol": rol.rol,
        "id_rol": rol.id_rol,
    }


def requerir_roles(*roles_permitidos: str):
    def dependencia(usuario_actual=Depends(obtener_usuario_actual_empresa)):
        rol_usuario = usuario_actual["rol"].strip().lower()

        roles_normalizados = [
            rol.strip().lower()
            for rol in roles_permitidos
        ]

        if rol_usuario not in roles_normalizados:
            raise HTTPException(
                status_code=403,
                detail=f"No tienes permiso para realizar esta acción. Roles permitidos: {roles_permitidos}"
            )

        return usuario_actual

    return dependencia


def permitir_sin_usuario():
    return None