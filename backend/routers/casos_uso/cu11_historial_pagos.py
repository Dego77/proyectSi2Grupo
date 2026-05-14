from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy import func

from database_empresa import get_session_empresa
from utils.seguridad_roles import requerir_roles
from models import Pago


router = APIRouter(
    prefix="/casos-uso/cu11/pagos",
    tags=["CU11 - Historial de Pagos y Deudas"]
)


def redondear(valor) -> Decimal:
    return Decimal(str(valor or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


@router.get("/historial")
def ver_historial_pagos_deudas(
    id_proyecto: Optional[int] = None,
    id_venta: Optional[int] = None,
    estado: Optional[str] = None,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    consulta = select(Pago)

    if id_proyecto is not None:
        consulta = consulta.where(Pago.id_proyecto == id_proyecto)

    if id_venta is not None:
        consulta = consulta.where(Pago.id_venta == id_venta)

    if estado:
        consulta = consulta.where(func.lower(Pago.estado) == estado.lower())

    pagos = session.exec(
        consulta.order_by(Pago.fecha.desc())
    ).all()

    total_pagado = Decimal("0")
    total_pendiente = Decimal("0")
    total_observado = Decimal("0")

    for pago in pagos:
        monto = Decimal(str(pago.monto or 0))
        estado_pago = str(pago.estado or "").lower()

        if estado_pago in ["completado", "pagado", "aprobado"]:
            total_pagado += monto
        elif estado_pago in ["pendiente", "deuda", "por pagar"]:
            total_pendiente += monto
        else:
            total_observado += monto

    return {
        "total_registros": len(pagos),
        "total_pagado_bob": redondear(total_pagado),
        "total_pendiente_bob": redondear(total_pendiente),
        "total_observado_bob": redondear(total_observado),
        "pagos": pagos
    }