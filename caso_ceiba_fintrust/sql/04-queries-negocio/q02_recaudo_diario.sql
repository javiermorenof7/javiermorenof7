SELECT
    ultima_fecha_pago AS fecha_recaudo,
    SUM(total_paid_amount) AS recaudo_total,
    SUM(
        CASE 
            WHEN ultima_fecha_pago > due_date THEN total_paid_amount 
            ELSE 0 
        END
    ) AS recaudo_cuotas_vencidas
FROM `proyecto-prueba-367518.analytics_fintrust.dm_consolidado_creditos`
WHERE total_paid_amount > 0
GROUP BY 1
ORDER BY fecha_recaudo DESC;