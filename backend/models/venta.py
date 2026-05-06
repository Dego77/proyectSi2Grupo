from typing import Optional
from datetime import date
from decimal import Decimal
from sqlmodel import SQLModel, Field


class Venta(SQLModel, table=True):
    __tablename__ = "venta"

    id_venta: Optional[int] = Field(default=None, primary_key=True)
    id_cliente: Optional[int] = Field(default=None, foreign_key="cliente.id_cliente")
    id_movimiento: Optional[int] = Field(default=None, foreign_key="movimiento_financiero.id_movimiento")
    id_usuarios: Optional[int] = Field(default=None, foreign_key="usuario.id_usuarios")
    total: Decimal
    fecha: Optional[date] = None