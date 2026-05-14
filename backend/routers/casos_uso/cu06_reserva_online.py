from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from database_empresa import get_session_empresa
from utils.seguridad_roles import requerir_roles
from utils.bitacora import registrar_bitacora
from models import Pago, MovimientoFinanciero


router = APIRouter(
    prefix="/casos-uso/cu06/reserva-online",
    tags=["CU06 - Pagar Reserva Online"]
)


def redondear(valor) -> Decimal:
    return Decimal(str(valor or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


class PagarReservaOnlineRequest(BaseModel):
    id_proyecto: Optional[int] = None
    id_venta: Optional[int] = None
    monto_reserva: Decimal = Field(..., gt=0)
    metodo_pago: str = Field(..., min_length=2)
    codigo_transaccion: Optional[str] = None
    descripcion: Optional[str] = None


class PagarReservaOnlineResponse(BaseModel):
    id_pago: int
    id_movimiento: int
    id_proyecto: Optional[int]
    monto_reserva: Decimal
    estado: str
    mensaje: str


@router.post("/pagar", response_model=PagarReservaOnlineResponse)
def pagar_reserva_online(
    datos: PagarReservaOnlineRequest,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    movimiento = MovimientoFinanciero(
        id_proyecto=datos.id_proyecto,
        tipo_movimiento="Ingreso",
        categoria="Reserva online",
        monto=redondear(datos.monto_reserva),
        fecha=datetime.utcnow().date(),
        descripcion=datos.descripcion or "Pago de reserva online web/móvil",
    )

    session.add(movimiento)
    session.commit()
    session.refresh(movimiento)

    pago = Pago(
        id_venta=datos.id_venta,
        id_movimiento=movimiento.id_movimiento,
        id_proyecto=datos.id_proyecto,
        metodo_pago=datos.metodo_pago,
        monto=redondear(datos.monto_reserva),
        fecha=datetime.utcnow(),
        estado="Completado",
        codigo_transaccion=datos.codigo_transaccion,
    )

    session.add(pago)
    session.commit()
    session.refresh(pago)

    registrar_bitacora(
        session=session,
        id_usuario=usuario_actual["usuario"].id_usuarios,
        modulo="CU06 - Pagar Reserva Online",
        accion="Pago de reserva online",
        descripcion=f"Se registró una reserva online por {pago.monto} Bs. Pago ID {pago.id_pago}.",
    )

    return {
        "id_pago": pago.id_pago,
        "id_movimiento": movimiento.id_movimiento,
        "id_proyecto": pago.id_proyecto,
        "monto_reserva": redondear(pago.monto),
        "estado": pago.estado,
        "mensaje": "Reserva online pagada correctamente."
    }