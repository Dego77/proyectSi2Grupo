from crud.factory import crear_crud_router

from models import (
    Empresa,
    BaseDeDatosEmpresa,
    Rol,
    Usuario,
    Permisos,
    RolPermisos,
    Bitacora,
)


# ============================================================
# TABLAS CENTRALES DEL SISTEMA MULTIEMPRESA
# ============================================================

empresa_router = crear_crud_router(
    modelo=Empresa,
    prefix="/empresas",
    tags=["Sistema - Empresas"],
    campos_pk=("id_empresa",),
    usar_bd_empresa=False,
    proteger=False,
)

base_datos_empresa_router = crear_crud_router(
    modelo=BaseDeDatosEmpresa,
    prefix="/bases-datos-empresa",
    tags=["Sistema - Bases de datos por empresa"],
    campos_pk=("id_basedatos",),
    usar_bd_empresa=False,
    proteger=False,
)


# ============================================================
# TABLAS PROPIAS DE CADA EMPRESA
# ============================================================

rol_router = crear_crud_router(
    modelo=Rol,
    prefix="/roles",
    tags=["Sistema - Roles"],
    campos_pk=("id_rol",),
    usar_bd_empresa=True,
    proteger=True,
    roles_listar=("Administrador",),
    roles_crear=("Administrador",),
    roles_actualizar=("Administrador",),
    roles_eliminar=("Administrador",),
)

usuario_router = crear_crud_router(
    modelo=Usuario,
    prefix="/usuarios",
    tags=["Sistema - Usuarios"],
    campos_pk=("id_usuarios",),
    usar_bd_empresa=True,
    proteger=True,
    roles_listar=("Administrador",),
    roles_crear=("Administrador",),
    roles_actualizar=("Administrador",),
    roles_eliminar=("Administrador",),
)

permisos_router = crear_crud_router(
    modelo=Permisos,
    prefix="/permisos",
    tags=["Sistema - Permisos"],
    campos_pk=("id_permiso",),
    usar_bd_empresa=True,
    proteger=True,
    roles_listar=("Administrador",),
    roles_crear=("Administrador",),
    roles_actualizar=("Administrador",),
    roles_eliminar=("Administrador",),
)

rol_permisos_router = crear_crud_router(
    modelo=RolPermisos,
    prefix="/rol-permisos",
    tags=["Sistema - Rol permisos"],
    campos_pk=("id_rol", "id_permiso"),
    usar_bd_empresa=True,
    proteger=True,
    roles_listar=("Administrador",),
    roles_crear=("Administrador",),
    roles_actualizar=("Administrador",),
    roles_eliminar=("Administrador",),
)

bitacora_router = crear_crud_router(
    modelo=Bitacora,
    prefix="/bitacoras",
    tags=["Sistema - Bitácora"],
    campos_pk=("id_bitacora",),
    usar_bd_empresa=True,
    proteger=True,
    roles_listar=("Administrador",),
    roles_crear=("Administrador",),
    roles_actualizar=("Administrador",),
    roles_eliminar=("Administrador",),
)


routers = [
    empresa_router,
    base_datos_empresa_router,
    rol_router,
    usuario_router,
    permisos_router,
    rol_permisos_router,
    bitacora_router,
]