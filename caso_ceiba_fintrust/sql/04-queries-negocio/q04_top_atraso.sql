SELECT
    loan_id,
    full_name AS nombre_cliente,
    MAX(days_late) AS dias_maximo_atraso,
    SUM(total_due_amount - total_paid_amount) AS saldo_pendiente_total
FROM `proyecto-prueba-367518.analytics_fintrust.dm_consolidado_creditos`
WHERE is_fully_paid = FALSE
GROUP BY 1, 2
ORDER BY dias_maximo_atraso DESC, saldo_pendiente_total DESC
LIMIT 10;