import os
import uuid
from pathlib import Path
from decimal import Decimal

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from sqlalchemy import func

from utils.ia_gemini import responder_con_gemini
from utils.transcripcion_audio import transcribir_audio

from database_empresa import get_session_empresa
from models import (
    Proyecto,
    Material,
    Presupuesto,
    MovimientoFinanciero,
    Planillas,
    ActivosFijos,
    Empleados,
    Cliente,
    Venta,
    Pago,
    Compra,
    Proveedor,
    DetalleCompra,
)


router = APIRouter(
    prefix="/ia",
    tags=["IA - Gemini y Audio"]
)


# ============================================================
# MODELOS DE REQUEST / RESPONSE
# ============================================================

class PreguntaIARequest(BaseModel):
    pregunta: str = Field(..., min_length=2)


class PreguntaIAResponse(BaseModel):
    tipo: str
    pregunta: str
    respuesta: str


class AudioIAResponse(BaseModel):
    tipo: str
    transcripcion: str
    respuesta: str


class PreguntaIAContextoRequest(BaseModel):
    pregunta: str = Field(..., min_length=2)


class PreguntaIAContextoResponse(BaseModel):
    tipo: str
    pregunta: str
    contexto_usado: str
    respuesta: str


class AudioIAContextoResponse(BaseModel):
    tipo: str
    transcripcion: str
    contexto_usado: str
    respuesta: str


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def redondear_valor(valor) -> str:
    if valor is None:
        return "0.00"

    try:
        return str(Decimal(str(valor)).quantize(Decimal("0.01")))
    except Exception:
        return str(valor)


def construir_contexto_empresa(session: Session) -> str:
    # ============================================================
    # RESUMEN GENERAL
    # ============================================================

    total_proyectos = session.exec(
        select(func.count(Proyecto.id_proyecto))
    ).one()

    total_materiales = session.exec(
        select(func.count(Material.id_material))
    ).one()

    total_empleados = session.exec(
        select(func.count(Empleados.id_empleados))
    ).one()

    total_clientes = session.exec(
        select(func.count(Cliente.id_cliente))
    ).one()

    total_proveedores = session.exec(
        select(func.count(Proveedor.id_proveedor))
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

    total_planillas = session.exec(
        select(func.coalesce(func.sum(Planillas.pago), 0))
    ).one()

    valor_activos = session.exec(
        select(func.coalesce(func.sum(ActivosFijos.valor_compra), 0))
    ).one()

    total_ventas = session.exec(
        select(func.coalesce(func.sum(Venta.total), 0))
    ).one()

    total_compras = session.exec(
        select(func.coalesce(func.sum(Compra.total), 0))
    ).one()

    total_pagos = session.exec(
        select(func.coalesce(func.sum(Pago.monto), 0))
    ).one()

    pagos_pendientes = session.exec(
        select(func.coalesce(func.sum(Pago.monto), 0))
        .where(func.lower(Pago.estado) == "pendiente")
    ).one()

    pagos_completados = session.exec(
        select(func.coalesce(func.sum(Pago.monto), 0))
        .where(func.lower(Pago.estado) == "completado")
    ).one()

    # ============================================================
    # LISTAS PRINCIPALES
    # ============================================================

    proyectos = session.exec(
        select(Proyecto).limit(10)
    ).all()

    materiales_principales = session.exec(
        select(Material)
        .order_by(Material.stock)
        .limit(10)
    ).all()

    materiales_bajo_stock = session.exec(
        select(Material)
        .where(Material.stock <= 10)
        .order_by(Material.stock)
        .limit(10)
    ).all()

    activos = session.exec(
        select(ActivosFijos).limit(10)
    ).all()

    clientes = session.exec(
        select(Cliente).limit(10)
    ).all()

    proveedores = session.exec(
        select(Proveedor).limit(10)
    ).all()

    ventas = session.exec(
        select(Venta)
        .order_by(Venta.fecha)
        .limit(10)
    ).all()

    compras = session.exec(
        select(Compra)
        .order_by(Compra.fecha)
        .limit(10)
    ).all()

    pagos = session.exec(
        select(Pago)
        .order_by(Pago.fecha)
        .limit(10)
    ).all()

    detalles_compra = session.exec(
        select(DetalleCompra).limit(15)
    ).all()

    # ============================================================
    # FORMATEO DE LISTAS
    # ============================================================

    lista_proyectos = "\n".join(
        [
            f"- ID {p.id_proyecto}: {p.nombre}, ubicación: {p.ubicacion}, estado: {p.estado}"
            for p in proyectos
        ]
    ) or "No hay proyectos registrados."

    lista_materiales = "\n".join(
        [
            f"- ID {m.id_material}: {m.nombre}, stock: {m.stock}, precio: {m.precio} Bs"
            for m in materiales_principales
        ]
    ) or "No hay materiales registrados."

    lista_materiales_bajo_stock = "\n".join(
        [
            f"- {m.nombre}: stock {m.stock}, precio {m.precio} Bs"
            for m in materiales_bajo_stock
        ]
    ) or "No hay materiales con stock bajo."

    lista_activos = "\n".join(
        [
            f"- ID {a.id_activo}: {a.nombre}, tipo: {a.tipo_activo}, valor compra: {a.valor_compra} Bs, estado: {a.estado}"
            for a in activos
        ]
    ) or "No hay activos fijos registrados."

    lista_clientes = "\n".join(
        [
            f"- ID {c.id_cliente}: {c.nombre}, teléfono: {c.telefono}, dirección: {c.direccion}"
            for c in clientes
        ]
    ) or "No hay clientes registrados."

    lista_proveedores = "\n".join(
        [
            f"- ID {p.id_proveedor}: {p.nombre}, contacto: {p.contacto}"
            for p in proveedores
        ]
    ) or "No hay proveedores registrados."

    lista_ventas = "\n".join(
        [
            f"- ID {v.id_venta}: cliente ID {v.id_cliente}, total: {v.total} Bs, fecha: {v.fecha}"
            for v in ventas
        ]
    ) or "No hay ventas registradas."

    lista_compras = "\n".join(
        [
            f"- ID {c.id_compra}: proveedor ID {c.id_proveedor}, total: {c.total} Bs, fecha: {c.fecha}"
            for c in compras
        ]
    ) or "No hay compras registradas."

    lista_pagos = "\n".join(
        [
            f"- ID {p.id_pago}: proyecto ID {p.id_proyecto}, monto: {p.monto} Bs, estado: {p.estado}, método: {p.metodo_pago}, fecha: {p.fecha}"
            for p in pagos
        ]
    ) or "No hay pagos registrados."

    lista_detalle_compras = []

    for detalle in detalles_compra:
        material = session.get(Material, detalle.id_material)
        compra = session.get(Compra, detalle.id_compra)

        nombre_material = material.nombre if material else f"Material ID {detalle.id_material}"
        id_compra = compra.id_compra if compra else detalle.id_compra

        lista_detalle_compras.append(
            f"- Compra ID {id_compra}: {nombre_material}, cantidad: {detalle.cantidad}, precio: {detalle.precio} Bs"
        )

    lista_detalle_compras = "\n".join(lista_detalle_compras) or "No hay detalles de compra registrados."

    # ============================================================
    # CONTEXTO FINAL PARA GEMINI
    # ============================================================

    contexto = f"""
DATOS ACTUALES DE LA EMPRESA

Resumen general:
- Total de proyectos: {total_proyectos}
- Total de materiales: {total_materiales}
- Total de empleados: {total_empleados}
- Total de clientes: {total_clientes}
- Total de proveedores: {total_proveedores}
- Total presupuestado: {redondear_valor(total_presupuestado)} Bs
- Total ingresos: {redondear_valor(total_ingresos)} Bs
- Total egresos: {redondear_valor(total_egresos)} Bs
- Total planillas: {redondear_valor(total_planillas)} Bs
- Valor total de activos fijos: {redondear_valor(valor_activos)} Bs
- Total ventas: {redondear_valor(total_ventas)} Bs
- Total compras: {redondear_valor(total_compras)} Bs
- Total pagos registrados: {redondear_valor(total_pagos)} Bs
- Pagos pendientes: {redondear_valor(pagos_pendientes)} Bs
- Pagos completados: {redondear_valor(pagos_completados)} Bs

Proyectos registrados:
{lista_proyectos}

Materiales principales:
{lista_materiales}

Materiales con stock bajo:
{lista_materiales_bajo_stock}

Activos fijos:
{lista_activos}

Clientes:
{lista_clientes}

Proveedores:
{lista_proveedores}

Ventas recientes:
{lista_ventas}

Compras recientes:
{lista_compras}

Pagos recientes:
{lista_pagos}

Detalle de compras:
{lista_detalle_compras}
"""

    return contexto


def responder_con_contexto_empresa(pregunta: str, session: Session) -> tuple[str, str]:
    contexto_empresa = construir_contexto_empresa(session)

    prompt = f"""
Eres un asistente inteligente para un sistema multiempresa de construcción.

Debes responder en español, de forma clara, útil y directa.

Tienes dos funciones:
1. Si la pregunta es general, responde normalmente.
2. Si la pregunta trata sobre la empresa, proyectos, materiales, presupuestos, empleados, activos, stock, compras, egresos o ingresos, usa estrictamente los datos reales entregados desde PostgreSQL.

No inventes datos que no estén en el contexto.
Si un dato no existe o no está registrado, dilo claramente.
Si los valores están en cero, explica que aún no existen registros suficientes.

Contexto real de la empresa:
{contexto_empresa}

Pregunta del usuario:
{pregunta}
"""

    respuesta = responder_con_gemini(prompt)

    return contexto_empresa, respuesta


async def guardar_audio_temporal(audio: UploadFile) -> Path:
    extensiones_permitidas = [".mp3", ".wav", ".m4a", ".ogg", ".webm", ".mp4"]

    nombre_original = audio.filename or ""
    extension = Path(nombre_original).suffix.lower()

    if extension not in extensiones_permitidas:
        raise HTTPException(
            status_code=400,
            detail="Formato de audio no permitido. Usa mp3, wav, m4a, ogg, webm o mp4."
        )

    carpeta_temporal = Path("temp_audio")
    carpeta_temporal.mkdir(exist_ok=True)

    nombre_temporal = f"{uuid.uuid4()}{extension}"
    ruta_temporal = carpeta_temporal / nombre_temporal

    contenido = await audio.read()

    if not contenido:
        raise HTTPException(
            status_code=400,
            detail="El archivo de audio está vacío."
        )

    with open(ruta_temporal, "wb") as archivo:
        archivo.write(contenido)

    return ruta_temporal


# ============================================================
# 1. IA GENERAL POR TEXTO
# ============================================================

@router.post("/preguntar", response_model=PreguntaIAResponse)
def preguntar_ia(datos: PreguntaIARequest):
    try:
        respuesta = responder_con_gemini(datos.pregunta)

        return {
            "tipo": "texto",
            "pregunta": datos.pregunta,
            "respuesta": respuesta
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar Gemini: {str(error)}"
        )


# ============================================================
# 2. IA GENERAL POR AUDIO
# ============================================================

@router.post("/preguntar-audio", response_model=AudioIAResponse)
async def preguntar_ia_con_audio(audio: UploadFile = File(...)):
    ruta_temporal = None

    try:
        ruta_temporal = await guardar_audio_temporal(audio)

        transcripcion = transcribir_audio(str(ruta_temporal))

        if not transcripcion or transcripcion == "No se pudo transcribir el audio.":
            raise HTTPException(
                status_code=400,
                detail="No se pudo transcribir el audio."
            )

        pregunta_para_ia = f"""
El usuario envió un audio. Esta es la transcripción:

{transcripcion}

Responde a lo que el usuario pidió en el audio.
"""

        respuesta = responder_con_gemini(pregunta_para_ia)

        return {
            "tipo": "audio",
            "transcripcion": transcripcion,
            "respuesta": respuesta
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el audio con IA: {str(error)}"
        )

    finally:
        if ruta_temporal and ruta_temporal.exists():
            try:
                os.remove(ruta_temporal)
            except Exception:
                pass


# ============================================================
# 3. IA CON DATOS DE LA EMPRESA POR TEXTO
# ============================================================

@router.post("/preguntar-contexto", response_model=PreguntaIAContextoResponse)
def preguntar_ia_con_contexto(
    datos: PreguntaIAContextoRequest,
    session: Session = Depends(get_session_empresa),
):
    try:
        contexto_empresa, respuesta = responder_con_contexto_empresa(
            pregunta=datos.pregunta,
            session=session,
        )

        return {
            "tipo": "texto_con_contexto_empresa",
            "pregunta": datos.pregunta,
            "contexto_usado": "Datos consultados desde PostgreSQL según X-Empresa-Id.",
            "respuesta": respuesta,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar IA con contexto de empresa: {str(error)}"
        )


# ============================================================
# 4. IA CON DATOS DE LA EMPRESA POR AUDIO
# ============================================================

@router.post("/preguntar-audio-contexto", response_model=AudioIAContextoResponse)
async def preguntar_ia_con_audio_contexto(
    audio: UploadFile = File(...),
    session: Session = Depends(get_session_empresa),
):
    ruta_temporal = None

    try:
        ruta_temporal = await guardar_audio_temporal(audio)

        transcripcion = transcribir_audio(str(ruta_temporal))

        if not transcripcion or transcripcion == "No se pudo transcribir el audio.":
            raise HTTPException(
                status_code=400,
                detail="No se pudo transcribir el audio."
            )

        contexto_empresa, respuesta = responder_con_contexto_empresa(
            pregunta=transcripcion,
            session=session,
        )

        return {
            "tipo": "audio_con_contexto_empresa",
            "transcripcion": transcripcion,
            "contexto_usado": "Datos consultados desde PostgreSQL según X-Empresa-Id.",
            "respuesta": respuesta,
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar audio con contexto de empresa: {str(error)}"
        )

    finally:
        if ruta_temporal and ruta_temporal.exists():
            try:
                os.remove(ruta_temporal)
            except Exception:
                pass