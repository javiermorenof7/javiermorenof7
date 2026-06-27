CREATE OR REPLACE PROCEDURE `dataset_prueba.sp_usuarios_por_procedimiento`(
    nombre_departamento_in STRING
)
BEGIN
    -- Se estandariza el parámetro de entrada a mayúsculas
    DECLARE var_departamento STRING DEFAULT UPPER(nombre_departamento_in);

    -- Ejecución de la consulta solicitada
    SELECT 
        c.procedimiento,
        COUNT(DISTINCT c.identification_number) AS cantidad_usuarios_unicos
    FROM 
        `dataset_prueba.citas_start` c
    JOIN 
        `dataset_prueba.divipola_municipios` d
        -- Lógica de limpieza para el cruce entregada en los requerimientos
        ON CAST(CAST(c.municipio_code AS STRING) AS INT64) = d.municipio_code
    WHERE 
        UPPER(d.departamento_name) = var_departamento
    GROUP BY 
        c.procedimiento
    ORDER BY 
        cantidad_usuarios_unicos DESC;

END;



CALL dataset_prueba.sp_usuarios_por_procedimiento('BOGOTA D.C.')
