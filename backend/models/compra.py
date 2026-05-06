from typing import Optional
from datetime import date
from decimal import Decimal
from sqlmodel import SQLModel, Field


class Proveedor(SQLModel, table=True):
    __tablename__ = "proveedor"

    id_proveedor: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    contacto: str


class Compra(SQLModel, table=True):
    __tablename__ = "compra"

    id_compra: Optional[int] = Field(default=None, primary_key=True)
    id_proveedor: Optional[int] = Field(default=None, foreign_key="proveedor.id_proveedor")
    id_movimiento: Optional[int] = Field(default=None, foreign_key="movimiento_financiero.id_movimiento")
    id_usuarios: Optional[int] = Field(default=None, foreign_key="usuario.id_usuarios")
    fecha: Optional[date] = None
    total: Decimal


class DetalleCompra(SQLModel, table=True):
    __tablename__ = "detalle_compra"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_compra: Optional[int] = Field(default=None, foreign_key="compra.id_compra")
    id_material: Optional[int] = Field(default=None, foreign_key="material.id_material")
    cantidad: int
    precio: Decimal