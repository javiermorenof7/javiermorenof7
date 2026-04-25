-- Crear dataset para la capa de Analytics (Data Mart)
CREATE SCHEMA IF NOT EXISTS `proyecto-prueba-367518.analytics_fintrust`
OPTIONS (
  location = 'us',
  description = 'Capa analítica final con indicadores de originación, mora y recaudo listos para BI.',
  labels = [('env', 'dev'), ('team', 'analytics')]
);

-- ==============================================================================
-- TABLA CONSOLIDADA (ONE BIG TABLE)
-- Granularidad: 1 Fila = 1 Cuota (Installment)
-- ==============================================================================

CREATE OR REPLACE TABLE `proyecto-prueba-367518.analytics_fintrust.dm_consolidado_creditos` AS

-- 1. Agrupación de Pagos (Evita la duplicación de cuotas por pagos parciales)
WITH PagosAgrupados AS (
    SELECT 
        installment_id,
        MAX(payment_date) AS ultima_fecha_pago,
        SUM(payment_amount) AS total_pagado,
        STRING_AGG(DISTINCT payment_channel, ', ') AS canales_de_pago
    FROM `proyecto-prueba-367518.stg_fintrust.stg_payments`
    GROUP BY installment_id
)

-- 2. Cruce Maestro
SELECT 
    -- ----------------------------------------
    -- LLAVES Y DIMENSIONES DE CLIENTE
    -- ----------------------------------------
    i.installment_id,
    l.loan_id,
    c.customer_id,
    c.full_name,
    c.city,
    c.segment,
    c.monthly_income,
    
    -- ----------------------------------------
    -- DIMENSIONES DEL CRÉDITO (LOAN)
    -- ----------------------------------------
    l.origination_date,
    FORMAT_DATE('%Y-%m', l.origination_date) AS origination_cohort, -- Cohorte para análisis
    l.principal_amount AS loan_principal_amount,
    l.annual_rate,
    l.term_months,
    l.loan_status,
    l.product_type,
    
    -- ----------------------------------------
    -- MÉTRICAS DE LA CUOTA (INSTALLMENT)
    -- ----------------------------------------
    i.installment_number,
    i.due_date,
    i.principal_due,
    i.interest_due,
    i.total_due_amount,
    i.installment_status,
    
    -- ----------------------------------------
    -- MÉTRICAS DE RECAUDO (PAYMENTS)
    -- ----------------------------------------
    -- COALESCE asegura que las cuotas sin pago muestren 0 en lugar de NULL
    COALESCE(p.total_pagado, 0) AS total_paid_amount,
    p.ultima_fecha_pago,
    p.canales_de_pago,
    
    -- ----------------------------------------
    -- REGLAS DE CALIDAD Y NEGOCIO CALCULADAS
    -- ----------------------------------------
    -- 1. Bandera de cuota cubierta
    CASE 
        WHEN COALESCE(p.total_pagado, 0) >= i.total_due_amount THEN TRUE
        ELSE FALSE
    END AS is_fully_paid,

    -- 2. Días de mora exactos al momento de la foto
    CASE 
        -- Si sigue en mora, calculamos contra la fecha actual
        WHEN i.installment_status IN ('LATE', 'DUE') AND CURRENT_DATE() > i.due_date 
            THEN DATE_DIFF(CURRENT_DATE(), i.due_date, DAY)
        -- Si ya pagó, pero pagó tarde, calculamos el retraso histórico
        WHEN i.installment_status = 'PAID' AND p.ultima_fecha_pago > i.due_date 
            THEN DATE_DIFF(p.ultima_fecha_pago, i.due_date, DAY)
        ELSE 0 
    END AS days_late

FROM `proyecto-prueba-367518.stg_fintrust.stg_installments` i
-- INNER JOIN hacia arriba: Toda cuota debe tener un crédito y un cliente (Integridad Referencial)
INNER JOIN `proyecto-prueba-367518.stg_fintrust.stg_loans` l 
    ON i.loan_id = l.loan_id
INNER JOIN `proyecto-prueba-367518.stg_fintrust.stg_customers` c 
    ON l.customer_id = c.customer_id
-- LEFT JOIN hacia pagos: Una cuota puede no tener pagos aún
LEFT JOIN PagosAgrupados p 
    ON i.installment_id = p.installment_id;