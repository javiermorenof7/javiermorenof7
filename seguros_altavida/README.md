# Presentación

## Transformación - Proceso de manejo de Datos e IA
![Descripción de la imagen](/seguros_altavida/capturas/IA_y_transformación_en_seguros.png)

## Arquitectura en la Nube con GCP
![Descripción de la imagen](/seguros_altavida/capturas/Arquitectura_IA_para_Sector_Salud.png)

# Seguros Altavida

Seguros Altavida es una compañía de seguros que administra el aseguramiento en salud de sus
afiliados. El área de Transformación Operacional analiza las autorizaciones de prestaciones
(procedimientos y medicamentos) para apoyar la toma de decisiones sobre cobertura, costo y
calidad de la operación. La compañía quiere escalar sus iniciativas de analítica e inteligencia
artificial: pasar de soluciones puntuales a soluciones robustas, seguras y escalables, integradas con
sus sistemas core y desplegadas en la n ube empresarial. Esta prueba evalúa su profundidad técnica
en procesamiento de datos, machine learning e IA, y —de forma central — su capacidad para diseñar
arquitecturas de IA escalables, integraciones y puesta en producción (MLOps).

# Arquitectura y Modelado de IA: Autorizaciones Médicas (EPS)

Este documento detalla las decisiones técnicas, metodológicas y de arquitectura para la implementación de soluciones de Inteligencia Artificial (ML, NLP y GenAI) sobre la nube de Google Cloud Platform (GCP)(Esta fue Opcional para manejar este caso de uso), integradas al flujo operativo y core de autorizaciones médicas.

---
## Parte A – Procesamiento e Ingeniería de Datos en Python

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

---

## Parte C: Modelado de IA (ML, NLP y GenAI)

### 1. Modelo Predictivo para Evitar Anulaciones ("Semáforo Preventivo")
* **Objetivo:** Evaluar solicitudes al radicar para detectar errores formales o probabilidad de rechazo antes de ir a auditoría.
* **Variable Objetivo:** Binaria (Sí/No: ¿Se anula o devuelve en los primeros días?).
* **Variables Clave:** Historial de errores de la clínica/médico, código del procedimiento, diagnóstico, copagos pendientes y tipo de plan.
* **Partición de Datos:** Estrictamente **por tiempo (pasado vs. futuro)**. Entrenar con los primeros 10 meses y validar con el mes 11 y 12.
* **Métrica ante Desbalance (85% bien / 15% rechazo):** **PR-AUC** y **F1-Score** para enfocar la puntería en detectar el 15% problemático sin saturar de falsas alarmas.
* **Prevención de Errores:** 
  * *Fuga de datos:* Ocultar al modelo variables futuras (ej. nombre del auditor o motivo final de rechazo).
  * *Sobreajuste:* Usar detención temprana (*Early Stopping*) para que no memorice los datos de prueba.

### 2. Lectura Inteligente de Notas Clínicas (NLP)
* **Objetivo:** Leer párrafos libres del médico para categorizar la urgencia y extraer medicamentos y dosis sin intervención humana.
* **Técnicas:**
  * **Embeddings:** Matemáticas para que la IA entienda sinónimos médicos (ej. "cefalea" = "dolor de cabeza").
  * **Zero-Shot (Gemini 1.5):** Para **arranque inmediato (Día 1)**. Clasifica y extrae con instrucciones en el prompt sin entrenamiento previo.
  * **Fine-Tuning:** Para **fase 2**. Entrenar un modelo propio pequeño con miles de casos acumulados para que sea ultra rápido y de costo muy bajo.
* **Evaluación:** **Macro F1** para precisión en categorías clínicas y **Exact Match** para verificar que extraiga medicamentos y dosis palabra por palabra.

### 3. Asistente con RAG para Coberturas de Salud
* **Objetivo:** Chatbot para auditores y usuarios que responde si un procedimiento está cubierto leyendo contratos y manuales en PDF.
* **Flujo del RAG:**
  1. **Chunking:** Cortar PDFs en párrafos con sentido completo (cláusulas/artículos).
  2. **Búsqueda:** Encontrar en milisegundos los 4 párrafos exactos que responden la pregunta del usuario.
  3. **Generación:** El LLM redacta la respuesta usando **únicamente** esos 4 párrafos.
* **Control de Alucinaciones ("Cero Inventos"):**
  * Regla estricta: Si el dato no está en el texto recuperado, responde *"Información no disponible"* y remite a un humano.
  * Obligación de incluir la cita exacta al final (ej. *Póliza Oro, Pág. 14, Art. 3*).
* **Evaluación:** Estándar **RAGAS** para medir utilidad de búsqueda, fidelidad al texto real y relevancia de la respuesta.

---

## Parte D: Arquitectura de Solución en Google Cloud Platform (GCP)

### 1. Mapa de Servicios y Componentes GCP

| Capa de Arquitectura | Servicio en GCP | Función Práctica |
| :--- | :--- | :--- |
| **Ingesta** | **Pub/Sub** y **Dataflow** | Recibe solicitudes en vivo (uno a uno) y cargas masivas nocturnas de clínicas. |
| **Almacenamiento** | **Cloud Storage** y **BigQuery** | Guarda archivos brutos (PDFs, audios) y actúa como la gran bodega central de datos. |
| **Procesamiento** | **BigQuery + Dataproc** y **Feature Store** | Limpia información, calcula estadísticas y sirve variables al modelo en milisegundos. |
| **Inteligencia (IA)** | **Vertex AI Platform** y **Vector Search** | Entrena y sirve los modelos predictivos; funciona como buscador veloz para el RAG. |
| **Salida / API** | **Apigee** y **Cloud Run** | Controla seguridad, acceso de usuarios y corre las aplicaciones web de forma auto-escalable. |

### 2. Escalabilidad, Rendimiento y Costos
* **Escalabilidad Serverless:** Crece automáticamente con picos masivos de trámites los lunes y baja a cero en la madrugada para pagar solo por segundo usado.
* **Tiempo Real vs. Lotes:** Semáforo predictivo y chatbot operan en **tiempo real (< 500 ms)**. La actualización de pólizas y cálculo de métricas opera por **lotes en la noche**.
* **Ahorro de Costos:** 
  * Uso de máquinas con descuento (**Spot VMs**, -70% costo) para tareas pesadas nocturnas.
  * Implementar **Caché** para que dudas repetidas se respondan desde la memoria sin pagar al LLM cada vez.
  * Mover historiales viejos (> 1 año) a almacenamiento frío económico (**Cloud Storage Coldline**).

### 3. Seguridad y Gobierno Médico (Habeas Data / HIPAA)
* **Anonimización Automática:** **Cloud DLP** borra o enmascara nombres, cédulas y teléfonos en notas clínicas *antes* de que la IA las lea.
* **Control Estricto y Cifrado:** Cifrado total de datos (**Cloud KMS**) y permisos por rol/zona (**IAM + Row-Level Security**) para que un auditor solo vea pacientes de su clínica asignada.
* **Trazabilidad:** Bitácora inmutable (**Cloud Audit Logs**) que registra quién, cuándo y desde dónde se accedió a cada dato médico.

### 4. Justificación y Alternativa Descartada
* **Por qué RAG:** Porque las pólizas y copagos cambian todo el tiempo; actualizar un PDF en el buscador toma 5 segundos.
* **Alternativa Descartada:** Entrenar todo el conocimiento médico dentro de un modelo gigante propio (*Fine-Tuning de LLM*).
* **Motivo del rechazo:** Tarda días, cuesta miles de dólares por cada actualización normativa y genera un alto riesgo de mezclar reglas viejas con nuevas.

### 5. Integración Práctica (Sin frenar por el Backlog de TI)
* **El Problema:** El equipo de TI central (Core) tiene filas de trabajo largas y los sistemas hospitalarios son delicados.
* **Solución Basada en Eventos:** En lugar de pedir al TI central que reescriba su sistema para conectar APIs síncronas, conectamos una **lectura pasiva silenciosa (Change Data Capture / Pub-Sub)**.
* **Resultado:** Cada trámite que entra al hospital se copia a GCP sin afectar el rendimiento central. La IA analiza en un carril paralelo y muestra las alertas en pantallas secundarias, logrando un despliegue en semanas sin tocar el código central.

---

## Bonus: Transferencia Técnica a los Analistas

1. **De Excel a Alto Rendimiento:** Migrar al equipo al uso de **Polars o PySpark en GCP** para procesar millones de datos en segundos.
2. **Revisión en Pareja (Peer Review):** Implementar **Git** para versionar código y prohibir subir modelos a producción sin revisión de un compañero.
3. **Pruebas de Calidad Automáticas:** Scripts automáticos (**CI/CD**) que bloquean datos vacíos o erróneos antes de alimentar los modelos.
4. **Monitoreo de Salud de la IA (MLOps):** Capacitar en la lectura de alertas de **Vertex AI Model Monitoring** para saber cuándo la realidad clínica cambió y se debe reentrenar el modelo.