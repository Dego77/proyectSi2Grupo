from crud.factory import crear_crud_router

from models import Cliente, Venta


cliente_router = crear_crud_router(
    modelo=Cliente,
    prefix="/clientes",
    tags=["Comercial - Clientes"],
    campos_pk=("id_cliente",),
)

venta_router = crear_crud_router(
    modelo=Venta,
    prefix="/ventas",
    tags=["Comercial - Ventas"],
    campos_pk=("id_venta",),
)


routers = [
    cliente_router,
    venta_router,
]