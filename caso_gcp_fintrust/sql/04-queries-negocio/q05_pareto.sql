--------------------------------------------
-- Metricas adicionales para BI
-- Granularidad: 1 Fila = 1 Cliente
-- Estas métricas permiten identificar a los clientes más riesgosos y priorizar acciones de gestión.    
--------------------------------------------

-- Análisis Pareto (Concentración de Deuda)
-- Esta identifica al 20% de los clientes que representan el 80% del riesgo.

CREATE OR REPLACE TABLE `proyecto-prueba-367518.analytics_fintrust.bi_analisis_pareto` AS

WITH DeudaPorCliente AS (
    -- 1. Agrupamos la deuda en mora por cada cliente
    SELECT 
        customer_id,
        full_name AS cliente,
        segment AS segmento,
        SUM(total_due_amount - COALESCE(total_paid_amount, 0)) AS saldo_en_mora
    FROM `proyecto-prueba-367518.analytics_fintrust.dm_consolidado_creditos`
    WHERE estado_gestion = 'MORA'
    GROUP BY 1, 2, 3
),
CalculoAcumulado AS (
    -- 2. Calculamos el acumulado fila por fila y el total global
    SELECT 
        customer_id,
        cliente,
        segmento,
        saldo_en_mora,
        -- Suma progresiva de la deuda ordenando desde el que más debe al que menos
        SUM(saldo_en_mora) OVER(ORDER BY saldo_en_mora DESC) AS deuda_acumulada,
        -- Suma total de toda la cartera en mora
        SUM(saldo_en_mora) OVER() AS gran_total_mora
    FROM DeudaPorCliente
)
-- 3. Generamos los porcentajes y la clasificación final
SELECT 
    customer_id,
    cliente,
    segmento,
    saldo_en_mora,
    ROUND((deuda_acumulada / gran_total_mora) * 100, 2) AS porcentaje_acumulado,
    CASE 
        WHEN (deuda_acumulada / gran_total_mora) <= 0.80 THEN 'TOP 80% (Prioridad Alta)'
        ELSE 'RESTO 20% (Prioridad Baja)'
    END AS clasificacion_pareto
FROM CalculoAcumulado
ORDER BY saldo_en_mora DESC;