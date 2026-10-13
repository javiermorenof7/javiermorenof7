# Databricks notebook source
# Silver: toma la última versión de cada archivo de Bronze, la limpia y le pone tipos.
# Las filas que no se pueden usar se apartan con su motivo en vez de perderse.

# COMMAND ----------

# 1. Librerías y logs
import logging

from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("silver")

# COMMAND ----------

# 2. Entorno: dev por defecto; el job envía el suyo como parámetro
dbutils.widgets.dropdown("entorno", "dev", ["dev", "prod"])
ENTORNO = dbutils.widgets.get("entorno")
CATALOGO = f"aulaviva_{ENTORNO}"

# COMMAND ----------

# 3. Configuración
BRONZE = f"{CATALOGO}.bronze.calendario"
CONTROL = f"{CATALOGO}.bronze.control_calendario"
TABLA = f"{CATALOGO}.silver.calendario"
RECHAZADOS = f"{CATALOGO}.silver.calendario_rechazados"
LLAVE = ["alianza", "programa", "cohorte", "periodo", "asignatura"]
# Cada alianza escribe las fechas a su manera
FORMATOS_FECHA = ["yyyy-MM-dd", "dd/MM/yyyy"]
ZONA_HORARIA = "America/Bogota"

# COMMAND ----------

# 4. Funciones
def texto(columna):
    """Quita espacios sobrantes al inicio, al final y entre palabras."""
    return F.trim(F.regexp_replace(F.col(columna), r"\s+", " "))


def fecha(columna):
    """Prueba cada formato conocido; si ninguno sirve devuelve nulo en vez de fallar."""
    return F.coalesce(
        *[F.try_to_timestamp(F.trim(F.col(columna)), F.lit(f)).cast("date") for f in FORMATOS_FECHA]
    )


def leer_version_vigente():
    """De cada archivo, solo las filas de su carga más reciente."""
    vigentes = spark.table(CONTROL).groupBy("archivo").agg(F.max("fecha_ingesta").alias("fecha_ingesta"))
    return spark.table(BRONZE).join(vigentes, ["archivo", "fecha_ingesta"])


def limpiar(bronze):
    motivo = (
        F.when(F.col("periodo").isNull(), "periodo no numérico")
        .when(F.col("fecha_inicio").isNull() | F.col("fecha_fin").isNull(), "fecha ilegible")
        .when(F.col("fecha_fin") < F.col("fecha_inicio"), "termina antes de empezar")
    )
    return (
        bronze.select(
            texto("alianza").alias("alianza"),
            texto("programa").alias("programa"),
            F.upper(texto("cohorte")).alias("cohorte"),
            F.expr("try_cast(trim(periodo) AS INT)").alias("periodo"),
            texto("asignatura").alias("asignatura"),
            fecha("fecha_inicio").alias("fecha_inicio"),
            fecha("fecha_fin").alias("fecha_fin"),
            F.col("fecha_inicio").alias("fecha_inicio_origen"),
            F.col("fecha_fin").alias("fecha_fin_origen"),
            "archivo",
        )
        .dropDuplicates(LLAVE)
        .withColumn("motivo", motivo)
        .withColumn("fecha_proceso", F.from_utc_timestamp(F.current_timestamp(), ZONA_HORARIA))
    )


# COMMAND ----------

# 5. Proceso
log.info("Inicio Silver en %s", CATALOGO)
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOGO}.silver")

limpio = limpiar(leer_version_vigente())

validas = (
    limpio.filter(F.col("motivo").isNull())
    .withColumn("semanas", F.ceil((F.datediff("fecha_fin", "fecha_inicio") + 1) / 7).cast("int"))
    .drop("motivo", "fecha_inicio_origen", "fecha_fin_origen")
)
rechazadas = limpio.filter(F.col("motivo").isNotNull()).drop("fecha_inicio", "fecha_fin")

validas.write.mode("overwrite").option("overwriteSchema", True).saveAsTable(TABLA)
log.info("[1/2] %s", TABLA)
rechazadas.write.mode("overwrite").option("overwriteSchema", True).saveAsTable(RECHAZADOS)
log.info("[2/2] %s", RECHAZADOS)

# COMMAND ----------

# 6. Validación: la llave no se repite y ninguna fila válida quedó sin fechas
silver = spark.table(TABLA)
total = silver.count()
repetidas = total - silver.select(*LLAVE).distinct().count()
sin_fecha = silver.filter(F.col("fecha_inicio").isNull() | F.col("fecha_fin").isNull()).count()
if repetidas or sin_fecha:
    raise ValueError(f"Silver no pasa la validación: {repetidas} llaves repetidas, {sin_fecha} filas sin fecha")
log.info("Fin Silver: %d filas válidas, %d rechazadas", total, spark.table(RECHAZADOS).count())
