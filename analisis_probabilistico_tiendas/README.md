# Análisis Probabilístico Tiendas
## Contexto
<p style="text-align: justify;">  
Para mejorar nuestras recomendaciones queremos saber a partir de una serie de características si un producto A es o no una buena recomendación para un producto B. Para ello tenemos un subconjunto de productos con la indicación de si a los usuarios les gusta como recomendación o no.
</p>

# Análisis y logros

### Comenzamos con el método científico

- ***Preguntas a responder a nuestro análisis***

  - Que podemos encontrar en los datos de la muestra propuesta en el ejercicio?
  - Como podemos saber que un producto es buena recomendación para otro?
  - Se proporciona una muestra de los datos, cuál es la mejor combinación y la que va a tener mejores resultados al exponerlo al cliente
  - Qué análisis, conclusiones encontramos sobre el tema?

- ***Obtener los datos a analizar***
  
  - Estos datos sé obtienen de la aplicación, los cuales requieren saber si un producto A es una buena recomendación para un producto B

  - ***Estos datos manejan los siguientes campos***:

    - product_id: id del producto para el cual se hizo la recomendación
    - recommended_product_id: id del producto recomendado
    - recommendation_index_order: posición en la pantalla en la que se mostró la recomendación
    - recommendation_approved_by_user: cantidad de usuarios que aprobaron la recomendación dentro de una orden
    - recommendation_done_by_rt: cantidad de veces que un Rappitendero recomendó este producto
    - recommendation_done_by_user: cantidad de veces que un usuario indicó este producto como similar
    - product_sales: cantidad de órdenes del producto para el cual se hizo la recomendación
    - recommended_product_sales: cantidad de órdenes del producto recomendado
    - product_category_path: clasificación del producto para el cual se hizo la recomendación (hay 3 niveles de categorías separadas por una barra / ) 
    - recommended_product_category_path: clasificación del producto recomendado (hay 3 niveles de categorías separadas por una barra / ) 
    - product_name: nombre del producto para el cual se hizo la recomendación
    - product_long_description: descripción del producto para el cual se hizo la recomendación
    - product_trademark: marca del producto para el cual se hizo la recomendación
    - product_maker: fabricante del producto para el cual se hizo la recomendación
    - product_last_price_sold: último precio de venta en moneda local (MX) del producto para el cual se hizo la recomendación
    - recommended_product_name: nombre del producto recomendado
    - recommended_product_long_description: descripción del producto recomendado
    - recommended_product_trademark: marca del producto recomendado
    - recommended_product_maker: fabricante del producto recomendado
    - recommended_product_last_price_sold: último precio de venta en moneda local (MX) del producto recomendado
    - user_liked(target): si al usuario le gusto o no la recomendación

- ***Exploración de los datos***   
  - Tipo de variables y tamaño de la muestra a analizar
   ![1](capturas/Captura%20de%20pantalla%202022-10-13%20145505.png)
  - Exploración de las columnas a manejar
   ![1](capturas/Captura%20de%20pantalla%202022-10-13%20145830.png)
  - Existen valores nulos o vacíos
  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20150016.png)
  En este caso es importante detectar esos valores Nulos o vacíos porque las variables que se analizan se pueden distorsionar bastante si se decide tomar el análisis partir de una variable que contenga muchos campos vacíos
  - Medidas de tendencia central
  - Descripción de las variables Categóricas (Más influyentes en el análisis)
  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20151631.png)
  Como se puede observar en este análisis no es lo mismo medir el ID que la variable nombre, ya que hay productos que pueden llegar a llamarse igual, pero no tiene el mismo ID, por esta razón es importante por esta razón se realizaran los análisis partir de los ID
  los cuales encontramos que en ***la categoría de producto ID (A) el TOP es Mágnum Paletas***
  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20151941.png)
  ***la categoría de producto Recomendado ID (B) el TOP es Sabritas-Cheetos Snack Flaming Hot***
  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20152150.png)
  - ### Descripción Categórica
    - De los 60430 registros contamos con 58853 registros con nombre.
    - Se cuenta con, 36067 Valores únicos de producto, los cuales se han recomendado 35015, es decir que por cada producto que se hace recomendación, se recomienda 1 producto aproximadamente
    - El producto para el cual se hacen más recomendaciones es ***Magnum Paleta Almendras***
    - el producto que se recomienda más con la venta de otro PRODUCT_ID es ***Sabritas-Cheetos Snack Flaming Hot***
    - el porcentaje de gusto de las recomendaciones dadas es positivo, este porcentaje se distribuye en 0,89 con Gusto positivo y un 0.11 que no gusta de la recomendación
  -  Distribución del gusto de los usuarios para todos los productos recomendados
  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20152429.png)

- ***Modelar los datos***
  - Distribución de los productos (A) por cada producto recomendado (B)
  ![1](capturas/Captura%20de%20pantalla%202022-10-12%20143500.png)

  Para poder saber la distribución de una variable es deseable verificar su comportamiento frente a otra categoría, como lo vamos a validar verificando los productos únicos sabiendo cuantas recomendaciones tiene cada uno, luego agruparlos

  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20153204.png)

  Normalmente, cuando la distribución no es normal, la moda, la media y la mediana no son simétricas; sin embargo, con el teorema de tendencia central, cuando más datos se capturen, todas las distribuciones tenderán a una normal

  http://195.134.76.37/applets/AppletCentralLimit/Appl_CentralLimit2.html

  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20153640.png)

  Como se observa, la mayoría de los productos que se compran solo se recomiendan una sola vez, productos que se recomiendan más de una vez comienzan a ser más raros.

  ####  ¿Teniendo esto como punto de partida podemos comenzar a realizar el clasificador, para poder responder la clasificación actual da las mejores combinaciones posibles?

   Realizamos la tabla de acuerdo a los productos recomendados (B), sabiendo cuál es él mejore producto que se pueden asociar a este o los mejores (A) (List)

  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20154907.png)

  ahora vamos a calcular la probabilidad de estas variables, teniendo en cuenta el producto (B)

  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20155210.png)

  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20155846.png)

  Con esto ya obtenemos la probabilidad. Ejemplo, la probabilidad de obtener una combinación que solo pueda tener más de 1 recomendación es de 0.91 (2 recomendaciones)

  Una vez obtenida esta probabilidad vamos a realizar ***el clasificador*** con las siguientes variables

  - Rango de los límites de la cantidad de los datos del 65% ***PROB[0.99,0.84]***
  - Si la categoría de la recomendación es igual a la categoría del producto recomendado
  - si al usuario le gusto o no la recomendación
  - Rangos de probabilidad

  Con esto podemos obtener la clasificación de las posibles combinaciones que puedan ser más aceptadas y recomendadas para un producto en específico

- ***Comunicar los resultados***
  - ***Que podemos encontrar en los datos de la muestra propuesta en el ejercicio?***
  
  Los que podemos observar es la gran variedad de combinaciones que existen con el clasificador que tenemos de acuerdo a las características que encontramos, que podemos anexarlo a la tabla final de acuerdo a sus características
  
    Si ya tenemos o queremos predecir buenas combinaciones, podemos utilizar la siguiente tabla:

  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20162109.png)
  
  La clasificación de toda la tabla Train es la siguiente
  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20165212.png)

  La mayoría de las recomendaciones son aceptables, pero estas podrían mejorar recomendando mejores productos, según la clasificación dada para cada uno

  - ***Como podemos saber que un producto es buena recomendación para otro?***
  
  La manera de saberlo es verificando su clasificación, por ejemplo vamos a analizar el producto top que verificamos anteriormente

  Es importante entender Que son dos puntos de vista distintos a analizar, uno es del producto recomendado (B) y del producto al cual se le hizo la recomendación (A)

  ***Producto TOP***

  ***Puntos de vista (B) producto recomendado***

  ***975228494 - Magnum Paleta Almendras***

  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20161518.png)

  En este caso observamos que no es buena recomendación combinar las paletas Mágnum con Helados Holanda Napolitano, pero si es una buena recomendación el de vainilla

  ***Producto TOP***

  ***Puntos de vista (A) al cual se le hizo la recomendación ***

  ***975228494 - Magnum Paleta Almendras***

  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20171920.png)

  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20172020.png)


  - Las combinaciones actuales está produciendo la mejor satisfacción al cliente?
  
  Para responder esta pregunta se va a realizar una muestra la cual tiene una proporción de la data que no tiene clasificación (test)

  Se toma la tabla de clasificación y se realiza un LEFT JOIN con la tabla test.

  Su distribución es:

  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20172217.png)

  La cual un ejemplo de las mejores combinaciones es la siguiente:

  ![1](capturas/Captura%20de%20pantalla%202022-10-13%20172245.png)

### Al archivo final se llama test_challengue_prob.csv