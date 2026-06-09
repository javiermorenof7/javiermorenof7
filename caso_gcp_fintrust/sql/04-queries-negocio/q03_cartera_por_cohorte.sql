CREATE OR REPLACE TABLE `proyecto-prueba-367518.analytics_fintrust.bi_cartera_cohortes` AS
SELECT
    origination_cohort AS cohorte,
    -- Saldo que aún no se vence
    SUM(CASE WHEN days_late = 0 THEN (total_due_amount - total_paid_amount) ELSE 0 END) AS saldo_al_dia,
    -- Saldo que ya pasó su fecha límite y no se ha pagado
    SUM(CASE WHEN days_late > 0 THEN (total_due_amount - total_paid_amount) ELSE 0 END) AS saldo_en_mora,
    -- Indicador de morosidad (Mora / Total pendiente)
    SAFE_DIVIDE(
        SUM(CASE WHEN days_late > 0 THEN (total_due_amount - total_paid_amount) ELSE 0 END),
        SUM(total_due_amount - total_paid_amount)
    ) * 100 AS porcentaje_mora
FROM `proyecto-prueba-367518.analytics_fintrust.dm_consolidado_creditos`
WHERE is_fully_paid = FALSE
GROUP BY 1;