from typing import Optional
from datetime import date
from decimal import Decimal
from sqlmodel import SQLModel, Field


class ActivosFijos(SQLModel, table=True):
    __tablename__ = "activos_fijos"

    id_activo: Optional[int] = Field(default=None, primary_key=True)
    id_proyecto: Optional[int] = Field(default=None, foreign_key="proyecto.id_proyecto")
    nombre: str
    tipo_activo: str
    codigo_activo: str
    fechacompra: Optional[date] = None
    valor_compra: Decimal
    vida_util: int
    valor_residual: Decimal
    estado: str