from typing import Optional
from datetime import date
from decimal import Decimal
from sqlmodel import SQLModel, Field


class Presupuesto(SQLModel, table=True):
    __tablename__ = "presupuesto"

    id_presupuesto: Optional[int] = Field(default=None, primary_key=True)
    id_proyecto: Optional[int] = Field(default=None, foreign_key="proyecto.id_proyecto")
    costo_total: Decimal
    fecha: Optional[date] = None


class DetallePresupuesto(SQLModel, table=True):
    __tablename__ = "detalle_presupuesto"

    id_presupuesto: int = Field(foreign_key="presupuesto.id_presupuesto", primary_key=True)
    id_material: int = Field(foreign_key="material.id_material", primary_key=True)
    cantidad: int
    costo: Decimal