from .auth import router as auth_router
from .auth_empresa import router as auth_empresa_router
from .ia import router as ia_router
from .presupuesto_calculo import router as presupuesto_calculo_router

from .sistema import routers as sistema_routers
from .comercial import routers as comercial_routers
from .financiero import routers as financiero_routers
from .compras import routers as compras_routers
from .proyectos import routers as proyectos_routers
from .empleados import routers as empleados_routers


def incluir_routers(app):
    todos_los_routers = (
        [auth_router, auth_empresa_router, ia_router, presupuesto_calculo_router]
        + sistema_routers
        + comercial_routers
        + financiero_routers
        + compras_routers
        + proyectos_routers
        + empleados_routers
    )

    for router in todos_los_routers:
        app.include_router(router)