import pandas as pd
from google.cloud import bigquery

# Inicializar cliente forzando el proyecto requerido
project_id = 'mi-proyecto-javier-500617'
client = bigquery.Client(project=project_id)

# Nombres de las tablas destino (Asegúrate de crear el dataset 'dataset_prueba' primero)
table_citas = f'{project_id}.dataset_prueba.citas_start'
table_divipola = f'{project_id}.dataset_prueba.divipola_municipios'

# ==========================================
# 1. Carga del archivo de Citas (TXT)
# ==========================================
# Estrategia: Como el separador es '|;|', pandas lo maneja bien con el engine de Python.
# Nota: En un entorno real, define el 'schema' explícito según el diccionario.
print("Cargando Citas...")
df_citas = pd.read_csv(
    'gs://javier-proyecto/Citas_Start_20220603.txt', 
    sep=r'\|;\|', 
    engine='python'
)
# Carga a BigQuery
job_config_citas = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
client.load_table_from_dataframe(df_citas, table_citas, job_config=job_config_citas).result()
print("Tabla de citas cargada exitosamente.")

# ==========================================
# 2. Carga del archivo DIVIPOLA (Excel)
# ==========================================
# Estrategia: BQ no soporta Excel directo. Lo pasamos por un DataFrame de Pandas.
print("Cargando Divipola...")
df_divipola = pd.read_excel('gs://javier-proyecto/Davipola_Municipios.xlsx')

job_config_divipola = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
client.load_table_from_dataframe(df_divipola, table_divipola, job_config=job_config_divipola).result()
print("Tabla Divipola cargada exitosamente.")