from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field


class MovimientoFinanciero(SQLModel, table=True):
    __tablename__ = "movimiento_financiero"

    id_movimiento: Optional[int] = Field(default=None, primary_key=True)
    id_proyecto: Optional[int] = Field(default=None, foreign_key="proyecto.id_proyecto")
    tipo_movimiento: str
    categoria: str
    monto: Decimal
    fecha: Optional[date] = None
    descripcion: Optional[str] = None


class Pago(SQLModel, table=True):
    __tablename__ = "pago"

    id_pago: Optional[int] = Field(default=None, primary_key=True)
    id_venta: Optional[int] = Field(default=None, foreign_key="venta.id_venta")
    id_movimiento: Optional[int] = Field(default=None, foreign_key="movimiento_financiero.id_movimiento")
    id_proyecto: Optional[int] = Field(default=None, foreign_key="proyecto.id_proyecto")
    metodo_pago: str
    monto: Decimal
    fecha: Optional[datetime] = None
    estado: str = "Pendiente"
    codigo_transaccion: Optional[str] = None