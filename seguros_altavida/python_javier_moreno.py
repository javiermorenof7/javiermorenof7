import os
import pandas as pd
import numpy as np

# 1. CARGA DE ARCHIVOS CON DELIMITADORES ESPECÍFICOS
df_aut = pd.read_csv('seguros_altavida/data/BaseAutorizaciones.txt', sep='\t')
df_sal = pd.read_csv('seguros_altavida/data/BaseSalario.txt', sep=',')
print(f"Carga inicial -> Autorizaciones: {len(df_aut)} | Salarios: {len(df_sal)}")

# 2. DEPURACIÓN DE BASE AUTORIZACIONES
for col in ['Tipo_Prestacion', 'Estado_Autorizacion']:
    df_aut[col] = df_aut[col].astype(str).str.strip().str.upper()

df_aut['Fecha'] = pd.to_datetime(df_aut['Fecha'], errors='coerce')
fechas_malas = df_aut['Fecha'].isna() | (df_aut['Fecha'] > pd.to_datetime('today'))
df_aut = df_aut[~fechas_malas]

val_ceros = (df_aut['Valor_Prestacion'] <= 0).sum()
df_aut = df_aut[df_aut['Valor_Prestacion'] > 0]
p99 = df_aut['Valor_Prestacion'].quantile(0.99)
outliers = (df_aut['Valor_Prestacion'] > p99).sum()
df_aut['Valor_Prestacion'] = np.where(df_aut['Valor_Prestacion'] > p99, p99, df_aut['Valor_Prestacion'])

print(f"[Evidencia Autorizaciones] Fechas eliminadas: {fechas_malas.sum()} | Valores <= $0 eliminados: {val_ceros} | Outliers topeados al P99 (${p99:,.0f}): {outliers}")

# 3. DEPURACIÓN DE BASE SALARIO
sal_invalido = (df_sal['salario'] <= 0) | (df_sal['salario'].isna())
df_sal.loc[sal_invalido, 'salario'] = 1300000
print(f"[Evidencia Salarios] Salarios inválidos imputados con SMLV: {sal_invalido.sum()}")

# 4. CRUCE Y CREACIÓN DE VARIABLES PREDICTIVAS
df_join = pd.merge(df_aut, df_sal, left_on='Afiliado_Id', right_on='Afiliado', how='inner')

# Variables creadas:
df_modelo = df_join.groupby('Afiliado_Id').agg(
    salario=('salario', 'first'),
    conteo_transacciones=('Autorizacion_id', 'count'),
    gasto_total=('Valor_Prestacion', 'sum'),
    tasa_anulacion_pct=('Estado_Autorizacion', lambda x: round(np.mean(x.isin(['ANULADA', 'RECHAZADA'])) * 100, 2))
).reset_index()

df_modelo['ratio_gasto_salario'] = round(df_modelo['gasto_total'] / df_modelo['salario'], 4)

print(f"\nCruce exitoso. Total afiliados en dataset analítico: {len(df_modelo)}")
print(df_modelo.head())

# 5. EXPORTACIÓN DEL ARCHIVO FINAL A LA RUTA 'data'
os.makedirs('data', exist_ok=True)
ruta_final = os.path.join('seguros_altavida/data', 'dataset_analitico_final.csv')
df_modelo.to_csv(ruta_final, index=False, encoding='utf-8')

print(f"\n[Éxito] Archivo final guardado correctamente en: {ruta_final}")
print(df_modelo.head())