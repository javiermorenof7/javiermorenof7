# Ingeniería de Datos en GCP

Este repositorio se enfocada en la construcción de un flujo completo de procesamiento de datos en Google Cloud Platform (GCP). 

El proyecto aplica mejores prácticas de ingeniería de datos, utilizando **Arquitectura Medallón (Medallion Architecture)** para garantizar la escalabilidad, calidad e idempotencia de los datos en BigQuery.

## 🏗️ Arquitectura y Componentes GCP

* **Google Cloud Storage (GCS):** Capa de aterrizaje (Landing) para la recepción de archivos crudos (CSV, TXT, Excel).
* **BigQuery:** Data Warehouse principal. Estructurado lógicamente en capas:
    * **Bronze:** Almacena los datos en crudo tras la ingesta (con esquema). Modo *Overwrite*.
    * **Silver:** Datos limpios y consolidados. Maneja el histórico particionado y operaciones idempotentes.
* **Cloud Composer (Apache Airflow):** Orquestador central del pipeline.
* **Cloud Functions / Compute (Python puro):** Utilizado en scripts auxiliares para limpiezas específicas (e.g., manipulación de archivos Excel con pandas antes de la ingesta).

## 📂 Estructura del Repositorio

* 📁 `dag/`
    * `dag_salud_ingestion.py`: Orquestación del flujo. Implementa sensores eficientes y cargas idempotentes desde GCS a las capas Bronze y Silver en BigQuery.
* 📁 `sql/`
    * `preparacion_DAG.sql`: DDL para la creación estructurada de las tablas `bronze_transacciones` y `silver_transacciones` (optimizadas con particionamiento y clustering).
    * `procedure.sql`: Lógica analítica encapsulada. Un Stored Procedure (`sp_usuarios_por_procedimiento`) que integra datos transaccionales con maestros geográficos usando parámetros dinámicos.
* 📁 `procesamiento/`
    * `python_tablas_gcp.py`: Script para cargar datos estructurados a BigQuery usando `google-cloud-bigquery` y la API de Dataframes.
    * `python_excel.py`: Limpieza de datos previa (ej. corrección de tipos de datos en códigos de municipios desde un origen `.xlsx` a `.csv`).
* 📁 `data/`
    * Archivos de muestra y prueba: `Citas_Start_20220603.txt`, `transacciones_medicas_20260611.csv`, maestro de municipios (DIVIPOLA), etc.

## 🚀 Resoluciones Clave y Mejores Prácticas Aplicadas

Al analizar la prueba original, se detectaron y solucionaron los siguientes anti-patrones arquitectónicos:

### 1. Optimización del Sensor en Composer (Ahorro de Costos)
* **El Problema:** El sensor original de espera de archivos (`GCSObjectExistenceSensor`) estaba configurado en modo `poke`, bloqueando el worker slot indefinidamente hasta que el archivo llegara, consumiendo recursos.
* **La Solución:** Se reconfiguró a `mode='reschedule'` con un `poke_interval` razonable (10 minutos). De esta forma, el worker se libera tras cada comprobación fallida, optimizando drásticamente los costos de Composer.

### 2. Idempotencia y Prevención de Duplicados
* **El Problema:** Las fallas y reejecuciones del DAG causaban reprocesamientos íntegros y la inserción de registros duplicados en BigQuery.
* **La Solución:** La transición de la capa Bronze a la Silver se realiza ahora mediante una operación `MERGE` en BigQuery. Esta evalúa las llaves primarias (`transaction_id`) para decidir si hacer un `INSERT` o un `UPDATE`, asegurando que la carga sea **100% idempotente**.

### 3. Trazabilidad del Pipeline
* Para facilitar la auditoría, se inyecta la variable macro de Airflow `{{ ds }}` (fecha de ejecución lógica) directamente como un parámetro en las sentencias SQL y cargas (`execution_date`). Esto permite rastrear exactamente qué ejecución del DAG insertó o modificó cada registro en la capa Silver.

### 4. Modelo de Seguridad (IAM)
* El diseño plantea remover el rol de `Editor` genérico sobre el proyecto de la cuenta de servicio de Composer. En su lugar, se asume el principio de **Mínimo Privilegio**: roles granulares como `roles/storage.objectAdmin` (solo para los buckets del flujo), `roles/bigquery.dataEditor` (para los datasets específicos) y `roles/bigquery.jobUser`.

## ⚙️ Instrucciones Básicas de Ejecución

1.  Asegúrese de configurar las credenciales de GCP en su entorno local o usar una Service Account válida.
2.  Despliegue la infraestructura base (tablas en BQ) ejecutando: `sql/preparacion_DAG.sql`.
3.  Cargue los datos maestros iniciales ejecutando los scripts en `procesamiento/`.
4.  Despliegue `dag_salud_ingestion.py` en el bucket de `dags/` de Cloud Composer.