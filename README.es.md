<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/pipeline-es-dark.svg">
  <img src="assets/pipeline-es-light.svg" alt="Javier Moreno, ingeniero de datos. Un pipeline que lleva los ficheros por las capas bronce, plata y oro hasta tableros y modelos." width="100%">
</picture>

[English](README.md) | Español

Soy ingeniero de datos, con un máster en Ingeniería de Datos. Diseño pipelines ETL y ELT, sobre todo en Google Cloud, y pongo en producción modelos predictivos y LLM sobre ellos.

[Portafolio](https://javiermorenof7.github.io/cv_portafolio/) | [LinkedIn](https://www.linkedin.com/in/francisco-javier-garcia-moreno-78b184166)

## Proyectos

Cada carpeta de este repositorio es un caso que resolví de principio a fin. Los datos de todos son ficticios.

### Pipelines en Google Cloud

| Proyecto | Qué hace |
| --- | --- |
| [Pipeline de datos de FinTrust](caso_gcp_fintrust) | Sustituye las descargas manuales de reportes de una fintech de crédito de consumo por un pipeline automatizado en BigQuery, con las decisiones técnicas y la evidencia de calidad de datos documentadas. |
| [Ingesta de datos de salud](analisis_gcp) | Carga ficheros CSV, TXT y Excel desde Cloud Storage a las capas bronce y plata de BigQuery. Lo orquesta Cloud Composer (Airflow) y todas las cargas son idempotentes. |
| [Seguros AltaVida](seguros_altavida) | Procesamiento de datos, machine learning y una arquitectura en la nube para llevar la analítica de una aseguradora de salud de soluciones puntuales a producción. |
| [Arquitectura de ventas](area_ventas) | Lleva un libro de ventas de un Excel local a una arquitectura escalable en Google Cloud. |

### Pipelines en AWS

| Proyecto | Qué hace |
| --- | --- |
| [Calendarios académicos en Databricks](calendarios_databricks_aws) | Lleva los calendarios que las universidades aliadas dejan en S3 por las capas bronce, plata y oro en tablas Delta de Databricks. Los ficheros que no han cambiado se omiten y las filas que no se pueden usar se apartan con su motivo. |

### IA

| Proyecto | Qué hace |
| --- | --- |
| [Agente de banca y e-commerce](ecomerce_agent) | Un asistente que compara el precio de un producto con el saldo del cliente antes de recomendarlo. Combina búsqueda semántica en el catálogo (FAISS) con los datos del propio cliente, y está hecho con LangChain. |

### Análisis

| Proyecto | Qué hace |
| --- | --- |
| [Riesgo de crédito](riesgo_credito) | Tasas de intermediación de la banca por tipo de entidad, tipo de crédito y plazo, para apoyar una estrategia de fondeo. |
| [Ausentismo en una fábrica](analisis_company) | Un modelo dimensional y una tabla única de análisis para explicar cómo afectan las ausencias a la productividad. |
| [Recomendación de productos](analisis_probabilistico_tiendas) | Un análisis probabilístico de si un producto es una buena recomendación para otro. |
| [Limpieza y transformación](limpieza_trasformacion) | Un notebook que convierte un Excel desordenado en un conjunto de datos limpio. |

## Herramientas

| Área | Qué uso |
| --- | --- |
| Lenguajes | Python, SQL, Scala |
| Pipelines | Spark, Databricks, Airflow, ODI, Pentaho, NiFi |
| Nube | Google Cloud, AWS, Azure |
| Bases de datos | BigQuery, PostgreSQL, MySQL, SQL Server |
| BI | Power BI, Tableau |
| IA | Modelos predictivos, visión artificial, despliegue de LLM |

## Aprendiendo ahora

Arquitecturas de datos en tiempo real, optimización de LLM y data mesh.
