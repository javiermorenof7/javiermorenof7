from airflow import DAG
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago

# Variables de configuración
PROJECT_ID = "mi-proyecto-javier-500617"
DATASET_ID = "dataset_prueba"
BUCKET_NAME = "javier-proyecto"
FILE_NAME = "transacciones_medicas_{{ ds_nodash }}.csv"# Espera un archivo con la fecha del DAG

default_args = {
    'owner': 'data_engineering_team',
    'start_date': days_ago(1),
    'retries': 1,
}

with DAG(
    'ingesta_transacciones_medicas',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['salud', 'medallion_architecture']
) as dag:

    # SOLUCIÓN PROBLEMA 1: Sensor asíncrono que no bloquea recursos
    esperar_archivo = GCSObjectExistenceSensor(
        task_id='esperar_archivo_csv',
        bucket=BUCKET_NAME,
        object=FILE_NAME,
        mode='reschedule', # Libera el worker de Composer entre chequeos
        poke_interval=600, # Revisa cada 10 minutos
        timeout=3600 * 4   # Falla después de 4 horas
    )

    # Carga a Capa Bronze (Sobreescritura - WRITE_TRUNCATE)
    # Se inyecta la fecha lógica (ds) de Airflow como constante para trazabilidad
    # Carga a Capa Bronze (Sobreescritura - WRITE_TRUNCATE)
    cargar_bronze = GCSToBigQueryOperator(
        task_id='gcs_a_bronze',
        bucket=BUCKET_NAME,
        source_objects=[FILE_NAME],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET_ID}.bronze_transacciones",
        schema_fields=[
            {'name': 'transaction_id', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'patient_id', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'procedure_code', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'transaction_date', 'type': 'DATE', 'mode': 'NULLABLE'},
            {'name': 'status', 'type': 'STRING', 'mode': 'NULLABLE'}
        ],
        write_disposition='WRITE_TRUNCATE',
        skip_leading_rows=1,
        source_format='CSV'
    )

    # SOLUCIÓN PROBLEMA 2: Idempotencia en Capa Silver
    # Operación MERGE para evitar duplicados si el DAG se reprocesa s s s
    merge_query = f"""
    MERGE `{PROJECT_ID}.{DATASET_ID}.silver_transacciones` T
    USING (
        SELECT 
            transaction_id, 
            patient_id, 
            procedure_code, 
            transaction_date, 
            status, 
            CAST('{{ ds }}' AS DATE) AS execution_date 
        FROM `{PROJECT_ID}.{DATASET_ID}.bronze_transacciones`
    ) S
    ON T.transaction_id = S.transaction_id
    WHEN MATCHED THEN
        UPDATE SET 
            patient_id = S.patient_id,
            procedure_code = S.procedure_code,
            transaction_date = S.transaction_date,
            status = S.status,
            execution_date = S.execution_date
    WHEN NOT MATCHED THEN
        INSERT (transaction_id, patient_id, procedure_code, transaction_date, status, execution_date)
        VALUES (S.transaction_id, S.patient_id, S.procedure_code, S.transaction_date, S.status, S.execution_date)
    """

    procesar_silver = BigQueryInsertJobOperator(
        task_id='merge_bronze_a_silver',
        configuration={
            "query": {
                "query": merge_query,
                "useLegacySql": False,
            }
        }
    )

    # Orquestación
    esperar_archivo >> cargar_bronze >> procesar_silver