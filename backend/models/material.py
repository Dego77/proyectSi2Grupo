from typing import Optional
from decimal import Decimal
from sqlmodel import SQLModel, Field


class Material(SQLModel, table=True):
    __tablename__ = "material"

    id_material: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    precio: Decimal
    stock: int