CREATE OR REPLACE TABLE `proyecto-prueba-367518.analytics_fintrust.bi_recaudo_efectividad` AS

SELECT
    ultima_fecha_pago AS fecha_pago,
    SUM(total_paid_amount) AS recaudo_total_diario,
    -- Recaudo aplicado a cuotas que ya tenían días de mora al pagar
    SUM(CASE WHEN ultima_fecha_pago > due_date THEN total_paid_amount ELSE 0 END) AS recaudo_cartera_vencida,
    -- Recaudo de cuotas pagadas a tiempo o anticipadas
    SUM(CASE WHEN ultima_fecha_pago <= due_date THEN total_paid_amount ELSE 0 END) AS recaudo_preventivo
FROM `proyecto-prueba-367518.analytics_fintrust.dm_consolidado_creditos`
WHERE total_paid_amount > 0
GROUP BY 1;