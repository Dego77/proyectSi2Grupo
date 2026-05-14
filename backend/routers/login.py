from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from sqlalchemy import func, or_

from database import get_session
from database_empresa import (
    get_session_empresa,
    construir_database_url_empresa,
    obtener_engine_empresa,
)
from models import Empresa, BaseDeDatosEmpresa, Usuario, Rol
from utils.seguridad_roles import requerir_roles
from utils.bitacora import registrar_bitacora


router = APIRouter(
    prefix="/login",
    tags=["Login - Multiempresa"]
)


class LoginEmpresaRequest(BaseModel):
    email: str = Field(..., min_length=5)
    contrasena: str = Field(..., min_length=4)


class LoginEmpresaResponse(BaseModel):
    mensaje: str
    id_empresa: int
    nombre_empresa: str
    email: str
    id_usuario_admin: int


class LoginUsuarioRequest(BaseModel):
    identificador: str = Field(..., min_length=3)
    contrasena: str = Field(..., min_length=4)


class LoginUsuarioResponse(BaseModel):
    mensaje: str
    id_empresa: int
    id_usuario: int
    usuario: str
    nombres: str
    apellido: str
    email: str
    rol: str


def registrar_login_empresa_en_bitacora(
    session_central: Session,
    id_empresa: int,
    descripcion: str,
):
    """
    Registra el login de empresa dentro de la BD propia de esa empresa.
    Usa id_usuario=1 porque al crear la empresa SaaS se crea un admin inicial.
    """

    config_bd = session_central.exec(
        select(BaseDeDatosEmpresa).where(
            BaseDeDatosEmpresa.id_empresa == id_empresa,
            BaseDeDatosEmpresa.estado == True,
        )
    ).first()

    if not config_bd:
        return

    try:
        database_url = construir_database_url_empresa(config_bd)
        engine_empresa = obtener_engine_empresa(database_url)

        with Session(engine_empresa) as session_empresa:
            usuario_admin = session_empresa.get(Usuario, 1)

            if usuario_admin:
                registrar_bitacora(
                    session=session_empresa,
                    id_usuario=1,
                    modulo="Login Empresa",
                    accion="Inicio de sesión",
                    descripcion=descripcion,
                )

    except Exception:
        pass


#iniciar sesión empresa
@router.post("/empresa", response_model=LoginEmpresaResponse)
def login_empresa(
    datos: LoginEmpresaRequest,
    session: Session = Depends(get_session),
):
    email_normalizado = datos.email.strip().lower()

    empresa = session.exec(
        select(Empresa).where(
            func.lower(Empresa.email) == email_normalizado
        )
    ).first()

    if not empresa:
        raise HTTPException(
            status_code=401,
            detail="Credenciales de empresa incorrectas."
        )

    if empresa.contrasena != datos.contrasena:
        raise HTTPException(
            status_code=401,
            detail="Credenciales de empresa incorrectas."
        )

    if str(empresa.estado).lower() != "activo":
        raise HTTPException(
            status_code=403,
            detail="La empresa no se encuentra activa."
        )

    registrar_login_empresa_en_bitacora(
        session_central=session,
        id_empresa=empresa.id_empresa,
        descripcion=f"La empresa {empresa.nombre} inició sesión correctamente.",
    )

    return {
        "mensaje": "Login de empresa correcto.",
        "id_empresa": empresa.id_empresa,
        "nombre_empresa": empresa.nombre,
        "email": empresa.email,
        "id_usuario_admin": 1,
    }


#iniciar sesión usuario
@router.post("/usuario", response_model=LoginUsuarioResponse)
def login_usuario(
    datos: LoginUsuarioRequest,
    x_empresa_id: int = Header(..., alias="X-Empresa-Id"),
    session: Session = Depends(get_session_empresa),
):
    identificador = datos.identificador.strip().lower()

    usuario = session.exec(
        select(Usuario).where(
            or_(
                func.lower(Usuario.email) == identificador,
                func.lower(Usuario.nombresusuario) == identificador,
            )
        )
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Credenciales de usuario incorrectas."
        )

    if usuario.contrasena != datos.contrasena:
        raise HTTPException(
            status_code=401,
            detail="Credenciales de usuario incorrectas."
        )

    rol = session.get(Rol, usuario.id_rol)

    if not rol:
        raise HTTPException(
            status_code=403,
            detail="El usuario no tiene rol asignado."
        )

    registrar_bitacora(
        session=session,
        id_usuario=usuario.id_usuarios,
        modulo="Login Usuario",
        accion="Inicio de sesión",
        descripcion=f"El usuario {usuario.nombresusuario} inició sesión correctamente.",
    )

    return {
        "mensaje": "Login de usuario correcto.",
        "id_empresa": x_empresa_id,
        "id_usuario": usuario.id_usuarios,
        "usuario": usuario.nombresusuario,
        "nombres": usuario.nombres,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "rol": rol.rol,
    }
    
class CerrarSesionResponse(BaseModel):
    mensaje: str
    id_empresa: int
    id_usuario: int
    usuario: str
    
@router.post("/cerrar-sesion", response_model=CerrarSesionResponse)
def cerrar_sesion(
    x_empresa_id: int = Header(..., alias="X-Empresa-Id"),
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    """
    Cierra la sesión del usuario dentro de una empresa activa.

    Multiempresa:
    - X-Empresa-Id define la base de datos de la empresa.
    - X-Usuario-Id identifica al usuario que cierra sesión.
    """

    usuario = usuario_actual["usuario"]

    registrar_bitacora(
        session=session,
        id_usuario=usuario.id_usuarios,
        modulo="Login Usuario",
        accion="Cierre de sesión",
        descripcion=f"El usuario {usuario.nombresusuario} cerró sesión correctamente.",
    )

    return {
        "mensaje": "Sesión cerrada correctamente. El cliente debe eliminar los datos de sesión almacenados.",
        "id_empresa": x_empresa_id,
        "id_usuario": usuario.id_usuarios,
        "usuario": usuario.nombresusuario,
    }