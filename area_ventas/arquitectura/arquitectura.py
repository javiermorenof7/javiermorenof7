import pandas as pd
import os
import re

def clean_bq_header(name):
    """
    Formatea el nombre de la columna para cumplir con los estándares de BigQuery:
    - Convierte a minúsculas.
    - Reemplaza espacios y guiones por guiones bajos (_).
    - Elimina cualquier carácter que no sea alfanumérico.
    - Asegura que no empiece con un número.
    """
    name = str(name).strip()
    
    # 1. Reemplazar uno o más espacios/guiones por un solo guion bajo
    name = re.sub(r'[\s\-]+', '_', name)
    
    # 2. Eliminar todo lo que no sea una letra, número o guion bajo
    name = re.sub(r'[^\w]', '', name)
    
    # 3. Convertir todo a minúsculas
    name = name.lower()
    
    # 4. BigQuery prefiere que las columnas no empiecen con números
    if name and name[0].isdigit():
        name = "_" + name
        
    return name

def export_to_bq_ready_csv(excel_file_path, output_folder):
    """
    Lee un archivo Excel, limpia las filas vacías, formatea los encabezados 
    para BigQuery y exporta cada hoja como CSV.
    """
    os.makedirs(output_folder, exist_ok=True)
    print(f"Leyendo el archivo base: {excel_file_path}")
    
    xls = pd.ExcelFile(excel_file_path)

    for sheet_name in xls.sheet_names:
        print(f"Procesando hoja: {sheet_name}...")
        
        # Leer la hoja actual
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # --- LIMPIEZA DE FILAS Y COLUMNAS VACÍAS ---
        # 1. Eliminar filas que estén completamente en blanco (sin ningún dato)
        df.dropna(axis=0, how='all', inplace=True)
        
        # 2. Eliminar columnas que estén completamente vacías
        df.dropna(axis=1, how='all', inplace=True)
        
        # 3. Omitir columnas sin encabezado real (Pandas las llama 'Unnamed: X')
        # Esto pasa cuando Excel detecta datos desplazados sin título
        cols_to_keep = [col for col in df.columns if not str(col).startswith('Unnamed')]
        df = df[cols_to_keep]
        
        # --- FORMATEO DE ENCABEZADOS PARA BIGQUERY ---
        # Aplicar la función clean_bq_header a cada columna
        df.columns = [clean_bq_header(col) for col in df.columns]
        
        # --- GUARDAR ARCHIVO ---
        # Limpiar también el nombre de la tabla (hoja)
        safe_sheet_name = clean_bq_header(sheet_name)
        csv_file_path = os.path.join(output_folder, f"{safe_sheet_name}.csv")
        
        # Guardar en CSV asegurando codificación utf-8
        df.to_csv(csv_file_path, index=False, encoding='utf-8')
        
        print(f"✅ Guardado (BQ Ready): {csv_file_path}")

# ==========================================
# Configuración y Ejecución
# ==========================================
if __name__ == "__main__":
    # Ruta de tu archivo Excel de origen
    EXCEL_PATH = 'area_ventas/data/AdventureWorksSales.xlsx' 
    
    # Nombre de la carpeta local donde se guardarán los CSVs
    # (Puede ser una ruta absoluta como 'C:/Users/TuUsuario/Documentos/CSVs')
    OUTPUT_FOLDER = 'area_ventas/data' 
    
    export_to_bq_ready_csv(EXCEL_PATH, OUTPUT_FOLDER)