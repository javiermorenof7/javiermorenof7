CREATE OR REPLACE TABLE `proyecto-prueba-367518.analytics_fintrust.bi_top_riesgo_mora` AS
SELECT
    loan_id,
    full_name AS cliente,
    segment AS segmento,
    MAX(days_late) AS dias_atraso_maximo,
    SUM(total_due_amount - total_paid_amount) AS saldo_total_pendiente
FROM `proyecto-prueba-367518.analytics_fintrust.dm_consolidado_creditos`
WHERE estado_gestion = 'MORA'
GROUP BY 1, 2, 3
ORDER BY dias_atraso_maximo DESC, saldo_total_pendiente DESC
LIMIT 10;