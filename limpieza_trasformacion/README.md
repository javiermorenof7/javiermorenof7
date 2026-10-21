# Limpieza y transformación

Un cuaderno que convierte un Excel desordenado en un conjunto de datos limpio.

El libro de origen tiene dos hojas (`TC` y `UO`) con las fechas en columnas y una fila por zona de cada vicepresidencia de empresas. El cuaderno transpone cada hoja, nombra las columnas por región y zona, une las dos hojas y grafica las series en el tiempo antes de exportar el resultado.

## Contenido

| Ruta | Qué contiene |
| --- | --- |
| [transformacion.ipynb](transformacion.ipynb) | Lectura, transformación, gráficas y exportación. |
| [data/datos.xlsx](data/datos.xlsx) | Libro de origen. |
| [data/datos_transformados.csv](data/datos_transformados.csv) | Resultado limpio. |
| [procesamiento/](procesamiento) | Ingesta y limpieza del PIB per cápita del Banco Mundial (datos reales). |
| [data/oro/](data/oro) | Resultado limpio de los datos del Banco Mundial. |

## Datos reales: PIB per cápita del Banco Mundial

El mismo problema (fechas en columnas, filas que no son datos) aparece en una fuente real: la descarga en CSV del [PIB per cápita en dólares actuales](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD) de los Indicadores del Desarrollo Mundial del Banco Mundial. Licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es).

El archivo llega con una marca BOM, cuatro filas de encabezado antes de las columnas, una columna vacía al final, un año por columna (1960 en adelante) y los agregados (Mundo, América Latina, "ingreso alto"...) mezclados con los países.

- `procesamiento/ingesta_banco_mundial.py` (bronce): baja el zip y guarda el indicador y los metadatos de países. Si el zip tiene la misma huella SHA-256 que la última vez, no reescribe bronce.
- `procesamiento/capas_banco_mundial.py` (plata y oro): salta el encabezado, quita la columna vacía, pasa los años a filas, separa los agregados usando los metadatos (un agregado no tiene región) y comprueba que todas las celdas del archivo ancho quedan contadas.

| Resultado | Celdas |
| --- | ---: |
| Celdas del archivo ancho | 17.556 |
| Aceptada (país y año con valor) | 10.465 |
| Agregado regional o por ingreso, no es país | 4.752 |
| País sin valor en el año | 2.339 |

En 2025, el PIB per cápita de Colombia (8.562 dólares) fue el 77 % del de América Latina y el Caribe (11.095) y el 59 % del mundial (14.406).

Los resultados están en `data/oro/`: `pib_per_capita_paises.csv` (una fila por país y año), `ultimo_valor_por_pais.csv` y `colombia_america_latina_mundo.csv`. Para correrlo: `python limpieza_trasformacion/procesamiento/ingesta_banco_mundial.py` y después `python limpieza_trasformacion/procesamiento/capas_banco_mundial.py`.

## Herramientas

Python con pandas, seaborn y matplotlib.
