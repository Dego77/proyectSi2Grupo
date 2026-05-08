from crud.factory import crear_crud_router

from models import MovimientoFinanciero, Pago


movimiento_financiero_router = crear_crud_router(
    modelo=MovimientoFinanciero,
    prefix="/movimientos-financieros",
    tags=["Financiero - Movimientos"],
    campos_pk=("id_movimiento",),
)

pago_router = crear_crud_router(
    modelo=Pago,
    prefix="/pagos",
    tags=["Financiero - Pagos"],
    campos_pk=("id_pago",),
)


routers = [
    movimiento_financiero_router,
    pago_router,
]