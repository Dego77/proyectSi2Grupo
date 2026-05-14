from .cu06_reserva_online import router as cu06_reserva_online_router
from .cu10_consultas import router as cu10_consultas_router
from .cu11_historial_pagos import router as cu11_historial_pagos_router
from .cu14_perfiles_permisos import router as cu14_perfiles_permisos_router
from .cu31_mensajeria import router as cu31_mensajeria_router
from .cu32_notificaciones import router as cu32_notificaciones_router
from .cu33_pagos_proyecto import router as cu33_pagos_proyecto_router
from .registrar_proyecto import router as registrar_proyecto_router
from .registrar_compra import router as registrar_compra_router
from .registrar_venta import router as registrar_venta_router


routers = [
    cu06_reserva_online_router,
    cu10_consultas_router,
    cu11_historial_pagos_router,
    cu14_perfiles_permisos_router,
    cu31_mensajeria_router,
    cu32_notificaciones_router,
    cu33_pagos_proyecto_router,
    registrar_proyecto_router,
    registrar_compra_router,
    registrar_venta_router
]