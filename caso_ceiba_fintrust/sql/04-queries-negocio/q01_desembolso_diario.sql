CREATE OR REPLACE TABLE `proyecto-prueba-367518.analytics_fintrust.bi_desembolso_resumen` AS

WITH CreditosUnicos AS (
    SELECT DISTINCT 
        loan_id, 
        origination_date, 
        city, 
        segment, 
        loan_principal_amount
    FROM `proyecto-prueba-367518.analytics_fintrust.dm_consolidado_creditos`
)
SELECT
    origination_date AS fecha_desembolso,
    city AS ciudad,
    segment AS segmento,
    COUNT(loan_id) AS cantidad_creditos,
    SUM(loan_principal_amount) AS total_desembolsado
FROM CreditosUnicos
GROUP BY 1, 2, 3
ORDER BY fecha_desembolso DESC, ciudad, segmento;