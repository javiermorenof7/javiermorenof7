# Arquitectura de ventas

Cómo pasar un libro de ventas en Excel (AdventureWorks Sales) de un archivo local a una arquitectura en Google Cloud que escale: modelo en estrella, capas bronce, plata y oro, y el análisis del top 10 de productos por categoría.

El detalle completo está en [arquitectura/arquitectura.md](arquitectura/arquitectura.md).

## Contenido

| Ruta | Qué contiene |
| --- | --- |
| [arquitectura/arquitectura.md](arquitectura/arquitectura.md) | Diseño de la solución, stack propuesto, análisis de negocio y plan de trabajo del MVP. |
| [arquitectura/arquitectura.py](arquitectura/arquitectura.py) | Exporta cada hoja del Excel a un CSV con cabeceras válidas para BigQuery. |
| [arquitectura/arquitecturagcp.py](arquitectura/arquitecturagcp.py) | Carga cada hoja del Excel directamente en BigQuery. |
| [data/](data) | `AdventureWorksSales.xlsx`, el libro de origen. |
| [capturas/](capturas) | Diagrama de la arquitectura y resultado del top 10. |

![Arquitectura en Google Cloud](capturas/gcp.png)
