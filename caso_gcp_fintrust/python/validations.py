import os
import google.auth
from google.cloud import bigquery

class DataQualityValidator:
    def __init__(self):
        try:
            self.credentials, self.project_id = google.auth.default()
            if not self.project_id:
                self.project_id = os.getenv("GCP_PROJECT_ID", "proyecto-prueba-367518")
            
            self.client = bigquery.Client(credentials=self.credentials, project=self.project_id)
            print(f"🔍 Iniciando Validaciones de Calidad en: {self.project_id}\n")
        except Exception as e:
            print(f"❌ Error de autenticación: {e}")
            raise

    def get_validation_rules(self):
        """
        Define las reglas de calidad. 
        Cada query debe estar diseñada para CONTAR LAS ANOMALÍAS.
        Si el resultado es 0, la prueba pasa. Si es > 0, la prueba falla.
        """
        return [
            # ---------------------------------------------------------
            # 1. COMPLETITUD (Ausencia de Nulos en campos críticos)
            # ---------------------------------------------------------
            {
                "name": "Completitud: Clientes sin ID nulo",
                "query": "SELECT COUNT(*) FROM `{project}.stg_fintrust.stg_customers` WHERE customer_id IS NULL"
            },
            {
                "name": "Completitud: Créditos sin fecha de originación",
                "query": "SELECT COUNT(*) FROM `{project}.stg_fintrust.stg_loans` WHERE origination_date IS NULL"
            },

            # ---------------------------------------------------------
            # 2. CALIDAD / UNICIDAD (No duplicados)
            # ---------------------------------------------------------
            {
                "name": "Unicidad: IDs de Crédito no duplicados",
                "query": """
                    SELECT COUNT(*) FROM (
                        SELECT loan_id FROM `{project}.stg_fintrust.stg_loans` 
                        GROUP BY loan_id HAVING COUNT(*) > 1
                    )
                """
            },
            {
                "name": "Unicidad: IDs de Pago no duplicados",
                "query": """
                    SELECT COUNT(*) FROM (
                        SELECT payment_id FROM `{project}.stg_fintrust.stg_payments` 
                        GROUP BY payment_id HAVING COUNT(*) > 1
                    )
                """
            },

            # ---------------------------------------------------------
            # 3. VERACIDAD / COHERENCIA LÓGICA (Reglas de Negocio)
            # ---------------------------------------------------------
            {
                "name": "Veracidad: Montos de préstamos mayores a cero",
                "query": "SELECT COUNT(*) FROM `{project}.stg_fintrust.stg_loans` WHERE principal_amount <= 0"
            },
            {
                "name": "Coherencia: Un cliente en mora no puede tener 'dias_mora' = 0",
                "query": """
                    SELECT COUNT(*) FROM `{project}.analytics_fintrust.dm_consolidado_creditos` 
                    WHERE is_fully_paid = FALSE 
                      AND due_date < CURRENT_DATE() 
                      AND days_late = 0
                """
            },
            {
                "name": "Coherencia: Cuota totalmente pagada debe tener fecha de pago",
                "query": """
                    SELECT COUNT(*) FROM `{project}.analytics_fintrust.dm_consolidado_creditos` 
                    WHERE is_fully_paid = TRUE 
                      AND ultima_fecha_pago IS NULL
                """
            }
        ]

    def run_validations(self):
        rules = self.get_validation_rules()
        failed_tests = 0

        print("-" * 50)
        print(" EJECUTANDO SUITE DE DATA QUALITY ".center(50, "="))
        print("-" * 50)

        for rule in rules:
            query = rule["query"].replace("{project}", self.project_id)
            try:
                # Ejecutamos la consulta y obtenemos el primer valor de la primera fila
                query_job = self.client.query(query)
                results = list(query_job.result())
                anomalies_count = results[0][0]

                if anomalies_count == 0:
                    print(f"✅ [PASS] {rule['name']}")
                else:
                    print(f"❌ [FAIL] {rule['name']} -> Se encontraron {anomalies_count} anomalías.")
                    failed_tests += 1

            except Exception as e:
                print(f"⚠️ [ERROR] No se pudo ejecutar '{rule['name']}': {e}")
                failed_tests += 1

        print("-" * 50)
        if failed_tests == 0:
            print("💎 RESULTADO: Datos 100% íntegros. Listo para producción.")
        else:
            print(f"🚨 RESULTADO: Se encontraron fallos en {failed_tests} regla(s) de calidad.")
            # Opcional: raise Exception("Data Quality Check Failed") para detener el pipeline en Airflow/Composer

if __name__ == "__main__":
    validator = DataQualityValidator()
    validator.run_validations()