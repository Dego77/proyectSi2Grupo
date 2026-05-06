from typing import Optional
from datetime import date
from decimal import Decimal
from sqlmodel import SQLModel, Field


class Empleados(SQLModel, table=True):
    __tablename__ = "empleados"

    id_empleados: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    cargo: str
    salario: Decimal
    telefono: str


class Planillas(SQLModel, table=True):
    __tablename__ = "planillas"

    id_planillas: Optional[int] = Field(default=None, primary_key=True)
    id_usuarios: Optional[int] = Field(default=None, foreign_key="usuario.id_usuarios")
    id_empleados: Optional[int] = Field(default=None, foreign_key="empleados.id_empleados")
    id_proyecto: Optional[int] = Field(default=None, foreign_key="proyecto.id_proyecto")
    id_movimiento: Optional[int] = Field(default=None, foreign_key="movimiento_financiero.id_movimiento")
    fecha: Optional[date] = None
    pago: Decimal
    periodo: str