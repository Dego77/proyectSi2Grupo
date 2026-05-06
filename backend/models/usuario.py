from typing import Optional
from datetime import date, datetime
from sqlmodel import SQLModel, Field


class Rol(SQLModel, table=True):
    __tablename__ = "rol"

    id_rol: Optional[int] = Field(default=None, primary_key=True)
    rol: str
    descripcion: Optional[str] = None
    niveljerarquia: int = 0
    fechacreacion: Optional[datetime] = None


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id_usuarios: Optional[int] = Field(default=None, primary_key=True)
    id_rol: int = Field(foreign_key="rol.id_rol")
    nombresusuario: str
    nombres: str
    apellido: str
    email: str
    ci: Optional[str] = None
    genero: Optional[str] = None
    contrasena: str
    fecha_de_nacimiento: Optional[date] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None


class Permisos(SQLModel, table=True):
    __tablename__ = "permisos"

    id_permiso: Optional[int] = Field(default=None, primary_key=True)
    descripcion: Optional[str] = None


class RolPermisos(SQLModel, table=True):
    __tablename__ = "rol_permisos"

    id_rol: int = Field(foreign_key="rol.id_rol", primary_key=True)
    id_permiso: int = Field(foreign_key="permisos.id_permiso", primary_key=True)


class Bitacora(SQLModel, table=True):
    __tablename__ = "bitacora"

    id_bitacora: Optional[int] = Field(default=None, primary_key=True)
    id_usuarios: int = Field(foreign_key="usuario.id_usuarios")
    fecha_hora: Optional[datetime] = None
    modulo: str
    accion: str
    descripcion: Optional[str] = None