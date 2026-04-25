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