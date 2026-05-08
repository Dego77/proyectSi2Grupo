from crud.factory import crear_crud_router

from models import Empleados, Planillas


empleados_router = crear_crud_router(
    modelo=Empleados,
    prefix="/empleados",
    tags=["Empleados - Empleados"],
    campos_pk=("id_empleados",),
)

planillas_router = crear_crud_router(
    modelo=Planillas,
    prefix="/planillas",
    tags=["Empleados - Planillas"],
    campos_pk=("id_planillas",),
)


routers = [
    empleados_router,
    planillas_router,
]