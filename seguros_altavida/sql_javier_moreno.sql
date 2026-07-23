
-- 1. Autorizaciones y valor total por Tipo_Prestacion y Estado_Autorizacion
SELECT 
    Tipo_Prestacion,
    Estado_Autorizacion,
    COUNT(Autorizacion_id) AS numero_autorizaciones,
    SUM(Valor_Prestacion) AS valor_total
FROM `javier-proyecto-502616.seguros_altavida.BaseAutorizaciones`
GROUP BY Tipo_Prestacion, Estado_Autorizacion
ORDER BY valor_total DESC;

-- 2. Valor total autorizado por rango salarial (Cruce y Expresión Condicional)
SELECT 
    CASE 
        WHEN s.salario <= 1300000 THEN '1. Hasta 1 SMLV'
        WHEN s.salario <= 2600000 THEN '2. De 1 a 2 SMLV'
        WHEN s.salario <= 5200000 THEN '3. De 2 a 4 SMLV'
        ELSE '4. Más de 4 SMLV'
    END AS rango_salarial,
    COUNT(a.Autorizacion_id) AS total_solicitudes,
    SUM(a.Valor_Prestacion) AS valor_total_autorizado
FROM `javier-proyecto-502616.seguros_altavida.BaseAutorizaciones` a
INNER JOIN `javier-proyecto-502616.seguros_altavida.BaseSalario` s
    ON a.Afiliado_Id = s.Afiliado
GROUP BY rango_salarial
ORDER BY rango_salarial ASC;

-- 3. Top 5 afiliados con mayor valor autorizado acumulado
SELECT 
    Afiliado_Id,
    COUNT(Autorizacion_id) AS conteo_prestaciones,
    SUM(CAST(Valor_Prestacion AS INT64)) AS valor_total_autorizado
FROM `javier-proyecto-502616.seguros_altavida.BaseAutorizaciones`
GROUP BY Afiliado_Id
ORDER BY valor_total_autorizado DESC
LIMIT 5;

-- 4. Porcentaje de autorizaciones "PAGADA" respecto al total, por mes
SELECT 
    FORMAT_DATE('%Y-%m', Fecha) AS mes_anio,
    COUNT(Autorizacion_id) AS total_autorizaciones,
    COUNTIF(Estado_Autorizacion = 'PAGADA') AS total_pagadas,
    ROUND((COUNTIF(Estado_Autorizacion = 'PAGADA') / COUNT(Autorizacion_id)) * 100, 2) AS porcentaje_pagadas
FROM `javier-proyecto-502616.seguros_altavida.BaseAutorizaciones`
GROUP BY mes_anio
ORDER BY mes_anio ASC;