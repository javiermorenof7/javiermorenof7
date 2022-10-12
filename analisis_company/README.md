

# Introducción

<p style="text-align: justify;">  La empresa The Best Company dedicada a producir repuestos automovilísticos, conoce que la baja productividad de sus colaboradores está dada en gran medida por los ausentismos a las jornadas laborales. Para realizar un análisis de ello y comprobarlo, requiere del apoyo del Consultor en Analítica (usted), con el fin de establecer los principales patrones de comportamiento de los colaboradores, respecto a su cargo y áreas de trabajo, las horas contratadas y los ausentismos o incapacidades que puedan tener.</p>

# Data

- Colaboradores.xlsx: Cuenta con el listado de colaboradores de la compañía y algunos datos demográficos.

- Cargos.txt:   Tabla paramétrica con los cargos existentes en la compañía.

- Areas.csv:    Tabla paramétrica con las áreas (sedes) existentes en la compañía.

- Horas_Contratadas.csv: Tabla histórica con la información de horas contratadas para cada persona en su respectivo cargo y área (Periodo de tiempo de ene19 – jun20).

- Ausentismo_Incapacidades.xlsx:    Tabla histórica con la información de horas de ausentismo y horas de incapacidades, para cada persona (Periodo de tiempo de ene19 – jun20).


# Modelo dimensional

![Kitten](capturas/modelo%20dimencional.drawio.png)

# Modelo obtener la tabla de análisis

<p style="text-align: justify;"> Para poder obtener un análisis que pueda producir y responder las preguntas para entender los datos, es necesario llegar a una tabla que unifique directamente la base de datos relacional, la cual podemos obtener con el archivo company.ipynb (Este modelo también se puede importar a una base de datos)</p>

la tabla unificada o la tabla final es la siguiente:

![Kitten](capturas/Captura%20de%20pantalla%202022-10-12%20105846.png)

# Visualización

Una vez obtenida esta tabla podemos realizar los siguientes análisis

https://public.tableau.com/app/profile/francisco2414/viz/Company_16655277589250/Dashboard1

![Kitten](capturas/Captura%20de%20pantalla%202022-10-11%20230801.png)