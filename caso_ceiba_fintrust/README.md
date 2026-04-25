Esta estructura es orientativa. Puedes adaptarla según tu criterio, pero debe
quedar claro dónde encontrar cada artefacto.

IDE-001-fintrust/
├── README.md # Documentación principal: contexto,
instrucciones de ejecución y decisiones clave
├── docs/
│ ├── decisiones-tecnicas.md # Supuestos, decisiones de diseño y
riesgos conocidos
│ └── evidencia-calidad-datos.md # Validaciones aplicadas y
resultados observados
├── sql/
│ ├── 01-raw/ # DDL y carga de tablas fuente en
raw_fintrust
│ │ └── create_raw_tables.sql
│ ├── 02-staging/ # Transformaciones intermedias,
limpieza y estandarización
│ │ └── stg_*.sql
│ ├── 03-analytics/ # Data mart y vistas analíticas
finales para BI
│ │ └── dm_*.sql o vw_*.sql
│ └── 04-queries-negocio/ # Consultas que responden las
preguntas del caso
│ ├── q01_desembolso_diario.sql
│ ├── q02_recaudo_diario.sql
│ ├── q03_cartera_por_cohorte.sql
│ ├── q04_top_atraso.sql
│ └── q05_dataset_bi.sql
├── python/

CASO PRÁCTICO
Ingeniero de Datos

│ ├── pipeline.py # Automatización ETL / orquestación
de pasos
│ ├── validations.py # Controles de calidad de datos
│ └── requirements.txt # Dependencias del proyecto
└── bonus/ # (Opcional) Propuesta de uso de
LLMs
└── llm_proposal.md

# FinTrust Data Pipeline - Caso Práctico Ceiba

Este proyecto automatiza la ingesta y transformación de datos financieros para la fintech **FinTrust**, consolidando indicadores de originación, recaudo y mora en Google BigQuery.

## 🚀 Arquitectura
Se implementó una arquitectura **ELT (Extract-Load-Transform)** siguiendo el patrón de capas de datos (Medallion):
1. **Raw**: Datos transaccionales tal cual vienen de la fuente.
2. **Staging**: Limpieza, tipado y estandarización.
3. **Analytics**: Modelado de Data Marts listos para consumo en BI (Power BI/Looker).

## 🛠️ Stack Tecnológico
- **Google BigQuery**: Data Warehouse serverless.
- **Python 3.13**: Orquestación y validaciones.
- **SQL (Standard SQL)**: Transformaciones y lógica de negocio.

## 📋 Requisitos e Instalación
1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`.
3. Instalar dependencias: `pip install -r python/requirements.txt`.
4. Configurar credenciales de GCP: `export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account.json"`.

## ⚙️ Ejecución
Para ejecutar el pipeline completo:
```bash
export GCP_PROJECT_ID="tu-id-de-proyecto"
python python/pipeline.py