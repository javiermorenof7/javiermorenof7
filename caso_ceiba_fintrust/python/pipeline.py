import os
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

class FinTrustETL:
    def __init__(self, project_id, dataset_raw, dataset_stg, dataset_ana):
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id
        self.dataset_raw = dataset_raw
        self.dataset_stg = dataset_stg
        self.dataset_ana = dataset_ana

    def run_query(self, query, description):
        """Ejecuta una consulta en BigQuery y maneja errores básicos."""
        print(f"Ejecutando: {description}...")
        try:
            query_job = self.client.query(query)
            query_job.result()  # Espera a que termine
            print(f"✅ {description} completado con éxito.")
        except Exception as e:
            print(f"❌ Error en {description}: {e}")
            raise

    def transform_staging(self):
        """Paso 1: Limpieza y tipado de datos (Capa Staging)."""
        # Ejemplo: Limpiar la tabla de pagos resolviendo inconsistencias de fechas [cite: 19]
        query = f"""
        CREATE OR REPLACE TABLE `{self.project_id}.{self.dataset_stg}.stg_payments` AS
        SELECT 
            CAST(payment_id AS STRING) as payment_id,
            CAST(loan_id AS STRING) as loan_id,
            SAFE_CAST(amount AS FLOAT64) as amount,
            SAFE.PARSE_DATE('%Y-%m-%d', payment_date) as payment_date,
            UPPER(TRIM(payment_channel)) as payment_channel
        FROM `{self.project_id}.{self.dataset_raw}.payments`
        WHERE payment_id IS NOT NULL;
        """
        self.run_query(query, "Transformación de Capa Staging (Pagos)")

    def create_data_mart(self):
        """Paso 2: Construcción del Data Mart Analítico (Capa Analytics)."""
        # Responde a: Desembolso total por día, ciudad y segmento [cite: 35]
        query = f"""
        CREATE OR REPLACE TABLE `{self.project_id}.{self.dataset_ana}.dm_daily_disbursements` AS
        SELECT 
            l.disbursement_date,
            c.city,
            c.segment,
            SUM(l.loan_amount) as total_disbursed,
            COUNT(l.loan_id) as loan_count
        FROM `{self.project_id}.{self.dataset_stg}.stg_loans` l
        JOIN `{self.project_id}.{self.dataset_stg}.stg_customers` c ON l.customer_id = c.customer_id
        GROUP BY 1, 2, 3;
        """
        self.run_query(query, "Generación de Data Mart de Desembolsos")

    def run_quality_checks(self):
        """Paso 3: Validaciones de calidad de datos[cite: 43, 71]."""
        query = f"""
        SELECT COUNT(*) as issues 
        FROM `{self.project_id}.{self.dataset_stg}.stg_payments` 
        WHERE amount < 0 OR payment_date > CURRENT_DATE()
        """
        results = self.client.query(query).to_dataframe()
        issues = results['issues'][0]
        
        if issues > 0:
            print(f"⚠️ Alerta de Calidad: Se encontraron {issues} registros con inconsistencias.")
        else:
            print("💎 Calidad de datos verificada: Sin anomalías críticas.")

    def run_pipeline(self):
        """Ejecución secuencial del pipeline[cite: 67]."""
        print("--- Iniciando Pipeline ETL FinTrust ---")
        self.transform_staging()
        self.create_data_mart()
        self.run_quality_checks()
        print("--- Pipeline Finalizado ---")

if __name__ == "__main__":
    # Configuración (Estas variables deberían venir de un .env o config)
    PROJECT = "proyecto-prueba"
    RAW = "raw_fintrust"
    STG = "stg_fintrust"
    ANA = "analytics_fintrust"

    etl = FinTrustETL(PROJECT, RAW, STG, ANA)
    etl.run_pipeline()