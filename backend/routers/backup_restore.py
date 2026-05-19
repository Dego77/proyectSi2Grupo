import json
import os
import platform
import re
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from zoneinfo import ZoneInfo
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.engine import make_url
from sqlmodel import Session, select

from database import get_session
from database_empresa import get_session_empresa
from models import BaseDeDatosEmpresa
from utils.seguridad_roles import requerir_roles
from utils.bitacora import registrar_bitacora


load_dotenv()


router = APIRouter(
    prefix="/backup-restore",
    tags=["Backup / Restore Multiempresa"]
)


@dataclass
class DBConfig:
    nombre_bd: str
    host: str
    puerto: int
    usuario: str
    password: str


# ============================================================
# UTILIDADES DE FECHA / HORA
# ============================================================

def obtener_fecha_hora_bolivia():
    return datetime.now(ZoneInfo("America/La_Paz"))


def obtener_fecha_archivo() -> str:
    """
    Formato seguro para nombres de archivo en Windows.
    Ejemplo: 2026-05-17_23-30
    """
    return obtener_fecha_hora_bolivia().strftime("%Y-%m-%d_%H-%M")


def obtener_fecha_hora_legible() -> str:
    """
    Formato visible para respuestas y manifest.
    Ejemplo: 2026-05-17 23:30:00
    """
    return obtener_fecha_hora_bolivia().strftime("%Y-%m-%d %H:%M:%S")


def obtener_zona_horaria() -> str:
    return "America/La_Paz"

def requerir_backup_admin(
    x_backup_token: str = Header(..., alias="X-Backup-Token"),
):
    token_configurado = os.getenv("BACKUP_ADMIN_TOKEN")

    if not token_configurado:
        raise HTTPException(
            status_code=500,
            detail="Falta BACKUP_ADMIN_TOKEN en el archivo .env."
        )

    if x_backup_token != token_configurado:
        raise HTTPException(
            status_code=403,
            detail="Token de administrador de backup inválido."
        )

    return True


def limpiar_nombre_archivo(texto: str) -> str:
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9_]+", "_", texto)
    texto = texto.strip("_")
    return texto[:80] or "base_datos"


# ============================================================
# CONFIGURACIÓN DE CARPETAS Y COMANDOS POSTGRESQL
# ============================================================

def obtener_carpeta_backups() -> Path:
    backup_dir = os.getenv("BACKUP_DIR", "backups")
    carpeta = Path(backup_dir)
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


def obtener_comando_postgres(nombre_comando: str) -> str:
    """
    Devuelve la ruta de pg_dump o psql.
    En Windows puede usar POSTGRES_BIN_PATH.
    """

    postgres_bin_path = os.getenv("POSTGRES_BIN_PATH")

    if postgres_bin_path:
        extension = ".exe" if platform.system().lower() == "windows" else ""
        return str(Path(postgres_bin_path) / f"{nombre_comando}{extension}")

    return nombre_comando


def ejecutar_comando_postgres(
    comando: list[str],
    password: str,
):
    env = os.environ.copy()
    env["PGPASSWORD"] = password or ""

    try:
        resultado = subprocess.run(
            comando,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=(
                "No se encontró pg_dump/psql. Agrega PostgreSQL al PATH "
                "o configura POSTGRES_BIN_PATH en tu .env."
            )
        )

    if resultado.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "mensaje": "Error ejecutando comando PostgreSQL.",
                "comando": comando,
                "stdout": resultado.stdout,
                "stderr": resultado.stderr,
            }
        )

    return resultado


# ============================================================
# CONFIGURACIÓN BASE CENTRAL Y EMPRESAS
# ============================================================

def obtener_config_central() -> DBConfig:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise HTTPException(
            status_code=500,
            detail="Falta DATABASE_URL en el archivo .env."
        )

    try:
        url = make_url(database_url)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"DATABASE_URL inválido: {str(error)}"
        )

    if not url.database or not url.username:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL debe incluir usuario y nombre de base de datos."
        )

    return DBConfig(
        nombre_bd=url.database,
        host=url.host or "127.0.0.1",
        puerto=int(url.port or 5432),
        usuario=url.username,
        password=url.password or "",
    )


def obtener_config_empresa(
    x_empresa_id: int,
    session_central: Session,
) -> BaseDeDatosEmpresa:
    config = session_central.exec(
        select(BaseDeDatosEmpresa).where(
            BaseDeDatosEmpresa.id_empresa == x_empresa_id,
            BaseDeDatosEmpresa.estado == True,
        )
    ).first()

    if not config:
        raise HTTPException(
            status_code=404,
            detail="No se encontró una base de datos activa para esta empresa."
        )

    return config


def convertir_config_empresa(config: BaseDeDatosEmpresa) -> DBConfig:
    return DBConfig(
        nombre_bd=config.nombre_bd,
        host=config.host,
        puerto=config.puerto,
        usuario=config.usuario_bd,
        password=config.password_bd,
    )


def listar_empresas_activas(session_central: Session):
    return session_central.exec(
        select(BaseDeDatosEmpresa).where(
            BaseDeDatosEmpresa.estado == True
        )
    ).all()


# ============================================================
# BACKUP / RESTORE SQL
# ============================================================

def generar_backup_sql(
    config: DBConfig,
    ruta_salida: Path,
):
    pg_dump = obtener_comando_postgres("pg_dump")

    comando = [
        pg_dump,
        "-h", config.host,
        "-p", str(config.puerto),
        "-U", config.usuario,
        "-d", config.nombre_bd,
        "--clean",
        "--if-exists",
        "--column-inserts",
        "--no-owner",
        "--no-privileges",
        "-f", str(ruta_salida),
    ]

    ejecutar_comando_postgres(
        comando=comando,
        password=config.password,
    )


def restaurar_sql(
    config: DBConfig,
    ruta_sql: Path,
):
    psql = obtener_comando_postgres("psql")

    comando = [
        psql,
        "-h", config.host,
        "-p", str(config.puerto),
        "-U", config.usuario,
        "-d", config.nombre_bd,
        "-v", "ON_ERROR_STOP=1",
        "-f", str(ruta_sql),
    ]

    ejecutar_comando_postgres(
        comando=comando,
        password=config.password,
    )


async def guardar_upload_temporal_async(
    archivo: UploadFile,
    extension: str,
) -> Path:
    if not archivo.filename or not archivo.filename.lower().endswith(extension):
        raise HTTPException(
            status_code=400,
            detail=f"Solo se permiten archivos {extension}."
        )

    contenido = await archivo.read()

    if not contenido:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío."
        )

    temp = NamedTemporaryFile(delete=False, suffix=extension)
    temp.write(contenido)
    temp.close()

    return Path(temp.name)


def registrar_evento_bitacora(
    session_empresa: Session,
    usuario_actual,
    accion: str,
    descripcion: str,
):
    try:
        usuario = usuario_actual.get("usuario")

        if usuario:
            registrar_bitacora(
                session=session_empresa,
                id_usuario=usuario.id_usuarios,
                modulo="Backup / Restore",
                accion=accion,
                descripcion=descripcion,
            )
    except Exception:
        session_empresa.rollback()
        
def registrar_evento_backup_sistema(
    accion: str,
    descripcion: str,
):
    carpeta = obtener_carpeta_backups()
    ruta_log = carpeta / "backup_restore_auditoria.log"

    with open(ruta_log, "a", encoding="utf-8") as archivo:
        archivo.write(
            f"[{obtener_fecha_hora_legible()}] {accion}: {descripcion}\n"
        )


# ============================================================
# 1. BACKUP / RESTORE BASE CENTRAL
# ============================================================

@router.get("/central/backup",
            summary="Descargar backup de la base central",
            description=(
                 "Genera y descarga un archivo SQL de la base central del sistema. "
                 "Incluye empresa, base_de_datos_empresa y configuración SaaS."
                ),
               response_description="Archivo SQL descargable de la base central."
            )
def backup_base_central(
    autorizado: bool = Depends(requerir_backup_admin),
):
    """
    Genera backup SQL de la base central.

    Incluye:
    - empresa
    - base_de_datos_empresa
    - configuraciones SaaS
    """

    config = obtener_config_central()
    carpeta = obtener_carpeta_backups()
    fecha = obtener_fecha_archivo()

    nombre_seguro = limpiar_nombre_archivo(config.nombre_bd)
    nombre_archivo = f"descarga_backup_central_{nombre_seguro}_{fecha}.sql"
    ruta_backup = carpeta / nombre_archivo

    generar_backup_sql(
        config=config,
        ruta_salida=ruta_backup,
    )

    registrar_evento_backup_sistema(
    accion="Backup base central",
    descripcion=(
        f"Se generó backup de la base central {config.nombre_bd} "
        f"en fecha/hora {obtener_fecha_hora_legible()}."
      ),
    )

    return FileResponse(
        path=str(ruta_backup),
        media_type="application/sql",
        filename=nombre_archivo,
        headers={
            "X-Fecha-Hora-Bolivia": obtener_fecha_hora_legible(),
            "X-Zona-Horaria": obtener_zona_horaria(),
        }
    )


@router.post("/central/restore",
               summary="Subir backup SQL y restaurar base central",
               description=(
               "Permite subir un archivo .sql previamente generado como backup "
               "para restaurar la base central del sistema."
              ),
                response_description="Resultado de la restauración de la base central."
             )
async def restore_base_central(
    archivo: UploadFile = File(...,
                               description="Subir archivo SQL de backup central para restaurar."),
    autorizado: bool = Depends(requerir_backup_admin),
):
    """
    Restaura un archivo SQL sobre la base central.

    CUIDADO:
    Puede reemplazar tablas centrales como empresa y base_de_datos_empresa.
    """

    config = obtener_config_central()
    ruta_temporal = await guardar_upload_temporal_async(archivo, ".sql")

    try:
        restaurar_sql(
            config=config,
            ruta_sql=ruta_temporal,
        )
    finally:
        try:
            os.remove(ruta_temporal)
        except Exception:
            pass

    registrar_evento_backup_sistema(
    accion="Restore base central",
    descripcion=(
        f"Se restauró backup sobre la base central {config.nombre_bd} "
        f"en fecha/hora {obtener_fecha_hora_legible()}."
      ),
    )

    return {
        "mensaje": "Base central restaurada correctamente.",
        "base_datos": config.nombre_bd,
        "archivo": archivo.filename,
        "fecha_hora": obtener_fecha_hora_legible(),
        "zona_horaria": obtener_zona_horaria(),
    }


# ============================================================
# 2. BACKUP / RESTORE POR EMPRESA
# ============================================================

@router.get("/empresa/backup",
            summary="Descargar backup de una empresa",
            description=(
             "Genera y descarga un archivo SQL de la base de datos de la empresa "
             "seleccionada mediante X-Empresa-Id. Incluye usuarios, proyectos, compras, "
             "ventas, presupuestos, pagos, bitácora y demás datos de esa empresa."
             ),
              response_description="Archivo SQL descargable de la empresa seleccionada."
            )
def backup_empresa(
    x_empresa_id: int = Header(..., alias="X-Empresa-Id"),
    session_central: Session = Depends(get_session),
    session_empresa: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador")),
):
    """
    Genera backup SQL solo de la empresa activa.

    Incluye:
    - proyectos
    - compras
    - ventas
    - presupuestos
    - pagos
    - usuarios
    - roles
    - bitácora
    - demás tablas de esa empresa
    """

    config_bd = obtener_config_empresa(
        x_empresa_id=x_empresa_id,
        session_central=session_central,
    )

    config = convertir_config_empresa(config_bd)
    carpeta = obtener_carpeta_backups()
    fecha = obtener_fecha_archivo()

    nombre_seguro = limpiar_nombre_archivo(config.nombre_bd)
    nombre_archivo = f"descarga_backup_empresa_{x_empresa_id}_{nombre_seguro}_{fecha}.sql"
    ruta_backup = carpeta / nombre_archivo

    generar_backup_sql(
        config=config,
        ruta_salida=ruta_backup,
    )

    registrar_evento_bitacora(
        session_empresa=session_empresa,
        usuario_actual=usuario_actual,
        accion="Backup empresa",
        descripcion=(
            f"Se generó backup de la base {config.nombre_bd} "
            f"en fecha/hora {obtener_fecha_hora_legible()}."
        ),
    )

    return FileResponse(
        path=str(ruta_backup),
        media_type="application/sql",
        filename=nombre_archivo,
        headers={
            "X-Fecha-Hora-Bolivia": obtener_fecha_hora_legible(),
            "X-Zona-Horaria": obtener_zona_horaria(),
        }
    )


@router.post("/empresa/restore",
              summary="Subir backup SQL y restaurar empresa",
              description=(
              "Permite subir un archivo .sql para restaurar la base de datos "
              "de la empresa seleccionada mediante X-Empresa-Id."
              ),
               response_description="Resultado de la restauración de la empresa."
             )
async def restore_empresa(
    archivo: UploadFile = File(...,description="Subir archivo SQL de backup de empresa para restaurar."),
    x_empresa_id: int = Header(..., alias="X-Empresa-Id"),
    session_central: Session = Depends(get_session),
    session_empresa: Session = Depends(get_session_empresa),
    usuario_actual=Depends(requerir_roles("Administrador")),
):
    """
    Restaura un archivo SQL sobre la base de datos de la empresa activa.

    CUIDADO:
    Si el SQL contiene --clean, puede borrar y recrear tablas.
    """

    config_bd = obtener_config_empresa(
        x_empresa_id=x_empresa_id,
        session_central=session_central,
    )

    config = convertir_config_empresa(config_bd)
    ruta_temporal = await guardar_upload_temporal_async(archivo, ".sql")

    try:
        restaurar_sql(
            config=config,
            ruta_sql=ruta_temporal,
        )
    finally:
        try:
            os.remove(ruta_temporal)
        except Exception:
            pass

    registrar_evento_bitacora(
        session_empresa=session_empresa,
        usuario_actual=usuario_actual,
        accion="Restore empresa",
        descripcion=(
            f"Se restauró backup sobre la base {config.nombre_bd} "
            f"en fecha/hora {obtener_fecha_hora_legible()}."
        ),
    )

    return {
        "mensaje": "Base de datos de empresa restaurada correctamente.",
        "empresa_id": x_empresa_id,
        "base_datos": config.nombre_bd,
        "archivo": archivo.filename,
        "fecha_hora": obtener_fecha_hora_legible(),
        "zona_horaria": obtener_zona_horaria(),
    }


# ============================================================
# 3. BACKUP / RESTORE COMPLETO
# ============================================================

@router.get("/completo/backup",
             summary="Descargar backup completo multiempresa",
             description=(
             "Genera y descarga un archivo ZIP con el backup completo del sistema. "
             "Incluye la base central, todas las bases de datos de empresas activas "
             "y un manifest.json con fecha, hora y detalle del respaldo."
             ),
             response_description="Archivo ZIP descargable con el backup completo multiempresa."
            )
def backup_completo(
    session_central: Session = Depends(get_session),
    autorizado: bool = Depends(requerir_backup_admin),
):
    """
    Genera backup completo del sistema.

    Incluye:
    - Base central
    - Todas las bases de datos de empresas activas
    - Manifest JSON con fecha/hora de inicio y fin
    """

    carpeta = obtener_carpeta_backups()
    fecha_archivo = obtener_fecha_archivo()
    fecha_inicio = obtener_fecha_hora_legible()

    carpeta_trabajo = carpeta / f"backup_completo_tmp_{fecha_archivo}"
    carpeta_trabajo.mkdir(parents=True, exist_ok=True)

    nombre_zip = f"descarga_backup_completo_multiempresa_{fecha_archivo}.zip"
    ruta_zip = carpeta / nombre_zip

    manifest = {
        "tipo": "backup_completo_multiempresa",
        "fecha_archivo": fecha_archivo,
        "fecha_inicio_backup": fecha_inicio,
        "fecha_fin_backup": None,
        "zona_horaria": obtener_zona_horaria(),
        "descripcion": (
            "Backup completo del sistema multiempresa: "
            "base central + bases activas de empresas."
        ),
        "central": None,
        "empresas": [],
    }

    try:
        # Backup central
        config_central = obtener_config_central()
        nombre_central = f"central_{limpiar_nombre_archivo(config_central.nombre_bd)}.sql"
        ruta_central = carpeta_trabajo / nombre_central

        generar_backup_sql(
            config=config_central,
            ruta_salida=ruta_central,
        )

        manifest["central"] = {
            "archivo": nombre_central,
            "nombre_bd": config_central.nombre_bd,
            "host": config_central.host,
            "puerto": config_central.puerto,
        }

        # Backups de empresas activas
        empresas = listar_empresas_activas(session_central)

        for empresa_config in empresas:
            config_empresa = convertir_config_empresa(empresa_config)

            nombre_empresa_sql = (
                f"empresa_{empresa_config.id_empresa}_"
                f"{limpiar_nombre_archivo(config_empresa.nombre_bd)}.sql"
            )

            ruta_empresa = carpeta_trabajo / nombre_empresa_sql

            generar_backup_sql(
                config=config_empresa,
                ruta_salida=ruta_empresa,
            )

            manifest["empresas"].append({
                "id_empresa": empresa_config.id_empresa,
                "nombre_bd": config_empresa.nombre_bd,
                "host": config_empresa.host,
                "puerto": config_empresa.puerto,
                "archivo": nombre_empresa_sql,
            })

        manifest["fecha_fin_backup"] = obtener_fecha_hora_legible()

        ruta_manifest = carpeta_trabajo / "manifest.json"

        with open(ruta_manifest, "w", encoding="utf-8") as archivo_manifest:
            json.dump(manifest, archivo_manifest, ensure_ascii=False, indent=4)

        with zipfile.ZipFile(ruta_zip, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for archivo in carpeta_trabajo.iterdir():
                zipf.write(archivo, arcname=archivo.name)

    finally:
        try:
            shutil.rmtree(carpeta_trabajo)
        except Exception:
            pass

    registrar_evento_backup_sistema(
    accion="Backup completo",
    descripcion=(
        "Se generó backup completo: central + empresas activas "
        f"en fecha/hora {obtener_fecha_hora_legible()}."
      ),
    )

    return FileResponse(
        path=str(ruta_zip),
        media_type="application/zip",
        filename=nombre_zip,
        headers={
            "X-Fecha-Hora-Bolivia": obtener_fecha_hora_legible(),
            "X-Zona-Horaria": obtener_zona_horaria(),
        }
    )


@router.post("/completo/restore",
              summary="Subir backup ZIP y restaurar sistema completo",
              description=(
              "Permite subir un archivo .zip generado por el backup completo. "
              "Restaura la base central y las bases de datos empresariales incluidas."
              ),
              response_description="Resultado de la restauración completa multiempresa."
             )
async def restore_completo(
    archivo: UploadFile = File(...,description="Subir archivo ZIP de backup completo multiempresa para restaurar."),
    session_central: Session = Depends(get_session),
    autorizado: bool = Depends(requerir_backup_admin),
):
    """
    Restaura backup completo generado por /backup-restore/completo/backup.

    Orden:
    1. Restaura base central.
    2. Restaura cada base de datos de empresa activa incluida en el ZIP.

    Requiere que las bases de datos existan previamente.
    """

    ruta_zip_temporal = await guardar_upload_temporal_async(archivo, ".zip")

    if not zipfile.is_zipfile(ruta_zip_temporal):
        try:
            os.remove(ruta_zip_temporal)
        except Exception:
            pass

        raise HTTPException(
            status_code=400,
            detail="El archivo subido no es un ZIP válido."
        )

    restaurados = {
        "central": None,
        "empresas": [],
        "omitidos": [],
        "fecha_hora_inicio_restore": obtener_fecha_hora_legible(),
        "fecha_hora_fin_restore": None,
        "zona_horaria": obtener_zona_horaria(),
    }

    try:
        with zipfile.ZipFile(ruta_zip_temporal, "r") as zipf:
            nombres = zipf.namelist()

            if "manifest.json" not in nombres:
                raise HTTPException(
                    status_code=400,
                    detail="El ZIP no contiene manifest.json."
                )

            manifest = json.loads(
                zipf.read("manifest.json").decode("utf-8")
            )

            if manifest.get("tipo") != "backup_completo_multiempresa":
                raise HTTPException(
                    status_code=400,
                    detail="El ZIP no corresponde a un backup completo multiempresa."
                )

            # 1. Restaurar central
            central_info = manifest.get("central")

            if not central_info or "archivo" not in central_info:
                raise HTTPException(
                    status_code=400,
                    detail="El manifest no contiene información de la base central."
                )

            archivo_central = central_info["archivo"]

            if archivo_central not in nombres:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se encontró el archivo central {archivo_central} en el ZIP."
                )

            config_central = obtener_config_central()

            with NamedTemporaryFile(delete=False, suffix=".sql") as temp_central:
                temp_central.write(zipf.read(archivo_central))
                ruta_central_sql = Path(temp_central.name)

            try:
                restaurar_sql(
                    config=config_central,
                    ruta_sql=ruta_central_sql,
                )
            finally:
                try:
                    os.remove(ruta_central_sql)
                except Exception:
                    pass

            restaurados["central"] = config_central.nombre_bd

            try:
                session_central.rollback()
                session_central.expire_all()
            except Exception:
                pass

            # 2. Restaurar empresas usando configuración actual de base central
            configs_actuales = listar_empresas_activas(session_central)

            configs_por_id = {
                config.id_empresa: config
                for config in configs_actuales
            }

            empresas_manifest = manifest.get("empresas", [])

            for empresa_info in empresas_manifest:
                id_empresa = empresa_info.get("id_empresa")
                archivo_empresa = empresa_info.get("archivo")

                if not id_empresa or not archivo_empresa:
                    restaurados["omitidos"].append({
                        "motivo": "Registro de empresa incompleto en manifest.",
                        "empresa": empresa_info,
                    })
                    continue

                if archivo_empresa not in nombres:
                    restaurados["omitidos"].append({
                        "id_empresa": id_empresa,
                        "motivo": f"No se encontró {archivo_empresa} en el ZIP.",
                    })
                    continue

                config_bd = configs_por_id.get(id_empresa)

                if not config_bd:
                    restaurados["omitidos"].append({
                        "id_empresa": id_empresa,
                        "motivo": "No existe configuración activa en base central actual.",
                    })
                    continue

                config_empresa = convertir_config_empresa(config_bd)

                with NamedTemporaryFile(delete=False, suffix=".sql") as temp_empresa:
                    temp_empresa.write(zipf.read(archivo_empresa))
                    ruta_empresa_sql = Path(temp_empresa.name)

                try:
                    restaurar_sql(
                        config=config_empresa,
                        ruta_sql=ruta_empresa_sql,
                    )

                    restaurados["empresas"].append({
                        "id_empresa": id_empresa,
                        "base_datos": config_empresa.nombre_bd,
                    })

                finally:
                    try:
                        os.remove(ruta_empresa_sql)
                    except Exception:
                        pass

    finally:
        try:
            os.remove(ruta_zip_temporal)
        except Exception:
            pass

    restaurados["fecha_hora_fin_restore"] = obtener_fecha_hora_legible()

    registrar_evento_backup_sistema(
    accion="Restore completo",
    descripcion=(
        "Se ejecutó restore completo: central + empresas activas "
        f"en fecha/hora {obtener_fecha_hora_legible()}."
     ),
    )

    return {
        "mensaje": "Restore completo ejecutado.",
        "resultado": restaurados,
    }