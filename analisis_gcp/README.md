# Ingeniería de Datos en GCP

Este repositorio se enfocada en la construcción de un flujo completo de procesamiento de datos en Google Cloud Platform (GCP). 

El proyecto aplica mejores prácticas de ingeniería de datos, utilizando **Arquitectura Medallón (Medallion Architecture)** para garantizar la escalabilidad, calidad e idempotencia de los datos en BigQuery.

## 🏗️ Arquitectura y Componentes GCP

* **Google Cloud Storage (GCS):** Capa de aterrizaje (Landing) para la recepción de archivos crudos (CSV, TXT, Excel).
* **BigQuery:** Data Warehouse principal. Estructurado lógicamente en capas:
    * **Bronze:** Almacena los datos en crudo tras la ingesta (con esquema). Modo *Overwrite*.
    * **Silver:** Datos limpios y consolidados. Maneja el histórico particionado y operaciones idempotentes.
* **Cloud Composer (Apache Airflow):** Orquestador central del pipeline.
* **Cloud Functions / Compute (Python puro):** Utilizado en scripts auxiliares para limpiezas específicas (e.g., preparar el maestro de municipios del DANE con pandas antes de la ingesta).

## 📂 Estructura del Repositorio

* 📁 `dag/`
    * `dag_salud_ingestion.py`: Orquestación del flujo. Implementa sensores eficientes y cargas idempotentes desde GCS a las capas Bronze y Silver en BigQuery.
* 📁 `sql/`
    * `preparacion_DAG.sql`: DDL para la creación estructurada de las tablas `bronze_transacciones` y `silver_transacciones` (optimizadas con particionamiento y clustering).
    * `procedure.sql`: Lógica analítica encapsulada. Un Stored Procedure (`sp_usuarios_por_procedimiento`) que integra datos transaccionales con maestros geográficos usando parámetros dinámicos.
* 📁 `procesamiento/`
    * `python_tablas_gcp.py`: Script para cargar datos estructurados a BigQuery usando `google-cloud-bigquery` y la API de Dataframes.
    * `python_divipola.py`: Prepara el maestro oficial de municipios del DANE (DIVIPOLA, 1.122 municipios) para BigQuery: código como entero, coordenadas con punto decimal. Escribe `procesamiento/DIVIPOLA_Municipios_clean.csv`.
* 📁 `data/`
    * Archivos de muestra y prueba: `Citas_Start_20220603.txt`, `transacciones_medicas_20260611.csv` y la muestra de SIVIGILA. El maestro de municipios es el oficial del DANE (ver la sección de datos reales).

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

## 🩺 Datos reales: vigilancia en salud pública (SIVIGILA)

Además de los archivos de muestra, el proyecto procesa los casos notificados al **SIVIGILA**, el sistema nacional de vigilancia en salud pública de Colombia, que publica el Instituto Nacional de Salud (INS) en [datos.gov.co](https://www.datos.gov.co).

| Conjunto | Publica | Filas |
| --- | --- | --- |
| [SIVIGILA 2017](https://www.datos.gov.co/d/84d4-vfax) | INS | 193.641 |
| [SIVIGILA 2018](https://www.datos.gov.co/d/xd2n-cu8j) | INS | 194.139 |
| [SIVIGILA 2019](https://www.datos.gov.co/d/qvnt-2igj) | INS | 205.532 |
| [SIVIGILA 2021](https://www.datos.gov.co/d/fhc4-jjti) | INS | 187.598 |
| [DIVIPOLA, códigos de municipios](https://www.datos.gov.co/d/gdxc-w37w) | DANE | 1.122 |

Licencia: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es). Son conteos agregados por semana, evento y municipio, sin datos personales. El portal no publica 2020 a nivel nacional.

* `procesamiento/ingesta_sivigila.py` (bronce): baja cada conjunto desde la API del portal, paginado con un orden estable, y guarda un archivo de control con las filas, la fecha de actualización del portal y la huella SHA-256. Si el portal no cambió, no vuelve a descargar.
* `procesamiento/capas_sivigila.py` (plata y oro):
    * Unifica el esquema: cada año llega con columnas distintas (`cod_mun`, `cod_mun_o` y, en 2021, solo nombres sin códigos).
    * Completa los códigos DIVIPOLA, que llegan sin ceros a la izquierda (`5` y `250` pasan a `05` y `05250`).
    * En 2021 busca el código por nombre dentro de cada departamento: quita paréntesis (`ROBLES (LA PAZ)`), compara sin espacios (`POLO NUEVO` y `POLONUEVO`) y acepta un nombre corto solo si hay un único oficial que lo contiene (`CALI` en `SANTIAGO DE CALI`).
    * Aparta las filas que no se pueden ubicar, con su motivo, y comprueba que el total de casos cuadra entre bronce y plata.

Resultado de la última corrida (`data/oro/resumen_capas.csv`):

| Resultado | 2017 | 2018 | 2019 | 2021 |
| --- | ---: | ---: | ---: | ---: |
| Aceptada | 189.680 | 190.007 | 203.053 | 186.178 |
| Municipio desconocido (código `000`) | 2.841 | 2.413 | 437 | 0 |
| Caso del exterior | 1.031 | 1.604 | 1.922 | 1.361 |
| Procedencia desconocida | 66 | 72 | 67 | 51 |
| Código de municipio inexistente | 23 | 43 | 53 | 0 |
| Municipio sin código en DIVIPOLA | 0 | 0 | 0 | 8 |

La capa oro (`data/oro/`) trae los casos por semana, por evento y por departamento. Las capas bronce y plata se regeneran con los scripts y no se versionan; `data/sivigila_2019_semana_01.csv` es una muestra de bronce.

## ⚙️ Instrucciones Básicas de Ejecución

1.  Asegúrese de configurar las credenciales de GCP en su entorno local o usar una Service Account válida.
2.  Despliegue la infraestructura base (tablas en BQ) ejecutando: `sql/preparacion_DAG.sql`.
3.  Cargue los datos maestros iniciales ejecutando los scripts en `procesamiento/`.
4.  Despliegue `dag_salud_ingestion.py` en el bucket de `dags/` de Cloud Composer.
5.  Para los datos reales: `python analisis_gcp/procesamiento/ingesta_sivigila.py` y después `python analisis_gcp/procesamiento/capas_sivigila.py` (solo necesitan `pandas` y `requests`).
