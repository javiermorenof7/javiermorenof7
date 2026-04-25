--------------------------------------------
-- Metricas adicionales para BI
-- Granularidad: 1 Fila = 1 Cliente
-- Estas métricas permiten identificar a los clientes más riesgosos y priorizar acciones de gestión.    
--------------------------------------------

-- Análisis Pareto (Concentración de Deuda)
-- Esta identifica al 20% de los clientes que representan el 80% del riesgo.

CREATE OR REPLACE TABLE `proyecto-prueba-367518.analytics_fintrust.bi_analisis_pareto` AS
WITH DeudaAcumulada AS (
    SELECT 
        full_name,
        SUM(saldo_pendiente) AS deuda_total,
        SUM(SUM(saldo_pendiente)) OVER(ORDER BY SUM(saldo_pendiente) DESC) AS suma_acumulada,
        SUM(SUM(saldo_pendiente)) OVER() AS deuda_global
    FROM `proyecto-prueba-367518.analytics_fintrust.dm_master_creditos`
    WHERE estado_gestion = 'MORA'
    GROUP BY 1
)
SELECT 
    full_name,
    deuda_total,
    ROUND((suma_acumulada / deuda_global) * 100, 2) AS porcentaje_pareto_acumulado,
    CASE 
        WHEN (suma_acumulada / deuda_global) <= 0.80 THEN 'ALTA PRIORIDAD (Top 80%)'
        ELSE 'BAJA PRIORIDAD'
    END AS categoria_prioridad
FROM DeudaAcumulada;