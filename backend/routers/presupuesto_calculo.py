from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from database_empresa import get_session_empresa
from models import Presupuesto, DetallePresupuesto, Material, ActivosFijos


router = APIRouter(
    prefix="/presupuesto-calculos",
    tags=["Presupuestos - Cálculos"]
)


def redondear(valor: Decimal) -> Decimal:
    return Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ============================================================
# 1. CÁLCULO SIMPLE POR METRO CUADRADO
# ============================================================

class CalculoPresupuestoSimpleRequest(BaseModel):
    id_proyecto: Optional[int] = None

    area_m2: Decimal = Field(..., gt=0)
    precio_m2_usd: Decimal = Field(..., gt=0)
    tipo_cambio: Decimal = Field(..., gt=0)

    porcentaje_indirectos: Decimal = Field(default=Decimal("0"), ge=0)
    porcentaje_utilidad: Decimal = Field(default=Decimal("0"), ge=0)
    porcentaje_impuestos: Decimal = Field(default=Decimal("0"), ge=0)

    guardar_en_bd: bool = False


class CalculoPresupuestoSimpleResponse(BaseModel):
    id_presupuesto: Optional[int]
    id_proyecto: Optional[int]

    area_m2: Decimal
    precio_m2_usd: Decimal
    tipo_cambio: Decimal

    costo_base_usd: Decimal
    costo_indirectos_usd: Decimal
    utilidad_usd: Decimal
    impuestos_usd: Decimal
    total_usd: Decimal

    costo_base_bob: Decimal
    costo_indirectos_bob: Decimal
    utilidad_bob: Decimal
    impuestos_bob: Decimal
    total_bob: Decimal

    mensaje: str


@router.post("/calcular-simple", response_model=CalculoPresupuestoSimpleResponse)
def calcular_presupuesto_simple(
    datos: CalculoPresupuestoSimpleRequest,
    session: Session = Depends(get_session_empresa),
):
    """
    Calcula presupuesto por metro cuadrado.

    Ejemplo:
    100 m2 x 17 USD = 1700 USD
    1700 USD x 6.96 = 11832 Bs

    Si guardar_en_bd=True, guarda el total en la tabla presupuesto
    de la base de datos de la empresa indicada por X-Empresa-Id.
    """

    costo_base_usd = datos.area_m2 * datos.precio_m2_usd

    costo_indirectos_usd = costo_base_usd * (
        datos.porcentaje_indirectos / Decimal("100")
    )

    subtotal_usd = costo_base_usd + costo_indirectos_usd

    utilidad_usd = subtotal_usd * (
        datos.porcentaje_utilidad / Decimal("100")
    )

    subtotal_con_utilidad_usd = subtotal_usd + utilidad_usd

    impuestos_usd = subtotal_con_utilidad_usd * (
        datos.porcentaje_impuestos / Decimal("100")
    )

    total_usd = subtotal_con_utilidad_usd + impuestos_usd

    costo_base_bob = costo_base_usd * datos.tipo_cambio
    costo_indirectos_bob = costo_indirectos_usd * datos.tipo_cambio
    utilidad_bob = utilidad_usd * datos.tipo_cambio
    impuestos_bob = impuestos_usd * datos.tipo_cambio
    total_bob = total_usd * datos.tipo_cambio

    id_presupuesto = None

    if datos.guardar_en_bd:
        presupuesto = Presupuesto(
            id_proyecto=datos.id_proyecto,
            costo_total=redondear(total_bob),
            fecha=date.today()
        )

        session.add(presupuesto)
        session.commit()
        session.refresh(presupuesto)

        id_presupuesto = presupuesto.id_presupuesto

    return {
        "id_presupuesto": id_presupuesto,
        "id_proyecto": datos.id_proyecto,

        "area_m2": datos.area_m2,
        "precio_m2_usd": datos.precio_m2_usd,
        "tipo_cambio": datos.tipo_cambio,

        "costo_base_usd": redondear(costo_base_usd),
        "costo_indirectos_usd": redondear(costo_indirectos_usd),
        "utilidad_usd": redondear(utilidad_usd),
        "impuestos_usd": redondear(impuestos_usd),
        "total_usd": redondear(total_usd),

        "costo_base_bob": redondear(costo_base_bob),
        "costo_indirectos_bob": redondear(costo_indirectos_bob),
        "utilidad_bob": redondear(utilidad_bob),
        "impuestos_bob": redondear(impuestos_bob),
        "total_bob": redondear(total_bob),

        "mensaje": "Presupuesto calculado correctamente en la base de datos de la empresa."
    }


# ============================================================
# 2. PRESUPUESTO CON MATERIALES
# ============================================================

class MaterialPresupuestoItem(BaseModel):
    id_material: int
    cantidad: int = Field(..., gt=0)


class CrearPresupuestoMaterialesRequest(BaseModel):
    id_proyecto: Optional[int] = None
    materiales: List[MaterialPresupuestoItem]


class DetalleMaterialResponse(BaseModel):
    id_material: int
    nombre: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class CrearPresupuestoMaterialesResponse(BaseModel):
    id_presupuesto: int
    id_proyecto: Optional[int]
    total: Decimal
    detalles: List[DetalleMaterialResponse]
    mensaje: str


@router.post("/crear-con-materiales", response_model=CrearPresupuestoMaterialesResponse)
def crear_presupuesto_con_materiales(
    datos: CrearPresupuestoMaterialesRequest,
    session: Session = Depends(get_session_empresa),
):
    """
    Crea un presupuesto usando materiales existentes de la base de datos
    de la empresa indicada por X-Empresa-Id.

    Fórmula:
    cantidad x material.precio = subtotal
    """

    if not datos.materiales:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un material."
        )

    total = Decimal("0")
    detalles_respuesta = []
    materiales_calculados = []

    for item in datos.materiales:
        material = session.get(Material, item.id_material)

        if not material:
            raise HTTPException(
                status_code=404,
                detail=f"Material con ID {item.id_material} no encontrado en esta empresa."
            )

        precio_unitario = Decimal(str(material.precio))
        subtotal = precio_unitario * Decimal(item.cantidad)

        total += subtotal

        materiales_calculados.append({
            "id_material": item.id_material,
            "cantidad": item.cantidad,
            "subtotal": subtotal
        })

        detalles_respuesta.append({
            "id_material": material.id_material,
            "nombre": material.nombre,
            "cantidad": item.cantidad,
            "precio_unitario": redondear(precio_unitario),
            "subtotal": redondear(subtotal)
        })

    presupuesto = Presupuesto(
        id_proyecto=datos.id_proyecto,
        costo_total=redondear(total),
        fecha=date.today()
    )

    session.add(presupuesto)
    session.commit()
    session.refresh(presupuesto)

    for detalle in materiales_calculados:
        detalle_presupuesto = DetallePresupuesto(
            id_presupuesto=presupuesto.id_presupuesto,
            id_material=detalle["id_material"],
            cantidad=detalle["cantidad"],
            costo=redondear(detalle["subtotal"])
        )

        session.add(detalle_presupuesto)

    session.commit()

    return {
        "id_presupuesto": presupuesto.id_presupuesto,
        "id_proyecto": presupuesto.id_proyecto,
        "total": redondear(total),
        "detalles": detalles_respuesta,
        "mensaje": "Presupuesto con materiales creado correctamente en la base de datos de la empresa."
    }


# ============================================================
# 3. CÁLCULO DE COSTO DE USO DE ACTIVO FIJO
# ============================================================

class CalculoActivoRequest(BaseModel):
    id_activo: int
    dias_uso: int = Field(..., gt=0)


class CalculoActivoResponse(BaseModel):
    id_activo: int
    nombre: str
    valor_compra: Decimal
    valor_residual: Decimal
    vida_util: int
    dias_uso: int
    depreciacion_total: Decimal
    costo_por_dia: Decimal
    costo_uso: Decimal
    mensaje: str


@router.post("/calcular-activo", response_model=CalculoActivoResponse)
def calcular_costo_activo(
    datos: CalculoActivoRequest,
    session: Session = Depends(get_session_empresa),
):
    """
    Calcula el costo de uso de un activo fijo registrado en la base
    de datos de la empresa indicada por X-Empresa-Id.

    Fórmula:
    depreciación total = valor_compra - valor_residual
    costo por día = depreciación total / vida_util
    costo de uso = costo por día x dias_uso
    """

    activo = session.get(ActivosFijos, datos.id_activo)

    if not activo:
        raise HTTPException(
            status_code=404,
            detail=f"Activo fijo con ID {datos.id_activo} no encontrado en esta empresa."
        )

    if activo.vida_util <= 0:
        raise HTTPException(
            status_code=400,
            detail="La vida útil del activo debe ser mayor a cero."
        )

    valor_compra = Decimal(str(activo.valor_compra))
    valor_residual = Decimal(str(activo.valor_residual))

    depreciacion_total = valor_compra - valor_residual
    costo_por_dia = depreciacion_total / Decimal(activo.vida_util)
    costo_uso = costo_por_dia * Decimal(datos.dias_uso)

    return {
        "id_activo": activo.id_activo,
        "nombre": activo.nombre,
        "valor_compra": redondear(valor_compra),
        "valor_residual": redondear(valor_residual),
        "vida_util": activo.vida_util,
        "dias_uso": datos.dias_uso,
        "depreciacion_total": redondear(depreciacion_total),
        "costo_por_dia": redondear(costo_por_dia),
        "costo_uso": redondear(costo_uso),
        "mensaje": "Costo de activo calculado correctamente en la base de datos de la empresa."
    }