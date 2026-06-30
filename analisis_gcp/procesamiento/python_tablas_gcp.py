import pandas as pd
from google.cloud import bigquery


project_id = 'mi-proyecto-javier-500617'
client = bigquery.Client(project=project_id)


table_citas = f'{project_id}.dataset_prueba.citas_start'
table_divipola = f'{project_id}.dataset_prueba.divipola_municipios'


print("Cargando Citas...")
df_citas = pd.read_csv(
    'gs://javier-proyecto/Citas_Start_20220603.txt', 
    sep=r'\|;\|', 
    engine='python'
)

job_config_citas = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
client.load_table_from_dataframe(df_citas, table_citas, job_config=job_config_citas).result()
print("Tabla de citas cargada exitosamente.")


print("Cargando Divipola...")
df_divipola = pd.read_excel('gs://javier-proyecto/Davipola_Municipios.xlsx')

job_config_divipola = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
client.load_table_from_dataframe(df_divipola, table_divipola, job_config=job_config_divipola).result()
print("Tabla Divipola cargada exitosamente.")