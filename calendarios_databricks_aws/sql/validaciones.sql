-- Consultas para revisar las tablas después de una ejecución.
-- Cambiar el catálogo a aulaviva_prod para revisar producción.
USE CATALOG aulaviva_dev;

-- 1. Qué archivos se han cargado y cuántas versiones tiene cada uno
SELECT archivo, COUNT(*) AS versiones, MAX(fecha_ingesta) AS ultima_carga, MAX_BY(filas, fecha_ingesta) AS filas_vigentes
FROM bronze.control_calendario
GROUP BY archivo
ORDER BY archivo;

-- 2. Filas apartadas en Silver y por qué
SELECT archivo, motivo, alianza, cohorte, periodo, asignatura, fecha_inicio_origen, fecha_fin_origen
FROM silver.calendario_rechazados
ORDER BY archivo, cohorte, periodo;

-- 3. La llave de Silver no se repite (debe devolver cero filas)
SELECT alianza, programa, cohorte, periodo, asignatura, COUNT(*) AS veces
FROM silver.calendario
GROUP BY ALL
HAVING COUNT(*) > 1;

-- 4. Calendario final por alianza
SELECT alianza, programa, cohorte, periodo, inicio_periodo, fin_periodo, semanas, asignaturas
FROM gold.calendario_periodos
ORDER BY alianza, programa, cohorte, periodo;
