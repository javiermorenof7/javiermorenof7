# Agente de banca y e-commerce

Prototipo de asistente para un escenario de banca y comercio electrónico. Responde preguntas del cliente combinando dos fuentes: el catálogo de productos, consultado por búsqueda semántica, y los datos del propio cliente (saldo de la tarjeta e historial de pedidos).

Los datos son ficticios: dos clientes y un catálogo pequeño definidos en el notebook.

## Cómo funciona

1. **Catálogo:** las descripciones de los productos se convierten en vectores con `OpenAIEmbeddings` y se indexan en FAISS. Así, "una compu para jugar" encuentra el portátil gamer sin coincidencia exacta de palabras.
2. **Datos del cliente:** `MockDatabase` simula el core bancario y el ERP (clientes, saldos y pedidos). Para cada pregunta se toman el saldo y los pedidos del cliente.
3. **Respuesta:** los productos encontrados y los datos del cliente se pasan al modelo (`gpt-3.5-turbo`, temperatura 0) con LangChain, junto con la instrucción de comparar el precio con el saldo antes de recomendar una compra.

## Escenarios de prueba

El notebook ejecuta tres casos:

| Escenario | Pregunta | Qué se espera |
| --- | --- | --- |
| Posventa | "¿Qué ha pasado con el mouse que compré?" | Responde con el estado del pedido del cliente. |
| Validación de saldo | "Quiero comprar el MacBook Air, ¿me alcanza el cupo de mi tarjeta?" | El precio ($5,2 M) supera el saldo ($5,0 M): no recomienda la compra y sugiere financiación. |
| Venta cruzada | "Busco un monitor bueno para trabajar, ¿qué me recomiendas?" | Encuentra el monitor y sugiere el mouse como complemento (campo `sugeridos` del catálogo). |

## Límites

- **La validación del saldo la hace el modelo, no el código:** el precio y el saldo van en el prompt y el modelo los compara, así que no es una regla garantizada; en producción la comparación debería hacerse en código antes de llamar al modelo.
- **Sin memoria de conversación:** cada pregunta se responde por separado.
- **Sin acciones:** el agente recomienda, pero no ejecuta compras ni consulta sistemas reales.
- **Datos en memoria:** el catálogo y los clientes viven en el notebook; no hay base de datos ni API.
- **Sin evaluación sistemática:** solo se comprueban los tres escenarios.

## Cómo ejecutarlo

1. Instalar las dependencias (Python 3.10+): `pip install -r requirements.txt`.
2. Poner una clave propia de OpenAI en `OPENAI_API_KEY`, en la primera celda del notebook.
3. Abrir `ecomerce.ipynb` y ejecutar todas las celdas: crea los datos, indexa el catálogo y corre los escenarios.

## Tecnologías

Python, LangChain, OpenAI (`gpt-3.5-turbo` y embeddings), FAISS y Pandas.
