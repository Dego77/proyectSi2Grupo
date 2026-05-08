from typing import Any, Dict, List, Type

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session, select
from sqlalchemy.exc import SQLAlchemyError

from database import get_session

# Empresa  
def convertir_a_dict(objeto):
    if hasattr(objeto, "model_dump"):
        return objeto.model_dump()
    return objeto.dict()


def crear_objeto(modelo: Type[SQLModel], data: Dict[str, Any]):
    try:
        return modelo(**data)
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Datos inválidos para {modelo.__name__}: {str(error)}",
        )


def manejar_error_bd(session: Session, error: SQLAlchemyError):
    session.rollback()
    detalle = str(getattr(error, "orig", error))
    raise HTTPException(status_code=400, detail=detalle)


def crear_crud_router(
    modelo: Type[SQLModel],
    prefix: str,
    tags: list[str],
    campos_pk: tuple[str, ...],
):
    router = APIRouter(prefix=prefix, tags=tags)

    nombre_ruta = prefix.strip("/").replace("-", "_").replace("/", "_")

    def listar(session: Session = Depends(get_session)):
        return session.exec(select(modelo)).all()

    listar.__name__ = f"listar_{nombre_ruta}"

    router.add_api_route(
        "",
        listar,
        methods=["GET"],
        summary=f"Listar {prefix}",
        response_model=List[modelo],
    )

    def crear(data: Dict[str, Any], session: Session = Depends(get_session)):
        objeto = crear_objeto(modelo, data)

        try:
            session.add(objeto)
            session.commit()
            session.refresh(objeto)
            return objeto
        except SQLAlchemyError as error:
            manejar_error_bd(session, error)

    crear.__name__ = f"crear_{nombre_ruta}"

    router.add_api_route(
        "",
        crear,
        methods=["POST"],
        summary=f"Crear {prefix}",
        response_model=modelo,
    )

    if len(campos_pk) == 1:
        campo_pk = campos_pk[0]

        def obtener(item_id: int, session: Session = Depends(get_session)):
            objeto = session.get(modelo, item_id)

            if not objeto:
                raise HTTPException(
                    status_code=404,
                    detail=f"{modelo.__name__} no encontrado",
                )

            return objeto

        obtener.__name__ = f"obtener_{nombre_ruta}"

        router.add_api_route(
            "/{item_id}",
            obtener,
            methods=["GET"],
            summary=f"Obtener {prefix} por ID",
            response_model=modelo,
        )

        def actualizar(
            item_id: int,
            data: Dict[str, Any],
            session: Session = Depends(get_session),
        ):
            objeto = session.get(modelo, item_id)

            if not objeto:
                raise HTTPException(
                    status_code=404,
                    detail=f"{modelo.__name__} no encontrado",
                )

            datos_actuales = convertir_a_dict(objeto)
            datos_nuevos = {**datos_actuales, **data}
            datos_nuevos[campo_pk] = item_id

            objeto_validado = crear_objeto(modelo, datos_nuevos)

            for campo, valor in convertir_a_dict(objeto_validado).items():
                if campo != campo_pk:
                    setattr(objeto, campo, valor)

            try:
                session.add(objeto)
                session.commit()
                session.refresh(objeto)
                return objeto
            except SQLAlchemyError as error:
                manejar_error_bd(session, error)

        actualizar.__name__ = f"actualizar_{nombre_ruta}"

        router.add_api_route(
            "/{item_id}",
            actualizar,
            methods=["PUT"],
            summary=f"Actualizar {prefix} por ID",
            response_model=modelo,
        )

        def eliminar(item_id: int, session: Session = Depends(get_session)):
            objeto = session.get(modelo, item_id)

            if not objeto:
                raise HTTPException(
                    status_code=404,
                    detail=f"{modelo.__name__} no encontrado",
                )

            try:
                session.delete(objeto)
                session.commit()
                return {"mensaje": f"{modelo.__name__} eliminado correctamente"}
            except SQLAlchemyError as error:
                manejar_error_bd(session, error)

        eliminar.__name__ = f"eliminar_{nombre_ruta}"

        router.add_api_route(
            "/{item_id}",
            eliminar,
            methods=["DELETE"],
            summary=f"Eliminar {prefix} por ID",
        )

    else:
        def obtener_compuesto(
            pk1: int,
            pk2: int,
            session: Session = Depends(get_session),
        ):
            objeto = session.get(modelo, (pk1, pk2))

            if not objeto:
                raise HTTPException(
                    status_code=404,
                    detail=f"{modelo.__name__} no encontrado",
                )

            return objeto

        obtener_compuesto.__name__ = f"obtener_{nombre_ruta}"

        router.add_api_route(
            "/{pk1}/{pk2}",
            obtener_compuesto,
            methods=["GET"],
            summary=f"Obtener {prefix} por clave compuesta",
            response_model=modelo,
        )

        def actualizar_compuesto(
            pk1: int,
            pk2: int,
            data: Dict[str, Any],
            session: Session = Depends(get_session),
        ):
            objeto = session.get(modelo, (pk1, pk2))

            if not objeto:
                raise HTTPException(
                    status_code=404,
                    detail=f"{modelo.__name__} no encontrado",
                )

            datos_actuales = convertir_a_dict(objeto)
            datos_nuevos = {**datos_actuales, **data}
            datos_nuevos[campos_pk[0]] = pk1
            datos_nuevos[campos_pk[1]] = pk2

            objeto_validado = crear_objeto(modelo, datos_nuevos)

            for campo, valor in convertir_a_dict(objeto_validado).items():
                if campo not in campos_pk:
                    setattr(objeto, campo, valor)

            try:
                session.add(objeto)
                session.commit()
                session.refresh(objeto)
                return objeto
            except SQLAlchemyError as error:
                manejar_error_bd(session, error)

        actualizar_compuesto.__name__ = f"actualizar_{nombre_ruta}"

        router.add_api_route(
            "/{pk1}/{pk2}",
            actualizar_compuesto,
            methods=["PUT"],
            summary=f"Actualizar {prefix} por clave compuesta",
            response_model=modelo,
        )

        def eliminar_compuesto(
            pk1: int,
            pk2: int,
            session: Session = Depends(get_session),
        ):
            objeto = session.get(modelo, (pk1, pk2))

            if not objeto:
                raise HTTPException(
                    status_code=404,
                    detail=f"{modelo.__name__} no encontrado",
                )

            try:
                session.delete(objeto)
                session.commit()
                return {"mensaje": f"{modelo.__name__} eliminado correctamente"}
            except SQLAlchemyError as error:
                manejar_error_bd(session, error)

        eliminar_compuesto.__name__ = f"eliminar_{nombre_ruta}"

        router.add_api_route(
            "/{pk1}/{pk2}",
            eliminar_compuesto,
            methods=["DELETE"],
            summary=f"Eliminar {prefix} por clave compuesta",
        )

    return router