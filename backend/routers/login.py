from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from sqlalchemy import func, or_

from database import get_session
from database_empresa import (
    get_session_empresa,
    construir_database_url_empresa,
    obtener_engine_empresa,
)
from models import Empresa, BaseDeDatosEmpresa, Usuario, Rol, Cliente, Proyecto
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
    has_active_project: bool = False


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

    # Verificar dinamicamente si el usuario tiene algún proyecto registrado en Postgres
    proyecto_activo = session.exec(
        select(Proyecto).where(Proyecto.id_usuario == usuario.id_usuarios)
    ).first()
    tiene_proyecto = proyecto_activo is not None

    return {
        "mensaje": "Login de usuario correcto.",
        "id_empresa": x_empresa_id,
        "id_usuario": usuario.id_usuarios,
        "usuario": usuario.nombresusuario,
        "nombres": usuario.nombres,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "rol": rol.rol,
        "has_active_project": tiene_proyecto,
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


class RegisterUsuarioRequest(BaseModel):
    nombres: str = Field(..., min_length=2)
    apellido: str = Field(..., min_length=2)
    email: str = Field(..., min_length=5)
    contrasena: str = Field(..., min_length=4)
    telefono:str= Field(..., min_length=7)
    direccion: str = Field(..., min_length=5)

class RegisterUsuarioResponse(BaseModel):
    mensaje: str
    id_empresa: int
    id_usuario: int
    usuario: str
    nombres: str
    apellido: str
    email: str
    rol: str



@router.post("/registro", response_model=RegisterUsuarioResponse)
def registrar_usuario(
    datos: RegisterUsuarioRequest,
    x_empresa_id: int = Header(..., alias="X-Empresa-Id"),
    session: Session = Depends(get_session_empresa),
):
    """
    Registra de forma autónoma (auto-registro público) un nuevo usuario de tipo Cliente.
    """
    email_normalizado = datos.email.strip().lower()

    # Verificar si el usuario ya existe en esta empresa
    existe_usuario = session.exec(
        select(Usuario).where(func.lower(Usuario.email) == email_normalizado)
    ).first()
    if existe_usuario:
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ya se encuentra registrado."
        )

    # Obtener el rol de Cliente (ID 2 según seed.sql)
    rol_cliente = session.get(Rol, 2)
    if not rol_cliente:
        rol_cliente = session.exec(
            select(Rol).where(func.lower(Rol.rol) == "cliente")
        ).first()
        if not rol_cliente:
            raise HTTPException(
                status_code=500,
                detail="Rol 'Cliente' no configurado en el sistema."
            )

    # Generar un nombresusuario único
    nombresusuario = email_normalizado.split("@")[0]
    nombresusuario_base = nombresusuario
    contador = 1
    while session.exec(
        select(Usuario).where(Usuario.nombresusuario == nombresusuario)
    ).first():
        nombresusuario = f"{nombresusuario_base}{contador}"
        contador += 1

    # Crear el Usuario
    nuevo_usuario = Usuario(
        id_rol=rol_cliente.id_rol,
        nombresusuario=nombresusuario,
        nombres=datos.nombres,
        apellido=datos.apellido,
        email=email_normalizado,
        contrasena=datos.contrasena,
        telefono=datos.telefono,
        direccion=datos.direccion
    )

    # Crear el Cliente (espejo CRM)
    nuevo_cliente = Cliente(
        nombre=f"{datos.nombres} {datos.apellido}".strip(),
        telefono=datos.telefono or "",
        direccion=datos.direccion or ""
    )

    try:
        session.add(nuevo_usuario)
        session.add(nuevo_cliente)
        session.commit()
        session.refresh(nuevo_usuario)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos al registrar: {str(e)}"
        )

    # Registrar en bitácora
    registrar_bitacora(
        session=session,
        id_usuario=nuevo_usuario.id_usuarios,
        modulo="Registro Usuario",
        accion="Creación de cuenta",
        descripcion=f"El cliente {nuevo_usuario.nombresusuario} se registró de forma autónoma.",
    )

    return {
        "mensaje": "Usuario registrado correctamente.",
        "id_empresa": x_empresa_id,
        "id_usuario": nuevo_usuario.id_usuarios,
        "usuario": nuevo_usuario.nombresusuario,
        "nombres": nuevo_usuario.nombres,
        "apellido": nuevo_usuario.apellido,
        "email": nuevo_usuario.email,
        "rol": rol_cliente.rol
    }