import pandas as pd

# Leer el excel (requiere openpyxl)
df_divipola = pd.read_excel('analisis_gcp/data/Davipola_Municipios.xlsx')

# Limpiar posibles ceros a la izquierda o problemas de casteo en el código
df_divipola['municipio_code'] = df_divipola['municipio_code'].astype(str)

# Guardar como CSV en GCS
df_divipola.to_csv('analisis_gcp/procesamiento/DIVIPOLA_Municipios_clean.csv', index=False)