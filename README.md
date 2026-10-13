<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/pipeline-en-dark.svg">
  <img src="assets/pipeline-en-light.svg" alt="Javier Moreno, data engineer. A pipeline that takes files through bronze, silver and gold layers to dashboards and models." width="100%">
</picture>

English | [Español](README.es.md)

I'm a data engineer with a master's degree in Data Engineering. I design ETL and ELT pipelines, mostly on Google Cloud, and I put predictive models and LLMs into production on top of them.

[Portfolio](https://javiermorenof7.github.io/cv_portafolio/) | [LinkedIn](https://www.linkedin.com/in/francisco-javier-garcia-moreno-78b184166)

## Projects

Each folder in this repository is a case I worked through end to end. The data in all of them is fictional.

### Pipelines on Google Cloud

| Project | What it does |
| --- | --- |
| [FinTrust data pipeline](caso_gcp_fintrust) | Replaces manual report downloads at a consumer-credit fintech with an automated pipeline in BigQuery, with documented technical decisions and data-quality evidence. |
| [Health data ingestion](analisis_gcp) | Loads CSV, TXT and Excel files from Cloud Storage into bronze and silver layers in BigQuery. Cloud Composer (Airflow) runs it, and every load is idempotent. |
| [Seguros AltaVida](seguros_altavida) | Data processing, machine learning and a cloud architecture to take a health insurer's analytics from one-off solutions to production. |
| [Sales architecture](area_ventas) | Takes a sales workbook from a local Excel file to an architecture on Google Cloud that scales. |

### AI

| Project | What it does |
| --- | --- |
| [Banking and e-commerce agent](ecomerce_agent) | An assistant that checks a product's price against the customer's balance before recommending it. It combines semantic search over the catalogue (FAISS) with the customer's own data, built with LangChain. |

### Analysis

| Project | What it does |
| --- | --- |
| [Credit risk](riesgo_credito) | Intermediation rates across banks, by entity type, credit type and term, to support a funding strategy. |
| [Absenteeism at a manufacturer](analisis_company) | A dimensional model and a single analysis table to explain how absences affect productivity. |
| [Product recommendations](analisis_probabilistico_tiendas) | A probabilistic analysis of whether one product is a good recommendation for another. |
| [Cleaning and transformation](limpieza_trasformacion) | A notebook that turns a messy Excel file into a clean dataset. |

## Tools

| Area | What I use |
| --- | --- |
| Languages | Python, SQL, Scala |
| Pipelines | Spark, Airflow, ODI, Pentaho, NiFi |
| Cloud | Google Cloud, AWS, Azure |
| Databases | BigQuery, PostgreSQL, MySQL, SQL Server |
| BI | Power BI, Tableau |
| AI | Predictive models, computer vision, LLM deployment |

## Learning now

Real-time data architectures, LLM optimization and data mesh.
