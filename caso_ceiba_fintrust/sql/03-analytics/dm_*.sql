-- Crear dataset para la capa de Analytics (Data Mart)
CREATE SCHEMA IF NOT EXISTS `proyecto-prueba-367518.analytics_fintrust`
OPTIONS (
  location = 'us',
  description = 'Capa analítica final con indicadores de originación, mora y recaudo listos para BI.',
  labels = [('env', 'dev'), ('team', 'analytics')]
);