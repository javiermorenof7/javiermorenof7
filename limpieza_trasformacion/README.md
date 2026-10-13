# Limpieza y transformación

Un cuaderno que convierte un Excel desordenado en un conjunto de datos limpio.

El libro de origen tiene dos hojas (`TC` y `UO`) con las fechas en columnas y una fila por zona de cada vicepresidencia de empresas. El cuaderno transpone cada hoja, nombra las columnas por región y zona, une las dos hojas y grafica las series en el tiempo antes de exportar el resultado.

## Contenido

| Ruta | Qué contiene |
| --- | --- |
| [transformacion.ipynb](transformacion.ipynb) | Lectura, transformación, gráficas y exportación. |
| [data/datos.xlsx](data/datos.xlsx) | Libro de origen. |
| [data/datos_transformados.csv](data/datos_transformados.csv) | Resultado limpio. |

## Herramientas

Python con pandas, seaborn y matplotlib.
