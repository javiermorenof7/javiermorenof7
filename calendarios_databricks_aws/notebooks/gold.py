# Databricks notebook source
# Gold: una fila por periodo de cada cohorte, lista para planificación y tableros.
# Si los datos no cumplen las reglas, el notebook falla y la tabla anterior queda intacta.

# COMMAND ----------

# 1. Librerías y logs
import logging

from pyspark.sql import Window
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("gold")

# COMMAND ----------

# 2. Entorno: dev por defecto; el job envía el suyo como parámetro
dbutils.widgets.dropdown("entorno", "dev", ["dev", "prod"])
ENTORNO = dbutils.widgets.get("entorno")
CATALOGO = f"aulaviva_{ENTORNO}"

# COMMAND ----------

# 3. Configuración
SILVER = f"{CATALOGO}.silver.calendario"
TABLA = f"{CATALOGO}.gold.calendario_periodos"
COHORTE = ["alianza", "programa", "cohorte"]
LLAVE = COHORTE + ["periodo"]
ZONA_HORARIA = "America/Bogota"

# COMMAND ----------

# 4. Funciones
def resumir_periodos(silver):
    return (
        silver.groupBy(*LLAVE)
        .agg(
            F.min("fecha_inicio").alias("inicio_periodo"),
            F.max("fecha_fin").alias("fin_periodo"),
            F.countDistinct("asignatura").alias("asignaturas"),
        )
        .withColumn("semanas", F.ceil((F.datediff("fin_periodo", "inicio_periodo") + 1) / 7).cast("int"))
        .withColumn("fecha_proceso", F.from_utc_timestamp(F.current_timestamp(), ZONA_HORARIA))
    )


def contar_solapados(gold):
    """Periodos que empiezan antes de que termine el anterior de su misma cohorte."""
    orden = Window.partitionBy(*COHORTE).orderBy("periodo")
    return (
        gold.withColumn("fin_anterior", F.lag("fin_periodo").over(orden))
        .filter(F.col("inicio_periodo") <= F.col("fin_anterior"))
        .count()
    )


# COMMAND ----------

# 5. Proceso
log.info("Inicio Gold en %s", CATALOGO)
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOGO}.gold")

gold = resumir_periodos(spark.table(SILVER))

# COMMAND ----------

# 6. Validación antes de publicar
total = gold.count()
solapados = contar_solapados(gold)
if total == 0 or solapados:
    raise ValueError(f"Gold no pasa la validación: {total} periodos, {solapados} solapados")

gold.write.mode("overwrite").option("overwriteSchema", True).saveAsTable(TABLA)
log.info("Fin Gold: %d periodos en %s", total, TABLA)
