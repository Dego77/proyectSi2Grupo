import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, create_engine
from sqlalchemy.exc import SQLAlchemyError

from database import get_session
from database_empresa import (
    construir_database_url,
    construir_nombre_bd_empresa,
    crear_base_datos_postgres,
    crear_tablas_empresa,
)
from models import (
    Empresa,
    BaseDeDatosEmpresa,
    Rol,
    Usuario,
    Permisos,
    RolPermisos,
)


router = APIRouter(
    prefix="/empresas-saas",
    tags=["Empresas SaaS"]
)


class RegistrarEmpresaSaasRequest(BaseModel):
    nombre: str = Field(..., min_length=2)
    nit: str
    telefono: str
    email: str
    direccion: str
    contrasena_empresa: str = Field(..., min_length=6)

    admin_usuario: str = Field(..., min_length=3)
    admin_nombres: str
    admin_apellido: str
    admin_email: str
    admin_contrasena: str = Field(..., min_length=6)


class RegistrarEmpresaSaasResponse(BaseModel):
    id_empresa: int
    nombre_empresa: str
    nombre_bd: str
    mensaje: str


def insertar_datos_iniciales_empresa(
    database_url_empresa: str,
    datos: RegistrarEmpresaSaasRequest,
):
    """
    Inserta datos base dentro de la base de datos propia de la empresa.

    Crea:
    - Roles: Administrador, Cliente, Empleado.
    - Usuario administrador inicial.
    - Permisos base del sistema.
    - Relación rol-permiso.
    """

    engine_empresa = create_engine(database_url_empresa, echo=True)

    with Session(engine_empresa) as session:
        try:
            # ============================================================
            # ROLES INICIALES
            # ============================================================

            rol_admin = Rol(
                id_rol=1,
                rol="Administrador",
                descripcion="Administra todo el sistema de la empresa",
                niveljerarquia=1,
                fechacreacion=datetime.utcnow(),
            )

            rol_cliente = Rol(
                id_rol=2,
                rol="Cliente",
                descripcion="Usuario cliente del sistema",
                niveljerarquia=2,
                fechacreacion=datetime.utcnow(),
            )

            rol_empleado = Rol(
                id_rol=3,
                rol="Empleado",
                descripcion="Personal interno de la empresa constructora",
                niveljerarquia=3,
                fechacreacion=datetime.utcnow(),
            )

            session.add(rol_admin)
            session.add(rol_cliente)
            session.add(rol_empleado)

            # ============================================================
            # PERMISOS INICIALES
            # ============================================================

            permiso_usuarios = Permisos(
                id_permiso=1,
                descripcion="Gestionar usuarios"
            )

            permiso_roles = Permisos(
                id_permiso=2,
                descripcion="Gestionar roles y permisos"
            )

            permiso_proyectos = Permisos(
                id_permiso=3,
                descripcion="Gestionar proyectos"
            )

            permiso_presupuestos = Permisos(
                id_permiso=4,
                descripcion="Gestionar presupuestos"
            )

            permiso_reportes = Permisos(
                id_permiso=5,
                descripcion="Ver reportes"
            )

            permiso_ia = Permisos(
                id_permiso=6,
                descripcion="Usar asistente IA"
            )

            permiso_materiales = Permisos(
                id_permiso=7,
                descripcion="Gestionar materiales"
            )

            permiso_compras = Permisos(
                id_permiso=8,
                descripcion="Gestionar compras"
            )

            permiso_ventas = Permisos(
                id_permiso=9,
                descripcion="Gestionar ventas"
            )

            permiso_finanzas = Permisos(
                id_permiso=10,
                descripcion="Gestionar movimientos financieros"
            )

            permisos = [
                permiso_usuarios,
                permiso_roles,
                permiso_proyectos,
                permiso_presupuestos,
                permiso_reportes,
                permiso_ia,
                permiso_materiales,
                permiso_compras,
                permiso_ventas,
                permiso_finanzas,
            ]

            for permiso in permisos:
                session.add(permiso)

            # Se guardan roles y permisos antes de crear relaciones.
            session.flush()

            # ============================================================
            # RELACIÓN ROL - PERMISOS
            # ============================================================

            permisos_admin = [
                RolPermisos(id_rol=1, id_permiso=1),
                RolPermisos(id_rol=1, id_permiso=2),
                RolPermisos(id_rol=1, id_permiso=3),
                RolPermisos(id_rol=1, id_permiso=4),
                RolPermisos(id_rol=1, id_permiso=5),
                RolPermisos(id_rol=1, id_permiso=6),
                RolPermisos(id_rol=1, id_permiso=7),
                RolPermisos(id_rol=1, id_permiso=8),
                RolPermisos(id_rol=1, id_permiso=9),
                RolPermisos(id_rol=1, id_permiso=10),
            ]

            permisos_cliente = [
                RolPermisos(id_rol=2, id_permiso=5),
                RolPermisos(id_rol=2, id_permiso=6),
            ]

            permisos_empleado = [
                RolPermisos(id_rol=3, id_permiso=3),
                RolPermisos(id_rol=3, id_permiso=4),
                RolPermisos(id_rol=3, id_permiso=5),
                RolPermisos(id_rol=3, id_permiso=6),
                RolPermisos(id_rol=3, id_permiso=7),
                RolPermisos(id_rol=3, id_permiso=8),
                RolPermisos(id_rol=3, id_permiso=9),
                RolPermisos(id_rol=3, id_permiso=10),
            ]

            for relacion in permisos_admin + permisos_cliente + permisos_empleado:
                session.add(relacion)

            # ============================================================
            # USUARIO ADMINISTRADOR INICIAL
            # ============================================================

            usuario_admin = Usuario(
                id_usuarios=1,
                id_rol=1,
                nombresusuario=datos.admin_usuario,
                nombres=datos.admin_nombres,
                apellido=datos.admin_apellido,
                email=datos.admin_email,
                ci=None,
                genero=None,
                contrasena=datos.admin_contrasena,
                fecha_de_nacimiento=None,
                telefono=datos.telefono,
                direccion=datos.direccion,
            )

            session.add(usuario_admin)

            session.commit()

        except SQLAlchemyError as error:
            session.rollback()
            raise RuntimeError(
                f"No se pudieron insertar los datos iniciales de la empresa: {str(error)}"
            )


@router.post("/registrar", response_model=RegistrarEmpresaSaasResponse)
def registrar_empresa_saas(
    datos: RegistrarEmpresaSaasRequest,
    session_central: Session = Depends(get_session),
):
    """
    Registra una nueva empresa SaaS.

    Flujo:
    1. Guarda empresa en BD central.
    2. Crea una BD exclusiva para esa empresa.
    3. Crea tablas en esa BD.
    4. Inserta roles, permisos y usuario administrador.
    5. Guarda la conexión en base_de_datos_empresa.
    """

    empresa = Empresa(
        nombre=datos.nombre,
        nit=datos.nit,
        telefono=datos.telefono,
        email=datos.email,
        direccion=datos.direccion,
        estado="Activo",
        contrasena=datos.contrasena_empresa,
    )

    try:
        session_central.add(empresa)
        session_central.commit()
        session_central.refresh(empresa)

    except Exception as error:
        session_central.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo registrar la empresa en la base central: {str(error)}"
        )

    nombre_bd = construir_nombre_bd_empresa(
        id_empresa=empresa.id_empresa,
        nombre_empresa=empresa.nombre,
    )

    host = os.getenv("DB_ADMIN_HOST", "127.0.0.1")
    puerto = int(os.getenv("DB_ADMIN_PORT", "5432"))
    usuario_bd = os.getenv("DB_ADMIN_USER", "postgres")
    password_bd = os.getenv("DB_ADMIN_PASSWORD")

    if not password_bd:
        empresa.estado = "Error configuración BD"
        session_central.add(empresa)
        session_central.commit()

        raise HTTPException(
            status_code=500,
            detail="Falta DB_ADMIN_PASSWORD en el archivo .env."
        )

    try:
        crear_base_datos_postgres(nombre_bd)

        database_url_empresa = construir_database_url(
            host=host,
            puerto=puerto,
            nombre_bd=nombre_bd,
            usuario=usuario_bd,
            password=password_bd,
        )

        crear_tablas_empresa(database_url_empresa)

        insertar_datos_iniciales_empresa(
            database_url_empresa=database_url_empresa,
            datos=datos,
        )

        config_bd = BaseDeDatosEmpresa(
            id_empresa=empresa.id_empresa,
            nombre_bd=nombre_bd,
            host=host,
            puerto=puerto,
            usuario_bd=usuario_bd,
            password_bd=password_bd,
            estado=True,
            fecha_creacion=datetime.utcnow(),
        )

        session_central.add(config_bd)
        session_central.commit()

    except Exception as error:
        empresa.estado = "Error creación BD"
        session_central.add(empresa)
        session_central.commit()

        raise HTTPException(
            status_code=500,
            detail=f"La empresa fue creada, pero falló la creación/configuración de su BD: {str(error)}"
        )

    return {
        "id_empresa": empresa.id_empresa,
        "nombre_empresa": empresa.nombre,
        "nombre_bd": nombre_bd,
        "mensaje": "Empresa registrada, base de datos creada y permisos iniciales configurados correctamente.",
    }