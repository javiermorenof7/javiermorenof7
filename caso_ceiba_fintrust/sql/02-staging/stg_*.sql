-- Crear dataset para la capa de Staging
CREATE SCHEMA IF NOT EXISTS `proyecto-prueba-367518.stg_fintrust`
OPTIONS (
  location = 'us', -- O la región que prefieras, ej: 'us-east1'
  description = 'Capa intermedia para limpieza, tipado y normalización de datos transaccionales.',
  labels = [('env', 'dev'), ('team', 'data_eng')]
);