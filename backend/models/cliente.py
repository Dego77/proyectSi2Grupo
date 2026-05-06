from typing import Optional
from sqlmodel import SQLModel, Field


class Cliente(SQLModel, table=True):
    __tablename__ = "cliente"

    id_cliente: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    telefono: str
    direccion: str