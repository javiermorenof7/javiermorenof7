import os
import google.auth
from google.cloud import bigquery

class FinTrustETL:
    def __init__(self):
        # Detecta automáticamente las credenciales y el project_id de la sesión activa
        try:
            self.credentials, self.project_id = google.auth.default()
            if not self.project_id:
                # Fallback por si no se detecta el proyecto automáticamente
                self.project_id = os.getenv("GCP_PROJECT_ID")
            
            self.client = bigquery.Client(credentials=self.credentials, project=self.project_id)
            print(f"✅ Autenticado exitosamente en el proyecto: {self.project_id}")
        except Exception as e:
            print(f"❌ Error de autenticación: {e}")
            print("Asegúrate de haber ejecutado: gcloud auth application-default login")
            raise

    def execute_sql_file(self, file_path, description):
        """Busca y ejecuta un archivo SQL reemplazando el ID del proyecto."""
        if not os.path.exists(file_path):
            print(f"⚠️ Saltando {description}: No se encontró el archivo en {file_path}")
            return

        with open(file_path, 'r') as f:
            # Reemplaza dinámicamente el placeholder por el proyecto detectado
            query = f.read().replace('proyecto-prueba-367518', self.project_id)
            
        print(f"🚀 Ejecutando: {description}...")
        try:
            job = self.client.query(query)
            job.result()
            print(f"✅ {description} completado.")
        except Exception as e:
            print(f"❌ Error en {description}: {e}")

    def run_pipeline(self):
        print("--- Iniciando Pipeline FinTrust (Modo ADC) ---")
        
        # Lista de capas a procesar según tu estructura de carpetas
        steps = [
            ("caso_ceiba_fintrust/sql/01-raw/create_raw_tables.sql", "Creación de Tablas Raw"),
            ("caso_ceiba_fintrust/sql/02-staging/stg_*.sql", "Creacion Capa Staging"),
            ("caso_ceiba_fintrust/sql/03-analytics/dm_*.sql", "Creacion Capa Analytics"),
            ("caso_ceiba_fintrust/sql/04-queries-negocio/q01_desembolso_diario.sql", "Creacion Caso Uso Desembolso Diario"),
            ("caso_ceiba_fintrust/sql/04-queries-negocio/q02_recaudo_diario.sql", "Creacion Caso Uso Recaudo Diario"),
            ("caso_ceiba_fintrust/sql/04-queries-negocio/q03_cartera_por_cohorte.sql", "Creacion Caso Uso Cartera por Cohorte"),
            ("caso_ceiba_fintrust/sql/04-queries-negocio/q04_top_atraso.sql", "Creacion Caso Uso Top Atraso"),
            ("caso_ceiba_fintrust/sql/04-queries-negocio/q05_pareto.sql", "Creacion Caso Uso Pareto"),
        ]

        for path, desc in steps:
            self.execute_sql_file(path, desc)

        print("--- Pipeline Finalizado con Éxito ---")

if __name__ == "__main__":
    etl = FinTrustETL()
    etl.run_pipeline()