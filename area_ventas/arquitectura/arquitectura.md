Explica qué herramientas y flujo propondrías para
automatizar la lectura de este Excel (u otros orígenes) hasta la visualización.
o Pregunta clave: ¿Cómo pasarías de un Excel local a una solución empresarial
escalable (Ej: Azure, AWS, GCP)?

La arquitectura propuesta la realizare en el entorno de GCP

la idea es hacerla escalable

Tenemos un excel AdventureWorks Sales, el cual se compone de la siguiente manera:

# Resumen de Composición: AdventureWorks Sales

Este conjunto de datos está estructurado como un **Esquema en Estrella (Star Schema)**, el diseño óptimo para análisis de datos y Business Intelligence (Power BI / Excel Power Pivot). Se compone de una tabla central de **Hechos** (métricas) rodeada por tablas de **Dimensiones** (contexto).

---

## 1. Tabla Central (Hechos)

### 📊 `Sales_data`
Es el núcleo del modelo. Registra cada transacción de venta con números analíticos y claves numéricas de enlace.

* **Claves de Conexión (FK):** `SalesOrderLineKey`, `ResellerKey`, `CustomerKey`, `ProductKey`, `OrderDateKey`, `DueDateKey`, `ShipDateKey`, `SalesTerritoryKey`.
* **Métricas Clave:**
    * `Order Quantity`: Cantidad de unidades.
    * `Unit Price`: Precio unitario.
    * `Sales Amount`: Ingreso neto real de la venta.
    * `Total Product Cost`: Costo total del producto para la empresa.

---

## 2. Tablas de Contexto (Dimensiones)

### 🏷️ `Product_data` (Catálogo)
Contiene la información de los productos vendidos.
* **Clave:** `ProductKey`
* **Atributos:** `SKU`, `Product` (Nombre), `Standard Cost`, `Color`, `List Price`, `Model`.
* **Jerarquía:** `Category` ➡️ `Subcategory`.

### 👥 `Customer_data` (Clientes B2C)
Información de personas naturales que compran directamente.
* **Clave:** `CustomerKey`
* **Atributos:** `Customer ID`, `Customer` (Nombre completo), `City`, `State-Province`, `Country-Region`, `Postal Code`.

### 🏢 `Reseller_data` (Distribuidores B2B)
Información de empresas o minoristas intermediarios.
* **Clave:** `ResellerKey`
* **Atributos:** `Reseller ID`, `Business Type`, `Reseller` (Nombre comercial), `City`, `State-Province`, `Country-Region`.

### 📦 `Sales Order_data` (Detalle del Pedido)
Define el origen y número de cada factura.
* **Clave:** `SalesOrderLineKey`
* **Atributos:** `Channel` (Canal: "Internet" o "Reseller"), `Sales Order` (ID Factura), `Sales Order Line` (Línea de factura).

### 🗺️ `Sales Territory_data` (Geografía)
Estructura comercial geográfica para agrupar ventas.
* **Clave:** `SalesTerritoryKey`
* **Atributos:** `Region`, `Country`, `Group` (Continente/Grupo).

### 📅 `Date_data` (Calendario)
Tabla maestra de tiempo para realizar inteligencia temporal (análisis YoY, mensual o trimestral).
* **Clave:** `DateKey` (Formato `AAAAMMDD`).
* **Atributos:** `Date`, `Fiscal Year`, `Fiscal Quarter`, `Month`, `MonthKey`.

---

## 3. ¿Cómo se relacionan? (Estructura de Enlaces)

```text
       ┌─────────────────┐       ┌─────────────────┐
       │  Customer_data  │       │  Product_data   │
       └────────┬────────┘       └────────┬────────┘
                │ (CustomerKey)           │ (ProductKey)
                └───────────┐   ┌─────────┘
                            ▼   ▼
                      ┌───────────┐
                      │Sales_data │ ◄── (SalesTerritoryKey) ── [Sales Territory_data]
                      └─────┬─────┘
                            ▲   ▲
                ┌───────────┘   └─────────┐
                │ (SalesOrderLineKey)     │ (OrderDateKey)
       ┌────────┴────────┐       ┌────────┴────────┐
       │Sales Order_data │       │    Date_data    │
       └─────────────────┘       └─────────────────┘
```

# Aplicacion arquitectura medallon

En base a a esta composicion, paremos por medio de un Python a uns estructura de CSV, esto para poder subirlo a un repositorio de GCP y poder crear la tablas

En un DWH, o DeltaLake, para hacer una estructura medallon, esta seria la estapa bronce donde la data esta cruda

# Propuesta de Arquitectura de Datos Escalable: Data Lakehouse

## 1. Visión General del Flujo
El objetivo de esta arquitectura es modernizar el procesamiento de datos, pasando de la manipulación manual de archivos locales (Excel) a un **Pipeline de Datos Automatizado y Escalable en la Nube**. 

Al desacoplar el almacenamiento del cómputo y aplicar el estándar de la industria, garantizamos alta disponibilidad, trazabilidad y un rendimiento óptimo para el consumo de analítica y Business Intelligence (BI).

---

## 2. Metodología Medallón (Data Lakehouse)
El flujo de datos se estructura en tres capas progresivas de calidad y refinamiento, asegurando que los analistas y modelos de negocio consuman información certificada.

### 🥉 Capa Bronce (Raw Data / Ingesta)
* **Origen:** Archivos CSV extraídos de fuentes locales o transaccionales.
* **Proceso:** Los archivos se cargan de forma automatizada hacia un **Cloud Storage** (Ej. Google Cloud Storage).
* **Propósito:** Actúa como el repositorio histórico inmutable. Los datos se almacenan exactamente en su formato original, sin alteraciones. Si ocurre algún error en las transformaciones posteriores, esta capa permite reprocesar la información sin depender de la fuente original.

### 🥈 Capa Plata (Cleansed Data / Procesamiento)
* **Proceso:** Un motor de procesamiento distribuido lee los datos de la capa Bronce y aplica limpieza y estandarización. 
* **Transformaciones:** * Manejo de valores nulos y eliminación de duplicados.
  * Estandarización de tipos de datos (fechas, monedas).
  * Conversión del formato CSV a formatos columnares altamente optimizados y comprimidos, como **Parquet** o **Delta** (creando la base del Delta Lake).
* **Propósito:** Establecer el modelo tabular (Hechos y Dimensiones) limpio y preparado para cruces de información técnica, fungiendo como la "única fuente de la verdad" a nivel transaccional.

### 🥇 Capa Oro (Business-Ready / DWH)
* **Proceso:** Los datos de la capa Plata se integran en un **Data Warehouse** (DWH) o se exponen mediante vistas materializadas.
* **Transformaciones:**
  * Aplicación de reglas de negocio complejas.
  * Agregaciones métricas (ej. Ventas totales por región, rentabilidad mensual).
  * Validaciones de calidad de datos (Data Quality) para asegurar que las cifras cuadren.
* **Propósito:** Entregar tablas listas para el consumo final. Las herramientas de visualización se conectan *únicamente* a esta capa, lo que garantiza tiempos de respuesta de milisegundos y consistencia en los reportes corporativos.

---

## 3. Stack Tecnológico Cloud Propuesto

Para implementar esta arquitectura de alto impacto, se proponen las siguientes herramientas nativas, destacando el ecosistema de GCP como referencia principal:

| Etapa del Pipeline | 🌐 Google Cloud (GCP) | ☁️ Amazon Web Services (AWS) | 🟦 Microsoft Azure |
| :--- | :--- | :--- | :--- |
| **Data Lake (Bronce)** | Cloud Storage (GCS) | Amazon S3 | Azure Data Lake Storage (ADLS) |
| **Procesamiento (Plata)** | Cloud Dataproc / Dataflow | AWS Glue / EMR | Azure Databricks / Synapse |
| **Data Warehouse (Oro)** | **BigQuery** | Amazon Redshift | Azure Synapse Analytics |
| **Orquestación** | Cloud Composer (Airflow) | MWAA (Airflow) | Azure Data Factory |
| **Visualización (BI)** | Looker / Power BI | QuickSight / Power BI | Power BI |

---

## 4. Beneficios y Escalabilidad Empresarial
1. **Escalabilidad Elástica:** La infraestructura Serverless (como BigQuery) permite procesar desde unos pocos Megabytes (un Excel) hasta múltiples Terabytes sin necesidad de reconfigurar servidores ni cambiar el código base.
2. **Gobernanza y Seguridad:** Al utilizar Cloud Storage y un DWH corporativo, se aplican políticas de acceso por roles (IAM), asegurando que solo el personal autorizado acceda a la información sensible.
3. **Eficiencia en BI:** Al trasladar toda la carga de procesamiento a la nube (Capas Plata y Oro), los tableros de visualización son extremadamente ligeros y rápidos, mejorando significativamente la experiencia del usuario final.