from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class Proyecto(SQLModel, table=True):
    __tablename__ = "proyecto"

    id_proyecto: Optional[int] = Field(default=None, primary_key=True)
    id_usuarios: Optional[int] = Field(default=None, foreign_key="usuario.id_usuarios")
    nombre: str
    ubicacion: str
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: str