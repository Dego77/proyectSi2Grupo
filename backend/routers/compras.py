from crud.factory import crear_crud_router

from models import Material, Proveedor, Compra, DetalleCompra


material_router = crear_crud_router(
    modelo=Material,
    prefix="/materiales",
    tags=["Compras - Materiales"],
    campos_pk=("id_material",),
)

proveedor_router = crear_crud_router(
    modelo=Proveedor,
    prefix="/proveedores",
    tags=["Compras - Proveedores"],
    campos_pk=("id_proveedor",),
)

compra_router = crear_crud_router(
    modelo=Compra,
    prefix="/compras",
    tags=["Compras - Compras"],
    campos_pk=("id_compra",),
)

detalle_compra_router = crear_crud_router(
    modelo=DetalleCompra,
    prefix="/detalle-compras",
    tags=["Compras - Detalle compras"],
    campos_pk=("id",),
)


routers = [
    material_router,
    proveedor_router,
    compra_router,
    detalle_compra_router,
]