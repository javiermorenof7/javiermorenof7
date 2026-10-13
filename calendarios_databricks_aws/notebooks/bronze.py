# Databricks notebook source
# Bronze: copia los calendarios de S3 tal como llegan, sin reglas de negocio.
# Solo agrega un archivo cuando su contenido cambió desde la última carga.

# COMMAND ----------

# 1. Librerías y logs
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("bronze")

# COMMAND ----------

# 2. Entorno: dev por defecto; el job envía el suyo como parámetro
dbutils.widgets.dropdown("entorno", "dev", ["dev", "prod"])
ENTORNO = dbutils.widgets.get("entorno")
CATALOGO = f"aulaviva_{ENTORNO}"
BUCKET = f"s3://aulaviva-{ENTORNO}-landing"

# COMMAND ----------

# 3. Configuración
ORIGEN = f"{BUCKET}/calendarios/"
TABLA = f"{CATALOGO}.bronze.calendario"
CONTROL = f"{CATALOGO}.bronze.control_calendario"
COLUMNAS = ["alianza", "programa", "cohorte", "periodo", "asignatura", "fecha_inicio", "fecha_fin"]
ZONA_HORARIA = "America/Bogota"

# COMMAND ----------

# 4. Funciones
def leer_origen():
    """Lee todos los CSV del bucket como texto y anota de qué archivo viene cada fila."""
    return (
        spark.read.option("header", True)
        .csv(ORIGEN)
        .select(*COLUMNAS, F.col("_metadata.file_name").alias("archivo"))
    )


def calcular_huellas(crudo):
    """Una huella por archivo: cambia si cambia cualquier celda, sin importar el orden de las filas."""
    fila = F.sha2(F.concat_ws("|", *[F.coalesce(F.col(c), F.lit("")) for c in COLUMNAS]), 256)
    return (
        crudo.withColumn("fila", fila)
        .groupBy("archivo")
        .agg(
            F.sha2(F.concat_ws("", F.sort_array(F.collect_list("fila"))), 256).alias("huella"),
            F.count("*").alias("filas"),
        )
    )


def descartar_conocidas(huellas):
    """Deja solo los archivos cuya huella no coincide con la última que se cargó."""
    if not spark.catalog.tableExists(CONTROL):
        return huellas
    vigentes = (
        spark.table(CONTROL)
        .groupBy("archivo")
        .agg(F.max_by("huella", "fecha_ingesta").alias("huella"))
    )
    return huellas.join(vigentes, ["archivo", "huella"], "left_anti")


# COMMAND ----------

# 5. Proceso
log.info("Inicio Bronze en %s, origen %s", CATALOGO, ORIGEN)
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOGO}.bronze")

crudo = leer_origen()
huellas = calcular_huellas(crudo)
# Una fila por archivo: cabe en memoria y evita leer S3 dos veces con resultados distintos
cambios = descartar_conocidas(huellas).collect()

if cambios:
    ahora = datetime.now(ZoneInfo(ZONA_HORARIA)).strftime("%Y-%m-%d %H:%M:%S")
    control = spark.createDataFrame(cambios, huellas.schema).withColumn(
        "fecha_ingesta", F.lit(ahora).cast("timestamp")
    )
    (
        crudo.join(control, "archivo")
        .select(*COLUMNAS, "archivo", "huella", "fecha_ingesta")
        .write.mode("append")
        .saveAsTable(TABLA)
    )
    control.write.mode("append").saveAsTable(CONTROL)
    for i, cambio in enumerate(cambios, start=1):
        log.info("[%d/%d] %s: %d filas", i, len(cambios), cambio["archivo"], cambio["filas"])
else:
    log.info("Ningún archivo cambió: no se agrega nada")

# COMMAND ----------

# 6. Validación: lo guardado de cada carga coincide con lo que se leyó
if cambios:
    guardadas = {
        f["archivo"]: f["count"]
        for f in spark.table(TABLA).filter(F.col("fecha_ingesta") == ahora).groupBy("archivo").count().collect()
    }
    for cambio in cambios:
        if guardadas.get(cambio["archivo"]) != cambio["filas"]:
            raise ValueError(f"{cambio['archivo']}: se leyeron {cambio['filas']} filas y se guardaron {guardadas.get(cambio['archivo'])}")
log.info("Fin Bronze")
