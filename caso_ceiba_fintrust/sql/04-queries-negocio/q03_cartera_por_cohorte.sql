SELECT
    origination_cohort AS cohorte_originacion,
    SUM(
        CASE 
            WHEN days_late = 0 THEN (total_due_amount - total_paid_amount) 
            ELSE 0 
        END
    ) AS cartera_al_dia,
    SUM(
        CASE 
            WHEN days_late > 0 THEN (total_due_amount - total_paid_amount) 
            ELSE 0 
        END
    ) AS cartera_en_mora
FROM `proyecto-prueba-367518.analytics_fintrust.dm_consolidado_creditos`
-- Filtramos para analizar solo las cuotas que no se han pagado por completo
WHERE is_fully_paid = FALSE
GROUP BY 1
ORDER BY cohorte_originacion DESC;