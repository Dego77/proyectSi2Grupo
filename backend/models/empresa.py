from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Empresa(SQLModel, table=True):
    __tablename__ = "empresa"

    id_empresa: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    nit: str
    telefono: str
    email: str
    direccion: str
    estado: str

 # Contraseña de acceso de la empresa al sistema
    contrasena: Optional[str] = None
 

class BaseDeDatosEmpresa(SQLModel, table=True):
    __tablename__ = "base_de_datos_empresa"

    id_basedatos: Optional[int] = Field(default=None, primary_key=True)
    id_empresa: Optional[int] = Field(default=None, foreign_key="empresa.id_empresa")
    nombre_bd: str
    host: str
    puerto: int
    usuario_bd: str
    password_bd: str
    estado: bool
    fecha_creacion: Optional[datetime] = None