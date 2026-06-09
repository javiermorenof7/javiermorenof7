# FinTrust Data Pipeline 

Este repositorio contiene el diseño e implementación de una solución analítica automatizada sobre Google Cloud Platform (BigQuery) para **FinTrust**, una fintech de crédito de consumo. El objetivo principal es eliminar los procesos manuales (descargas de reportes y cruces en Excel), reducir el *lag* analítico de 2 días a 0, y entregar un Data Mart centralizado y auditable listo para ser consumido por herramientas de BI (Looker).

💼 Para más detalles sobre mi experiencia y proyectos adicionales, te invito a visitar mi [Portafolio Profesional](https://javiermorenof7.github.io/cv_portafolio/).

Tablero BI
![Descripción de la imagen](docs/img/Tablero%20Data%20Loker%20BI.png)

### Estructura del Proyecto 📂
El proyecto está organizado en capas lógicas para separar la ingesta, transformación y consumo de datos:

```text
caso_gcp_fintrust/
├── bonus/                          # (Opcional) Propuesta de uso deLLMs
│   ├── llm_proposal.md             # Propuesta de uso de LLMs
├── img/                            # imganes de la solucion
├── docs/                           # Documentación y evidencias
│   ├── decisiones-tecnicas.md      # Justificación de arquitectura (Idempotencia, OBT)
│   └── evidencia-calidad-datos.md  # Resultados de pruebas
├── python/                         # Orquestación y Calidad de Datos
│   ├── pipeline.py                 # Script orquestador (ELT)
│   ├── validations.py              # Motor de reglas de Data Quality
│   └── requirements.txt            # Dependencias de Python
└── sql/                            # Transformaciones en BigQuery
    ├── 01-raw/                     # DDL y carga de datos crudos (MERGE idempotente)
    ├── 02-staging/                 # Limpieza, normalización y tipado
    ├── 03-analytics/               # Data Mart, One Big Table (OBT) y Vistas de BI
    └── 04-queries-negocio/         # Consultas para responder preguntas de negocio
├── README.md                       # Documentación principal: contexto
```
# Estructura GCP
![Descripción de la imagen](docs/img/Estructura%20Proyecto%20GCP.png)


# 🚀 Comenzando
 
Estas instrucciones te permitirán obtener una copia del proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas.
 
### 📋 Pre-requisitos
 
Asegúrate de tener instalado y configurado lo siguiente en tu entorno local:
 
- Python 3.9+
- Google Cloud CLI (`gcloud`)
- Una cuenta activa en GCP con un proyecto creado (ej. `proyecto-prueba-367518`)
- Permisos de **BigQuery Admin** en el proyecto asignado
### 🔧 Instalación y Ejecución
 
Sigue este paso a paso para configurar tu entorno y ejecutar el pipeline:
 
**1. Clona el repositorio:**
 
```bash
git clone https://github.com/javiermorenof7/javiermorenof7.git
cd caso_gcp_fintrust
```
 
**2. Configura el entorno virtual (Recomendado):**
 
```bash
python -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate
```
 
**3. Instala las dependencias:**
 
```bash
pip install -r python/requirements.txt
```
 
**4. Autenticación en Google Cloud (ADC):**
 
Inicia sesión y apunta al proyecto correcto para que Python acceda a BigQuery de forma segura.
 
```bash
gcloud auth application-default login
gcloud config set project proyecto-prueba-367518
export GCP_PROJECT_ID="proyecto-prueba-367518"
```
 
**5. Ejecuta el Pipeline de Datos:**
 
```bash
python python/pipeline.py
```
*Prueba ejecucion 1:*

Se observa que el ETL comienza a detectar errores

![Descripción de la imagen](docs/img/Ejecucion%20Falla%20Pipeline%20GCP.png)

*Prueba ejecucion 2:*

Se observa que el ETL detecta cuando la ruta del python no esta correcta, ademas que se visuliza que las ejecucion corrieron correctamente

![Descripción de la imagen](docs/img/ejecucion%20pepiline%20prueba%202.png)

*Prueba ejecucion 3:*

Una vez detectado el error se corrije y se valida nuevamente la ETL, la cual se procede a correr, validando que todo ejecuto correctamente, se puede tambien vizuzalizar los errores anteriores en el historial de trabajo en GCP Bigquery

![Descripción de la imagen](docs/img/Ejecucion%20Final%20ETL.png)
 
> 💡 **Nota:** La consola imprimirá un log en tiempo real confirmando la creación de las tablas capa por capa (`Raw ➔ Staging ➔ Analytics`).
 
---
 
## ⚙️ Ejecutando las Pruebas de Calidad de Datos
 
El sistema cuenta con un motor automatizado de Data Quality (`validations.py`). Para validarlo, ejecuta:
 
```bash
python3 caso_gcp_fintrust/python/validations.py
```
*Se puede vizulizar que se estan detectando errores en la data deacuerdo a las reglas de calidad que se definieron, esto se puede corregir en el codigo, detectando futuras anomalias en la calidad de los datos segun sea el caso*

![Descripción de la imagen](img/validaciones-data-quality.png)
 
### 🔩 Análisis de las Pruebas (End-to-End)
 
Las pruebas validan la integridad de la información directamente en BigQuery antes de que llegue a negocio:
 
| Tipo de Prueba | Descripción | Ejemplo de Regla Evaluada |
|---|---|---|
| **Completitud** | Evita la entrada de datos vacíos en campos críticos. | No pueden existir IDs nulos en clientes o créditos. |
| **Unicidad** | Garantiza la idempotencia del script. | No se pueden duplicar los IDs de pago en re-ejecuciones. |
| **Veracidad** | Valida la coherencia lógica y financiera. | Un cliente con estado de mora activa no puede tener 0 días de atraso. |
 
---
 
## 📦 Despliegue (Producción)
 
Actualmente, el despliegue es de tipo **Batch**. La lógica analítica vive nativamente en BigQuery, lo que permite que el visualizador de datos consulte la información a través de *DirectQuery* a las vistas del dataset `analytics_fintrust`.
 
Para un entorno productivo completo, se recomienda orquestar los scripts `pipeline.py` y `validations.py` dentro de un **DAG en Apache Airflow (Cloud Composer)**, programando su ejecución diaria (ej. `6:00 AM`) para garantizar datos frescos a primera hora de la jornada financiera.
 
---
 
## 🛠️ Construido Con
 
- **[Google BigQuery](https://cloud.google.com/bigquery)** — Data Warehouse serverless (Procesamiento SQL)
- **[Python 3](https://www.python.org/)** — Lenguaje principal para la orquestación
- **[google-cloud-bigquery](https://cloud.google.com/python/docs/reference/bigquery/latest)** — SDK oficial para la interacción con GCP
---
 
## ✒️ Autor
 
**Francisco Javier Garcia Moreno** — *Senior Data Engineer & BI*
 
💼 Para más detalles sobre mi experiencia y proyectos adicionales, te invito a visitar mi [Portafolio Profesional](https://javiermorenof7.github.io/cv_portafolio/).
 
---
 
## 🎁 Expresiones de Gratitud
 
- 🌐 A las comunidades de **Ingeniería de Datos** por promover arquitecturas pragmáticas y orientadas al valor de negocio.
- LLMs de ayuda Gemini y Cloude para darme ideas y desarrollar una excelente prueba tecnica a la altura de un inegiero de datos 
---
 
⌨️ Construido con ❤️ por **Francisco Javier Garcia Moreno**
 