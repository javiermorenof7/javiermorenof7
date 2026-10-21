import pandas as pd

# Maestro oficial de municipios del DANE (DIVIPOLA), descargado con ingesta_sivigila.py
df_divipola = pd.read_csv('analisis_gcp/data/raw/divipola.csv', dtype=str)

df_divipola = df_divipola.rename(columns={
    'cod_mpio': 'municipio_code', 'nom_mpio': 'municipio_name', 'cod_dpto': 'departamento_code',
    'dpto': 'departamento_name', 'tipo_municipio': 'tipo_municipio',
})

# El código se carga como entero, igual que lo cruza el procedimiento con las citas (05001 -> 5001)
df_divipola['municipio_code'] = df_divipola['municipio_code'].astype(int)
# Las coordenadas llegan con coma decimal
for columna in ['latitud', 'longitud']:
    df_divipola[columna] = df_divipola[columna].str.replace(',', '.').astype(float)

columnas = ['municipio_code', 'municipio_name', 'departamento_code', 'departamento_name',
            'tipo_municipio', 'latitud', 'longitud']
df_divipola[columnas].to_csv('analisis_gcp/procesamiento/DIVIPOLA_Municipios_clean.csv', index=False)
