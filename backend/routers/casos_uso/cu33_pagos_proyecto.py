from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database_empresa import get_session_empresa
from utils.seguridad_roles import requerir_roles
from utils.bitacora import registrar_bitacora
from models import Pago, MovimientoFinanciero


router = APIRouter(
    prefix="/casos-uso/hu33",
    tags=["HU-33 - Gestionar Pagos del Proyecto"]
)


def redondear(valor) -> Decimal:
    return Decimal(str(valor or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


class CrearPagoProyectoRequest(BaseModel):
    id_venta: Optional[int] = None
    metodo_pago: str = Field(..., min_length=2)
    monto: Decimal = Field(..., gt=0)
    estado: str = "Completado"
    codigo_transaccion: Optional[str] = None

    tipo_movimiento: str = "Ingreso"
    categoria: str = "Pago de proyecto"
    descripcion: Optional[str] = None


class ActualizarEstadoPagoRequest(BaseModel):
    estado: str = Field(..., min_length=2)


@router.post("/proyectos/{id_proyecto}/pagos")
def crear_pago_proyecto(
    id_proyecto: int,
    datos: CrearPagoProyectoRequest,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado")),
):
    movimiento = MovimientoFinanciero(
        id_proyecto=id_proyecto,
        tipo_movimiento=datos.tipo_movimiento,
        categoria=datos.categoria,
        monto=redondear(datos.monto),
        fecha=datetime.utcnow().date(),
        descripcion=datos.descripcion or f"Pago registrado para proyecto {id_proyecto}",
    )

    session.add(movimiento)
    session.commit()
    session.refresh(movimiento)

    pago = Pago(
        id_venta=datos.id_venta,
        id_movimiento=movimiento.id_movimiento,
        id_proyecto=id_proyecto,
        metodo_pago=datos.metodo_pago,
        monto=redondear(datos.monto),
        fecha=datetime.utcnow(),
        estado=datos.estado,
        codigo_transaccion=datos.codigo_transaccion,
    )

    session.add(pago)
    session.commit()
    session.refresh(pago)

    registrar_bitacora(
        session=session,
        id_usuario=usuario_actual["usuario"].id_usuarios,
        modulo="HU-33 - Pagos del Proyecto",
        accion="Registrar pago",
        descripcion=f"Se registró pago de {pago.monto} Bs para proyecto {id_proyecto}.",
    )

    return {
        "mensaje": "Pago del proyecto registrado correctamente.",
        "id_pago": pago.id_pago,
        "id_movimiento": movimiento.id_movimiento,
        "pago": pago,
        "movimiento_financiero": movimiento
    }


@router.get("/proyectos/{id_proyecto}/pagos", response_model=List[Pago])
def listar_pagos_proyecto(
    id_proyecto: int,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    return session.exec(
        select(Pago)
        .where(Pago.id_proyecto == id_proyecto)
        .order_by(Pago.fecha.desc())
    ).all()


@router.put("/pagos/{id_pago}/estado")
def actualizar_estado_pago(
    id_pago: int,
    datos: ActualizarEstadoPagoRequest,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado")),
):
    pago = session.get(Pago, id_pago)

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado."
        )

    estado_anterior = pago.estado
    pago.estado = datos.estado

    session.add(pago)
    session.commit()
    session.refresh(pago)

    registrar_bitacora(
        session=session,
        id_usuario=usuario_actual["usuario"].id_usuarios,
        modulo="HU-33 - Pagos del Proyecto",
        accion="Actualizar estado de pago",
        descripcion=f"Pago ID {id_pago}: {estado_anterior} -> {datos.estado}.",
    )

    return {
        "mensaje": "Estado del pago actualizado correctamente.",
        "pago": pago
    }