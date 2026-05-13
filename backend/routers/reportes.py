from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, select

from database_empresa import get_session_empresa
from models import (
    Proyecto,
    Material,
    Presupuesto,
    MovimientoFinanciero,
    Planillas,
    ActivosFijos,
    Usuario,
    Empleados,
)


router = APIRouter(
    prefix="/reportes",
    tags=["Reportes Multiempresa"]
)


def redondear(valor) -> Decimal:
    return Decimal(str(valor or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


class ReporteGeneralResponse(BaseModel):
    total_proyectos: int
    total_materiales: int
    total_usuarios: int
    total_empleados: int
    total_presupuestado_bob: Decimal
    total_ingresos_bob: Decimal
    total_egresos_bob: Decimal
    valor_total_activos_bob: Decimal
    valor_inventario_materiales_bob: Decimal


@router.get("/general", response_model=ReporteGeneralResponse)
def reporte_general(
    session: Session = Depends(get_session_empresa),
):
    total_proyectos = session.exec(
        select(func.count(Proyecto.id_proyecto))
    ).one()

    total_materiales = session.exec(
        select(func.count(Material.id_material))
    ).one()

    total_usuarios = session.exec(
        select(func.count(Usuario.id_usuarios))
    ).one()

    total_empleados = session.exec(
        select(func.count(Empleados.id_empleados))
    ).one()

    total_presupuestado = session.exec(
        select(func.coalesce(func.sum(Presupuesto.costo_total), 0))
    ).one()

    total_ingresos = session.exec(
        select(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))
        .where(func.lower(MovimientoFinanciero.tipo_movimiento) == "ingreso")
    ).one()

    total_egresos = session.exec(
        select(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))
        .where(func.lower(MovimientoFinanciero.tipo_movimiento) == "egreso")
    ).one()

    valor_total_activos = session.exec(
        select(func.coalesce(func.sum(ActivosFijos.valor_compra), 0))
    ).one()

    materiales = session.exec(select(Material)).all()

    valor_inventario = Decimal("0")

    for material in materiales:
        precio = Decimal(str(material.precio or 0))
        stock = Decimal(str(material.stock or 0))
        valor_inventario += precio * stock

    return {
        "total_proyectos": int(total_proyectos or 0),
        "total_materiales": int(total_materiales or 0),
        "total_usuarios": int(total_usuarios or 0),
        "total_empleados": int(total_empleados or 0),
        "total_presupuestado_bob": redondear(total_presupuestado),
        "total_ingresos_bob": redondear(total_ingresos),
        "total_egresos_bob": redondear(total_egresos),
        "valor_total_activos_bob": redondear(valor_total_activos),
        "valor_inventario_materiales_bob": redondear(valor_inventario),
    }


class ReporteProyectoResponse(BaseModel):
    id_proyecto: int
    nombre_proyecto: str
    ubicacion: str
    estado: str
    total_presupuestado_bob: Decimal
    total_ingresos_bob: Decimal
    total_egresos_bob: Decimal
    total_planillas_bob: Decimal
    valor_activos_bob: Decimal
    gasto_total_bob: Decimal
    saldo_estimado_bob: Decimal
    diferencia_presupuesto_vs_gasto_bob: Decimal


@router.get("/proyecto/{id_proyecto}", response_model=ReporteProyectoResponse)
def reporte_por_proyecto(
    id_proyecto: int,
    session: Session = Depends(get_session_empresa),
):
    proyecto = session.get(Proyecto, id_proyecto)

    if not proyecto:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado para esta empresa."
        )

    total_presupuestado = session.exec(
        select(func.coalesce(func.sum(Presupuesto.costo_total), 0))
        .where(Presupuesto.id_proyecto == id_proyecto)
    ).one()

    total_ingresos = session.exec(
        select(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))
        .where(
            MovimientoFinanciero.id_proyecto == id_proyecto,
            func.lower(MovimientoFinanciero.tipo_movimiento) == "ingreso"
        )
    ).one()

    total_egresos = session.exec(
        select(func.coalesce(func.sum(MovimientoFinanciero.monto), 0))
        .where(
            MovimientoFinanciero.id_proyecto == id_proyecto,
            func.lower(MovimientoFinanciero.tipo_movimiento) == "egreso"
        )
    ).one()

    total_planillas = session.exec(
        select(func.coalesce(func.sum(Planillas.pago), 0))
        .where(Planillas.id_proyecto == id_proyecto)
    ).one()

    valor_activos = session.exec(
        select(func.coalesce(func.sum(ActivosFijos.valor_compra), 0))
        .where(ActivosFijos.id_proyecto == id_proyecto)
    ).one()

    gasto_total = redondear(total_egresos) + redondear(total_planillas)
    saldo_estimado = redondear(total_ingresos) - gasto_total
    diferencia_presupuesto = redondear(total_presupuestado) - gasto_total

    return {
        "id_proyecto": proyecto.id_proyecto,
        "nombre_proyecto": proyecto.nombre,
        "ubicacion": proyecto.ubicacion,
        "estado": proyecto.estado,
        "total_presupuestado_bob": redondear(total_presupuestado),
        "total_ingresos_bob": redondear(total_ingresos),
        "total_egresos_bob": redondear(total_egresos),
        "total_planillas_bob": redondear(total_planillas),
        "valor_activos_bob": redondear(valor_activos),
        "gasto_total_bob": redondear(gasto_total),
        "saldo_estimado_bob": redondear(saldo_estimado),
        "diferencia_presupuesto_vs_gasto_bob": redondear(diferencia_presupuesto),
    }


class MaterialStockItem(BaseModel):
    id_material: int
    nombre: str
    precio: Decimal
    stock: int
    valor_total_bob: Decimal
    estado_stock: str


@router.get("/materiales-stock", response_model=List[MaterialStockItem])
def reporte_materiales_stock(
    session: Session = Depends(get_session_empresa),
):
    materiales = session.exec(
        select(Material).order_by(Material.stock)
    ).all()

    respuesta = []

    for material in materiales:
        precio = Decimal(str(material.precio or 0))
        stock = int(material.stock or 0)
        valor_total = precio * Decimal(stock)

        if stock <= 0:
            estado_stock = "Sin stock"
        elif stock <= 10:
            estado_stock = "Stock bajo"
        elif stock <= 50:
            estado_stock = "Stock medio"
        else:
            estado_stock = "Stock suficiente"

        respuesta.append({
            "id_material": material.id_material,
            "nombre": material.nombre,
            "precio": redondear(precio),
            "stock": stock,
            "valor_total_bob": redondear(valor_total),
            "estado_stock": estado_stock,
        })

    return respuesta


class ActivoFijoReporteItem(BaseModel):
    id_activo: int
    id_proyecto: Optional[int]
    nombre: str
    tipo_activo: str
    codigo_activo: str
    valor_compra: Decimal
    valor_residual: Decimal
    vida_util: int
    depreciacion_total: Decimal
    costo_por_dia: Decimal
    estado: str


@router.get("/activos-fijos", response_model=List[ActivoFijoReporteItem])
def reporte_activos_fijos(
    session: Session = Depends(get_session_empresa),
):
    activos = session.exec(select(ActivosFijos)).all()

    respuesta = []

    for activo in activos:
        valor_compra = Decimal(str(activo.valor_compra or 0))
        valor_residual = Decimal(str(activo.valor_residual or 0))
        vida_util = Decimal(str(activo.vida_util or 1))

        depreciacion_total = valor_compra - valor_residual
        costo_por_dia = depreciacion_total / vida_util

        respuesta.append({
            "id_activo": activo.id_activo,
            "id_proyecto": activo.id_proyecto,
            "nombre": activo.nombre,
            "tipo_activo": activo.tipo_activo,
            "codigo_activo": activo.codigo_activo,
            "valor_compra": redondear(valor_compra),
            "valor_residual": redondear(valor_residual),
            "vida_util": activo.vida_util,
            "depreciacion_total": redondear(depreciacion_total),
            "costo_por_dia": redondear(costo_por_dia),
            "estado": activo.estado,
        })

    return respuesta