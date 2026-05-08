from crud.factory import crear_crud_router

from models import Proyecto, Presupuesto, DetallePresupuesto, ActivosFijos


proyecto_router = crear_crud_router(
    modelo=Proyecto,
    prefix="/proyectos",
    tags=["Proyectos - Proyectos"],
    campos_pk=("id_proyecto",),
)

presupuesto_router = crear_crud_router(
    modelo=Presupuesto,
    prefix="/presupuestos",
    tags=["Proyectos - Presupuestos"],
    campos_pk=("id_presupuesto",),
)

detalle_presupuesto_router = crear_crud_router(
    modelo=DetallePresupuesto,
    prefix="/detalle-presupuestos",
    tags=["Proyectos - Detalle presupuestos"],
    campos_pk=("id_presupuesto", "id_material"),
)

activos_fijos_router = crear_crud_router(
    modelo=ActivosFijos,
    prefix="/activos-fijos",
    tags=["Proyectos - Activos fijos"],
    campos_pk=("id_activo",),
)


routers = [
    proyecto_router,
    presupuesto_router,
    detalle_presupuesto_router,
    activos_fijos_router,
]