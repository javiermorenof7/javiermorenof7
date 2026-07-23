# Seguros Altavida

Seguros Altavida es una compañía de seguros que administra el aseguramiento en salud de sus
afiliados. El área de Transformación Operacional analiza las autorizaciones de prestaciones
(procedimientos y medicamentos) para apoyar la toma de decisiones sobre cobertura, costo y
calidad de la operación. La compañía quiere escalar sus iniciativas de analítica e inteligencia
artificial: pasar de soluciones puntuales a soluciones robustas, seguras y escalables, integradas con
sus sistemas core y desplegadas en la n ube empresarial. Esta prueba evalúa su profundidad técnica
en procesamiento de datos, machine learning e IA, y —de forma central — su capacidad para diseñar
arquitecturas de IA escalables, integraciones y puesta en producción (MLOps).

# 🚀 Arquitectura y Modelado de IA: Autorizaciones Médicas (EPS)

Este documento detalla las decisiones técnicas, metodológicas y de arquitectura para la implementación de soluciones de Inteligencia Artificial (ML, NLP y GenAI) sobre la nube de Google Cloud Platform (GCP)(Esta fue Opcional para manejar este caso de uso), integradas al flujo operativo y core de autorizaciones médicas.

---
## 🛠️ Parte A – Procesamiento e Ingeniería de Datos en Python

El objetivo de esta etapa fue construir un pipeline de datos modular, autocontenido y reproducible que ingesta los archivos planos crudos, soluciona problemas de calidad de datos, genera nuevas variables analíticas, para modelamiento de IA y automatiza la carga hacia un centro de datos en la nube (Google BigQuery).

### 1. Ingesta y Estandarización
* **Manejo de Delimitadores:** Se configuro la lectura adaptada a la estructura de cada fuente plana, procesando `BaseAutorizaciones.txt` con separaciones por tabulación (`\t`) y `BaseSalario.txt` con delimitación por comas (`,`).
* **Limpieza de Texto:** Se aplico estandarizacion (`strip()` + `upper()`) sobre las columnas categóricas (`Tipo_Prestacion` y `Estado_Autorizacion`) para eliminar espacios laterales invisibles producidos en la digitación y evitar la duplicidad de categorias por inconsistencias entre mayusculas y minúsculas.

Para mas informacion se decidicio implementar dos python:

> **RECOMENDACION: Para usar el Python ejecutar el Requirements.txt de este proyecto

 - Uno para manejar los datos en OnPremise y Otro para subir la informacion 

 - OnPremise

![Descripción de la imagen](/seguros_altavida/capturas/1.png)
![Descripción de la imagen](/seguros_altavida/capturas/2.png)

 - GCP (Ejecucion Python) Ejeucion en la Nube

 Creacion de las tablas una vez se ejecuto el proceso

 ![Descripción de la imagen](/seguros_altavida/capturas/3.png)

 Tablas CREADAS
 - BaseAutorizaciones
 ![Descripción de la imagen](/seguros_altavida/capturas/4.png)

 - BaseAutorizaciones
 ![Descripción de la imagen](/seguros_altavida/capturas/5.png)

  - BaseSalario
 ![Descripción de la imagen](/seguros_altavida/capturas/6.png)

 - Consulta Base autorizaciones
 ![Descripción de la imagen](/seguros_altavida/capturas/7.png)

---
## Parte B – SQL
# Concusltas SQL

 Se realiza las conusltas SQL para dar repsuesta a las preguntas de la data solicitada 

 - 1. Por Tipo_Prestacion y Estado_Autorizacion, el número de autorizaciones y el valor total, ordenado de mayor a menor valor
 ![Descripción de la imagen](/seguros_altavida/capturas/8.png)
 - 2. Uniendo ambas tablas, el valor total autorizado por rango salarial. Construya los rangos con, una expresión condicional
![Descripción de la imagen](/seguros_altavida/capturas/9.png)
 - 3. Los 5 afiliados con mayor valor autorizado acumulado
 ![Descripción de la imagen](/seguros_altavida/capturas/10.png)
 - 4. Porcentaje de autorizaciones “PAGADA” respecto al total, por mes
 ![Descripción de la imagen](/seguros_altavida/capturas/11.png)
 ![Descripción de la imagen](/seguros_altavida/capturas/12.png)


# ☁️ Parte D – Arquitecura IA en GCP

Propuesta nativa en **GCP** conectada al BigQuery actual (`javier-proyecto-502616`).

## 1. Componentes y Flujo (Todo gira en torno a Vertex AI)
* **Ingesta:** Pub/Sub para streaming en vivo y Cloud Storage (GCS) para batch de noche.
* **Datos y Variables:** BigQuery como Data Warehouse.
  * **DESTACADO - Vertex AI Feature Store:** Es el cerebro. Centralisa las variables (`ratio_gasto_salario`, etc.) en un solo sitio y las entrega en **menos de 10ms** para entrenar o predecir en vivo.
* **Procesamiento:** Cloud Dataflow para limpiar datos. **Vertex AI Pipelines** orquesta todo y reentrena el modelo LightGBM automatico sin meter mano.
* **SERVICIO DE MODELOS (Vertex AI):**
  * **Anulaciones:** Desplegado en **Vertex AI Endpoints** (REST de baja latencia para ventanilla).
  * **Asistente RAG:** En Cloud Run, conectado directo a **Vertex AI Gemini API** y usando **BigQuery Vector Search**.
* **Salida:** Apigee / API Gateway para seguridad y exponer APIs al portal de la EPS.

## 2. Escalabilidad y Costos
* **DESTACADO - SERVERLESS:** Cloud Run y **Vertex AI Endpoints** auto-escalan solos en picos (ej. lunes am o cierres) y bajan a **cero replicas** de madrugada para no gastar plata.
* **Tiempo Real (<300ms):** Clave para avisarle al asesor en pantalla si el tramite va a ser rechazado antes de enviarlo.
* **Ahorro:** Tablas particionadas en BigQuery y maquinas spot en Vertex AI para entrenar baratisimo.

## 3. Seguridad y Datos Sensibles
* **Cumplimiento:** HIPAA y Ley 1581 / GDPR.
* **DLP:** Cloud DLP enmascara datos sensibles (cedulas, historia clinica) antes de guardarlos.
* **Seguridad:** Cifrado CMEK, IAM por menor privilegio y todo aislado en una VPC Service Controls.
* **DESTACADO - TRAZABILIDAD:** Con **Vertex AI ML Metadata** y Audit Logs sabemos exactamente que vercion del modelo o que pdf del RAG hizo que se negara una cobertura (clave para temas legales).

## 4. Por que GCP y no Kubernetes propio?
* **Por que GCP / Vertex:** Es *NoOps* (cero mantenimiento). Conecta perfecto BigQuery con **Vertex AI y Gemini** sin complicarnos la vida.
* **Que descartamos:** Armar clusteres Kubernetes (GKE/EKS) con Postgre y motores vectoriales open source (Milvus/Qdrant).
* **Por que se descarto:** Nesecitariamos un equipo DevOps solo para parchar y mantener servidores. Saldria mas caro por infraestructura subutilisada y mucho riesgo de caidas en horas pico.

## 5. Integracion con el Core

| Patrón | Para que se usa | Ventajas | Retos |
| :--- | :--- | :--- | :--- |
| **API Tiempo Real** | Validar al radicar con **Vertex AI Endpoint**. Si prob. >80%, bota alerta. | Feedback inmediato, evita errores y reprocesos. | Pide alta disponibilidad y latencia <300ms. |
| **Webhooks (Eventos)** | Auditoria de fondo. Pub/Sub avisa a un worker de IA que revisa texto en segundo plano. | No bloquea la pantalla, absorbe picos de trafico. | Mas complejo de programar (colas/reintentos). |
| **Batch Nocturno** | Cierres masivos de madrugada en BigQuery y reentreno en **Vertex AI**. | Super eficiente y barato para volumenes grandes. | Resultados llegan con horas o dias de retraso. |

> **RECOMENDACION:** Usar **API en Tiempo Real de Vertex AI** en el portal web para evitar errores al radicar, y **Webhooks asincronos** para el RAG y la auditoria profunda haci no ponemos lentos los sistemas core de la EPS.