*Prueba ejecucion 1:*

Se observa que el ETL comienza a detectar errores

![Descripción de la imagen](img/Ejecucion%20Falla%20Pipeline%20GCP.png)

*Prueba ejecucion 2:*

Se observa que el ETL detecta cuando la ruta del python no esta correcta, ademas que se visuliza que las ejecucion corrieron correctamente

![Descripción de la imagen](img/ejecucion%20pepiline%20prueba%202.png)

*Prueba ejecucion 3:*

Una vez detectado el error se corrije y se valida nuevamente la ETL, la cual se procede a correr, validando que todo ejecuto correctamente, se puede tambien vizuzalizar los errores anteriores en el historial de trabajo en GCP Bigquery

![Descripción de la imagen](img/Ejecucion%20Final%20ETL.png)
 
> 💡 **Nota:** La consola imprimirá un log en tiempo real confirmando la creación de las tablas capa por capa (`Raw ➔ Staging ➔ Analytics`).

# Estructura proyecto GCP

Una vez se ejecuta obtenemos las siguiente estructura de tablas, teniendo en cuenta que cuando se ejcuta no se duplicara la data

![Descripción de la imagen](img/Estructura%20Proyecto%20GCP.png)

# Tablero Loker estudio

Una vez ejeuctado el proceso obtenemos la data en el tablero

![Descripción de la imagen](img/Tablero%20Data%20Loker%20BI.png)
