from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database_empresa import get_session_empresa
from utils.seguridad_roles import requerir_roles
from utils.bitacora import registrar_bitacora

from models import (
    Compra,
    DetalleCompra,
    Proveedor,
    Material,
    MovimientoFinanciero,
)


router = APIRouter(
    prefix="/casos-uso/registrar-compra",
    tags=["CU - Registrar Compra"]
)


def redondear(valor) -> Decimal:
    return Decimal(str(valor or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


class DetalleCompraRequest(BaseModel):
    id_material: int
    cantidad: int = Field(..., gt=0)
    precio: Decimal = Field(..., gt=0)


class RegistrarCompraRequest(BaseModel):
    id_proveedor: Optional[int] = None
    id_proyecto: Optional[int] = None
    fecha: Optional[date] = None
    descripcion: Optional[str] = None
    detalles: List[DetalleCompraRequest]


class DetalleCompraResponse(BaseModel):
    id_material: int
    nombre_material: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class RegistrarCompraResponse(BaseModel):
    id_compra: int
    id_movimiento: int
    id_proveedor: Optional[int]
    id_usuarios: Optional[int]
    fecha: Optional[date]
    total: Decimal
    detalles: List[DetalleCompraResponse]
    mensaje: str


@router.post("", response_model=RegistrarCompraResponse)
def registrar_compra(
    datos: RegistrarCompraRequest,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado")),
):
    """
    Registra una compra dentro de la base de datos de la empresa activa.

    Multiempresa:
    - X-Empresa-Id define la base de datos de la empresa.
    - X-Usuario-Id define el usuario responsable.

    Flujo:
    1. Valida proveedor si se envía.
    2. Valida materiales.
    3. Calcula total.
    4. Registra movimiento financiero como egreso.
    5. Registra compra.
    6. Registra detalle de compra.
    7. Registra acción en bitácora.
    """

    if not datos.detalles:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un material en el detalle de la compra."
        )

    usuario = usuario_actual["usuario"]

    if datos.id_proveedor is not None:
        proveedor = session.get(Proveedor, datos.id_proveedor)

        if not proveedor:
            raise HTTPException(
                status_code=404,
                detail="Proveedor no encontrado en esta empresa."
            )

    ids_materiales = [detalle.id_material for detalle in datos.detalles]

    if len(ids_materiales) != len(set(ids_materiales)):
        raise HTTPException(
            status_code=400,
            detail="No se puede repetir el mismo material en una compra."
        )

    total_compra = Decimal("0")
    detalles_respuesta = []
    detalles_para_guardar = []

    for detalle in datos.detalles:
        material = session.get(Material, detalle.id_material)

        if not material:
            raise HTTPException(
                status_code=404,
                detail=f"Material con ID {detalle.id_material} no encontrado en esta empresa."
            )

        precio_unitario = Decimal(str(detalle.precio))
        subtotal = precio_unitario * Decimal(detalle.cantidad)
        total_compra += subtotal

        detalles_para_guardar.append({
            "id_material": material.id_material,
            "cantidad": detalle.cantidad,
            "precio": redondear(precio_unitario),
        })

        detalles_respuesta.append({
            "id_material": material.id_material,
            "nombre_material": material.nombre,
            "cantidad": detalle.cantidad,
            "precio_unitario": redondear(precio_unitario),
            "subtotal": redondear(subtotal),
        })

    movimiento = MovimientoFinanciero(
        id_proyecto=datos.id_proyecto,
        tipo_movimiento="Egreso",
        categoria="Compra de materiales",
        monto=redondear(total_compra),
        fecha=datos.fecha or date.today(),
        descripcion=datos.descripcion or "Registro de compra de materiales",
    )

    session.add(movimiento)
    session.commit()
    session.refresh(movimiento)

    compra = Compra(
        id_proveedor=datos.id_proveedor,
        id_movimiento=movimiento.id_movimiento,
        id_usuarios=usuario.id_usuarios,
        fecha=datos.fecha or date.today(),
        total=redondear(total_compra),
    )

    session.add(compra)
    session.commit()
    session.refresh(compra)

    for detalle in detalles_para_guardar:
        detalle_compra = DetalleCompra(
            id_compra=compra.id_compra,
            id_material=detalle["id_material"],
            cantidad=detalle["cantidad"],
            precio=detalle["precio"],
        )

        session.add(detalle_compra)

    session.commit()

    registrar_bitacora(
        session=session,
        id_usuario=usuario.id_usuarios,
        modulo="CU - Registrar Compra",
        accion="Registrar compra",
        descripcion=(
            f"Se registró la compra ID {compra.id_compra} "
            f"por un total de {compra.total} Bs."
        ),
    )

    return {
        "id_compra": compra.id_compra,
        "id_movimiento": movimiento.id_movimiento,
        "id_proveedor": compra.id_proveedor,
        "id_usuarios": compra.id_usuarios,
        "fecha": compra.fecha,
        "total": redondear(compra.total),
        "detalles": detalles_respuesta,
        "mensaje": "Compra registrada correctamente en la base de datos de la empresa."
    }


@router.get("")
def listar_compras(
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    """
    Lista las compras registradas en la empresa activa.
    """

    compras = session.exec(
        select(Compra).order_by(Compra.fecha.desc())
    ).all()

    return compras


@router.get("/{id_compra}")
def obtener_compra(
    id_compra: int,
    session: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador", "Empleado", "Cliente")),
):
    """
    Consulta una compra específica con su detalle dentro de la empresa activa.
    """

    compra = session.get(Compra, id_compra)

    if not compra:
        raise HTTPException(
            status_code=404,
            detail="Compra no encontrada en esta empresa."
        )

    detalles = session.exec(
        select(DetalleCompra).where(
            DetalleCompra.id_compra == id_compra
        )
    ).all()

    return {
        "compra": compra,
        "detalles": detalles,
    }