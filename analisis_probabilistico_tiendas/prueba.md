# Intro
Uno de los principales diferenciales de Rappi respecto a sus competidores es la vertical de Mercados (CPG). Ésta permite a nuestros consumidores realizar las típicas compras de supermercados, farmacias y licorerías de manera online con la posibilidad de programar cuándo desean recibir su pedido.
Para el éxito de esta vertical Rappi se asocia con tiendas y ofrece sus productos en la aplicación. 
Para cada producto que se vende a través de la app se ofrecen recomendaciones de productos similares con el objetivo de facilitar la navegación y ayudar al usuario a encontrar lo que busca.

# El problema
Para mejorar nuestras recomendaciones queremos saber a partir de una serie de características si un producto A es o no una buena recomendación para un producto B.
Para ello tenemos un subconjunto de productos con la indicación de si a los usuarios les gusta como recomendación o no.

Te proveemos dos dataset, train_data.csv con todas las características de productos, recomendaciones y la indicación del usuario (user_liked) y test_challengue.csv sólo con las características del producto. 

Características:
- product_id: id del producto para el cual se hizo la recomendación

-	recommended_product_id: id del producto recomendado
-	recommendation_index_order: posición en la pantalla en la que se mostró la recomendación
-	recommendation_approved_by_user: cantidad de usuarios que aprobaron la recomendación dentro de una orden
-	recommendation_done_by_rt: cantidad de veces que un Rappitendero recomendó este producto
-	recommendation_done_by_user: cantidad de veces que un usuario indicó este producto como similar
-	product_sales: cantidad de órdenes del producto para el cual se hizo la recomendación
-	recommended_product_sales: cantidad de órdenes del producto recomendado
-	product_category_path: clasificación del producto para el cual se hizo la recomendación (hay 3 niveles de categorías separadas por una barra / ) 
-	recommended_product_category_path: clasificación del producto recomendado (hay 3 niveles de categorías separadas por una barra / ) 
-	product_name: nombre del producto para el cual se hizo la recomendación
-	product_long_description: descripción del producto para el cual se hizo la recomendación
-	product_trademark: marca del producto para el cual se hizo la recomendación
-	product_maker: fabricante del producto para el cual se hizo la recomendación
-	product_last_price_sold: último precio de venta en moneda local (MX) del producto para el cual se hizo la recomendación
-	recommended_product_name: nombre del producto recomendado
-	recommended_product_long_description: descripción del producto recomendado
-	recommended_product_trademark: marca del producto recomendado
-	recommended_product_maker: fabricante del producto recomendado
-	recommended_product_last_price_sold: último precio de venta en moneda local (MX) del producto recomendado
-	user_liked(target): si al usuario le gusto o no la recomendación

# Consigna
-	Análisis descriptivos
-	Armar un clasificador que indique si un producto es una buena recomendación similar para otro.
-	Predecir para test_challengue.csv
-	Medir (todo lo que consideres relevante)
-	Conclusiones

Output esperado: 
-	Jupyter notebook con el análisis, las hipótesis, el modelo, etc.
-	Archivo csv con predicciones para el archivo test_challengue.csv

¡Éxitos! 

