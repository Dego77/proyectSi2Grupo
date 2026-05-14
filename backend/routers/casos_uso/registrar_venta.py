from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database_empresa import get_session_empresa
from utils.seguridad_roles import requerir_roles
from utils.bitacora import registrar_bitacora

from models import (
    Venta,
    Cliente,
    MovimientoFinanciero,
)


router = APIRouter(
    prefix="/casos-uso/registrar-venta",
    tags=["CU - Registrar Venta"]
)


def redondear(valor) -> Decimal:
    return Decimal(str(valor or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


class RegistrarVentaRequest(BaseModel):
    id_cliente: Optional[int] = None
    id_proyecto: Optional[int] = None

    total: Decimal = Field(..., gt=0)
    fecha: Optional[date] = None

    categoria: str = "Venta"
    descripcion: Optional[str] = None


class RegistrarVentaResponse(BaseModel):
    id_venta: int
    id_cliente: Optional[int]
    id_movimiento: Optional[int]
    id_usuarios: Optional[int]
    total: Decimal
    fecha: Optional[date]
    mensaje: str


@router.post("", response_model=RegistrarVentaResponse)
def registrar_venta(
    datos: RegistrarVentaRequest,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado")),
):
    """
    Registra una venta dentro de la base de datos de la empresa activa.

    Multiempresa:
    - X-Empresa-Id define la base de datos de la empresa.
    - X-Usuario-Id define el usuario responsable.

    Flujo:
    1. Valida cliente si se envía.
    2. Registra movimiento financiero como ingreso.
    3. Registra venta.
    4. Registra acción en bitácora.
    """

    usuario = usuario_actual["usuario"]

    if datos.id_cliente is not None:
        cliente = session.get(Cliente, datos.id_cliente)

        if not cliente:
            raise HTTPException(
                status_code=404,
                detail="Cliente no encontrado en esta empresa."
            )

    movimiento = MovimientoFinanciero(
        id_proyecto=datos.id_proyecto,
        tipo_movimiento="Ingreso",
        categoria=datos.categoria,
        monto=redondear(datos.total),
        fecha=datos.fecha or date.today(),
        descripcion=datos.descripcion or "Registro de venta",
    )

    session.add(movimiento)
    session.commit()
    session.refresh(movimiento)

    venta = Venta(
        id_cliente=datos.id_cliente,
        id_movimiento=movimiento.id_movimiento,
        id_usuarios=usuario.id_usuarios,
        total=redondear(datos.total),
        fecha=datos.fecha or date.today(),
    )

    session.add(venta)
    session.commit()
    session.refresh(venta)

    registrar_bitacora(
        session=session,
        id_usuario=usuario.id_usuarios,
        modulo="CU - Registrar Venta",
        accion="Registrar venta",
        descripcion=(
            f"Se registró la venta ID {venta.id_venta} "
            f"por un total de {venta.total} Bs."
        ),
    )

    return {
        "id_venta": venta.id_venta,
        "id_cliente": venta.id_cliente,
        "id_movimiento": venta.id_movimiento,
        "id_usuarios": venta.id_usuarios,
        "total": redondear(venta.total),
        "fecha": venta.fecha,
        "mensaje": "Venta registrada correctamente en la base de datos de la empresa."
    }


@router.get("")
def listar_ventas(
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    """
    Lista las ventas registradas en la empresa activa.
    """

    ventas = session.exec(
        select(Venta).order_by(Venta.fecha.desc())
    ).all()

    return ventas


@router.get("/{id_venta}")
def obtener_venta(
    id_venta: int,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    """
    Consulta una venta específica dentro de la empresa activa.
    """

    venta = session.get(Venta, id_venta)

    if not venta:
        raise HTTPException(
            status_code=404,
            detail="Venta no encontrada en esta empresa."
        )

    movimiento = None

    if venta.id_movimiento:
        movimiento = session.get(MovimientoFinanciero, venta.id_movimiento)

    return {
        "venta": venta,
        "movimiento_financiero": movimiento,
    }