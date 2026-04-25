-- Crear dataset para la capa de Staging
CREATE SCHEMA IF NOT EXISTS `proyecto-prueba-367518.stg_fintrust`
OPTIONS (
  location = 'us', -- O la región que prefieras, ej: 'us-east1'
  description = 'Capa intermedia para limpieza, tipado y normalización de datos transaccionales.',
  labels = [('env', 'dev'), ('team', 'data_eng')]
);

-- ==============================================================================
-- CAPA DE STAGING: Limpieza, normalización y tipado de datos transaccionales
-- ==============================================================================

-- 1. Staging de Clientes (Normalización de ciudades y textos)
CREATE OR REPLACE TABLE `proyecto-prueba-367518.stg_fintrust.stg_customers` AS
SELECT 
    TRIM(customer_id) AS customer_id,
    UPPER(TRIM(full_name)) AS full_name,
    CASE 
        WHEN UPPER(TRIM(city)) IN ('BOGOTA', 'BOGOTÁ', 'BOGOTÁ D.C.', 'BOG') THEN 'BOGOTÁ'
        WHEN UPPER(TRIM(city)) IN ('MEDELLIN', 'MEDELLÍN', 'MDE') THEN 'MEDELLÍN'
        WHEN UPPER(TRIM(city)) IN ('CALI', 'CLO') THEN 'CALI'
        ELSE UPPER(TRIM(city)) 
    END AS city,
    UPPER(TRIM(segment)) AS segment,
    CAST(monthly_income AS NUMERIC) AS monthly_income,
    CAST(created_at AS DATE) AS created_at
FROM `proyecto-prueba-367518.raw_fintrust.customers`
WHERE customer_id IS NOT NULL;

-- 2. Staging de Créditos (Tipado estricto)
CREATE OR REPLACE TABLE `proyecto-prueba-367518.stg_fintrust.stg_loans` AS
SELECT 
    TRIM(loan_id) AS loan_id,
    TRIM(customer_id) AS customer_id,
    CAST(origination_date AS DATE) AS origination_date,
    CAST(principal_amount AS NUMERIC) AS principal_amount,
    CAST(annual_rate AS NUMERIC) AS annual_rate,
    CAST(term_months AS INT64) AS term_months,
    UPPER(TRIM(loan_status)) AS loan_status,
    UPPER(TRIM(product_type)) AS product_type
FROM `proyecto-prueba-367518.raw_fintrust.loans`
WHERE loan_id IS NOT NULL;

-- 3. Staging de Cuotas (Cálculo de monto total adeudado)
CREATE OR REPLACE TABLE `proyecto-prueba-367518.stg_fintrust.stg_installments` AS
SELECT 
    TRIM(installment_id) AS installment_id,
    TRIM(loan_id) AS loan_id,
    CAST(installment_number AS INT64) AS installment_number,
    CAST(due_date AS DATE) AS due_date,
    CAST(principal_due AS NUMERIC) AS principal_due,
    CAST(interest_due AS NUMERIC) AS interest_due,
    (CAST(principal_due AS NUMERIC) + CAST(interest_due AS NUMERIC)) AS total_due_amount,
    UPPER(TRIM(installment_status)) AS installment_status
FROM `proyecto-prueba-367518.raw_fintrust.installments`
WHERE installment_id IS NOT NULL;

-- 4. Staging de Pagos (Filtro por pagos únicamente confirmados)
CREATE OR REPLACE TABLE `proyecto-prueba-367518.stg_fintrust.stg_payments` AS
SELECT 
    TRIM(payment_id) AS payment_id,
    TRIM(loan_id) AS loan_id,
    TRIM(installment_id) AS installment_id,
    CAST(payment_date AS DATE) AS payment_date,
    CAST(payment_amount AS NUMERIC) AS payment_amount,
    UPPER(TRIM(payment_channel)) AS payment_channel,
    UPPER(TRIM(payment_status)) AS payment_status,
    CAST(loaded_at AS TIMESTAMP) AS loaded_at
FROM `proyecto-prueba-367518.raw_fintrust.payments`
WHERE payment_id IS NOT NULL
  AND UPPER(TRIM(payment_status)) = 'CONFIRMED';