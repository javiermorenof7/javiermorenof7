# Agente IA: Banca + E-commerce (RAG Híbrido)

> *"Los LLMs saben hablar, pero no saben cuánto dinero tienes en el banco. Este proyecto soluciona eso."*

Este repositorio contiene un **MVP (Producto Mínimo Viable)** de un asistente virtual inteligente diseñado para un escenario bancario/retail (inspirado en Davivienda).

A diferencia de un chatbot estándar, este agente tiene **"Contexto Híbrido"**: es capaz de razonar simultáneamente con datos no estructurados (catálogo de productos) y datos estructurados privados (saldo del cliente, historial de pedidos), evitando alucinaciones financieras.

## ¿Qué hace especial a este proyecto?

La mayoría de los RAGs (Retrieval-Augmented Generation) solo buscan texto en documentos PDF. Este agente va un paso más allá integrando **Lógica de Negocio Transaccional**:

1.  **Guardián Financiero:** Antes de recomendar una compra, el agente cruza el precio del producto (obtenido por búsqueda semántica) contra el `saldo_disponible` del usuario (obtenido de la DB transaccional).
2.  **Búsqueda Semántica (FAISS):** Puedes pedir "una compu para jugar" y el agente entenderá que buscas la *ASUS ROG*, sin necesidad de coincidencia exacta de palabras.
3.  **astreo Inteligente:** Conecta con el historial de pedidos para responder preguntas de post-venta ("¿Dónde está mi mouse?") sin inventar datos.

## 🛠️ Stack Tecnológico

He construido esto manteniendo las dependencias ligeras pero potentes:

* **Orquestación:** [LangChain](https://python.langchain.com/) (Core LCEL).
* **Cerebro (LLM):** OpenAI GPT-3.5 Turbo.
* **Memoria Vectorial:** FAISS (Facebook AI Similarity Search) para el catálogo de productos.
* **Datos:** Pandas & Python Dicts (simulando una SQL Database).

## Escenarios de Prueba (Demos incluidos)

El notebook ejecuta automáticamente 3 casos de uso que demuestran la flexibilidad del agente:

| Escenario | Descripción | Lo que pasa "bajo el capó" |
| :--- | :--- | :--- |
| **1. Post-Venta** | *"¿Qué pasó con mi mouse?"* | El agente ignora el catálogo y hace una query directa al historial de pedidos del `user123`. |
| **2. Validación de Crédito** | *"Quiero la Mac, ¿me alcanza?"* | Recupera el precio ($5.2M), mira el saldo ($5.0M) y **deniega la compra** amablemente, sugiriendo financiación. |
| **3. Venta Cruzada** | *"Busco monitor para trabajo"* | Encuentra el monitor Samsung y sugiere el Mouse Logitech como complemento lógico. |

## 🛠️ Cómo correrlo localmente

1.  **Clona el repositorio**
    Descarga el proyecto o clona el repositorio en tu máquina local:
    ```bash
    git clone [https://github.com/tu-usuario/davivienda-agent-test.git](https://github.com/tu-usuario/davivienda-agent-test.git)
    cd davivienda-agent-test
    ```

2.  **Instala las dependencias**
    Asegúrate de tener Python 3.10+ instalado. Ejecuta el archivo de requerimientos:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configura la API Key**
    Abre el archivo `Davivienda_Ecommerce_Bot.ipynb` (o el script `.py`) y busca la celda de configuración.
    
    > **Nota para el Evaluador:** He dejado mi API Key configurada  (unicamente en el archivo ZIP)
    
    ```python
    import os
    # # OJO: no se adjunta la Key la key de seja en el archivo que se adjunta a la prueba
    os.environ["OPENAI_API_KEY"] = "sk-(TU-API-KEY)"
    ```

4.  **Ejecuta el Agente**
    * Si usas **Jupyter/Colab**: Corre las celdas en orden ("Run All").
    * Si usas **Terminal**: Ejecuta `python main.py`.
    
    El script inicializará la base de datos simulada (Usuarios/Pedidos), indexará los vectores de productos y ejecutará los escenarios de prueba automáticamente.

## Estructura del Código

* `MockDatabase`: Una clase que simula tu Core Bancario y ERP. Aquí viven los usuarios, saldos y el stock.
* `DaviviendaAgent`: La clase principal.
    * `_build_vector_store()`: Convierte descripciones de texto en vectores matemáticos.
    * `responder()`: El pipeline principal que inyecta los datos en el Prompt del LLM.

## Próximos Pasos (Roadmap)

Si quisiera llevar esto a producción, esto es lo que falta:

- [ ] Reemplazar la `MockDatabase` por conexiones reales a SQL/API Rest.
- [ ] Agregar memoria conversacional (para que recuerde lo que dijimos hace 2 mensajes).
- [ ] Implementar *Tools* de LangChain para que el agente pueda ejecutar la compra real (POST request), no solo decir que puede hacerlo.

---
*Hecho con ❤️ y Python.*