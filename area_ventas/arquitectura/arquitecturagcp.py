import pandas as pd
import re
from google.cloud import bigquery

def clean_bq_header(name):
    """
    Limpia el encabezado para que cumpla con los estándares de BigQuery:
    Minúsculas, sin espacios, sin caracteres especiales y que no inicie con número.
    """
    name = str(name).strip()
    name = re.sub(r'[\s\-]+', '_', name)
    name = re.sub(r'[^\w]', '', name)
    name = name.lower()
    if name and name[0].isdigit():
        name = "_" + name
    return name

def upload_excel_to_bigquery(excel_file_path, project_id, dataset_id):
    print(f"Iniciando cliente de BigQuery para el proyecto: {project_id}")
    client = bigquery.Client(project=project_id)
    
    print(f"Leyendo el archivo base: {excel_file_path}")
    xls = pd.ExcelFile(excel_file_path)

    for sheet_name in xls.sheet_names:
        print(f"\nProcesando hoja: {sheet_name}...")
        
        # Usar la segunda línea del Excel como encabezados reales (ignora la descripción en español)
        df = pd.read_excel(xls, sheet_name=sheet_name, header=1)
        
        # 1. Limpieza de filas y columnas vacías
        df.dropna(axis=0, how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        cols_to_keep = [col for col in df.columns if not str(col).startswith('Unnamed')]
        df = df[cols_to_keep]
        
        # 2. Limpieza de encabezados para BigQuery
        df.columns = [clean_bq_header(col) for col in df.columns]
        
        # 3. Homologar tipos mixtos a String (Evita el error de PyArrow)
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
        
        safe_sheet_name = clean_bq_header(sheet_name)
        table_id = f"{project_id}.{dataset_id}.{safe_sheet_name}"
        
        # ---> NUEVO: Eliminar la tabla físicamente antes de la carga <---
        print(f"Eliminando tabla existente (si existe): {table_id} ...")
        client.delete_table(table_id, not_found_ok=True)
        
        # Configurar la nueva carga
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",  # Sobrescribe en caso de colisión
            autodetect=True,                     # Detecta tipos de datos automáticamente
        )
        
        print(f"Creando y subiendo nueva tabla a BigQuery: {table_id} ...")
        
        # Ejecutar el Job de carga desde el DataFrame
        job = client.load_table_from_dataframe(
            df, 
            table_id, 
            job_config=job_config
        )
        
        # Esperar a que el Job finalice de manera síncrona
        job.result()
        
        table = client.get_table(table_id)
        print(f"✅ Éxito: Se recreó la tabla y se cargaron {table.num_rows} filas en {table_id}")

# ==========================================
# Configuración y Ejecución
# ==========================================

if __name__ == "__main__":
    EXCEL_PATH = 'area_ventas/data/AdventureWorksSales.xlsx'
    
    # Credenciales y rutas de tu proyecto GCP
    PROJECT_ID = 'javier-proyecto-502616'
    DATASET_ID = 'ventas_bronce'
    
    upload_excel_to_bigquery(EXCEL_PATH, PROJECT_ID, DATASET_ID)
