-- Capa Bronze (Staging): Se limpia y llena en cada ejecución
CREATE OR REPLACE TABLE `mi-proyecto-javier-500617.dataset_prueba.bronze_transacciones` (
    transaction_id STRING,
    patient_id STRING,
    procedure_code STRING,
    transaction_date DATE,
    status STRING,
    execution_date DATE -- Campo de trazabilidad inyectado por Airflow
);

-- Capa Silver (Producción): Histórico consolidado y particionado
CREATE TABLE IF NOT EXISTS `mi-proyecto-javier-500617.dataset_prueba.silver_transacciones` (
    transaction_id STRING,
    patient_id STRING,
    procedure_code STRING,
    transaction_date DATE,
    status STRING,
    execution_date DATE
)
PARTITION BY execution_date
CLUSTER BY patient_id;