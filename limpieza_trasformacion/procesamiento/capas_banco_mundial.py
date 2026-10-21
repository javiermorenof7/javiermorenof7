"""Limpia el PIB per cápita del Banco Mundial: de un CSV ancho y desordenado a una tabla larga.

El archivo de origen trae una marca BOM, cuatro filas de encabezado antes de las columnas, una
columna vacía al final, un año por columna y las regiones mezcladas con los países. Plata: una
fila por país y año, solo países y solo valores informados. Oro: último valor por país y la serie
de Colombia frente a América Latina y el mundo.

Uso (después de ingesta_banco_mundial.py): python limpieza_trasformacion/procesamiento/capas_banco_mundial.py
"""
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).resolve().parents[1] / "data"
BRONCE, ORO = DATOS / "raw", DATOS / "oro"
REGIONES = {
    "East Asia & Pacific": "Asia oriental y el Pacífico", "Europe & Central Asia": "Europa y Asia central",
    "Latin America & Caribbean": "América Latina y el Caribe",
    "Middle East, North Africa, Afghanistan & Pakistan": "Oriente Medio, Norte de África, Afganistán y Pakistán",
    "North America": "América del Norte", "South Asia": "Asia meridional", "Sub-Saharan Africa": "África subsahariana",
}
SERIE = {"COL": "Colombia", "LCN": "América Latina y el Caribe", "WLD": "Mundo"}


def plata():
    ancho = pd.read_csv(BRONCE / "indicador.csv", skiprows=4, encoding="utf-8-sig")
    ancho = ancho.loc[:, ~ancho.columns.str.startswith("Unnamed")]
    meta = pd.read_csv(BRONCE / "metadatos_paises.csv", encoding="utf-8-sig",
                       usecols=["Country Code", "Region", "IncomeGroup"])

    largo = ancho.melt(id_vars=["Country Name", "Country Code", "Indicator Name", "Indicator Code"],
                       var_name="anio", value_name="pib_per_capita_usd")
    largo = largo.rename(columns={"Country Name": "nombre_pais", "Country Code": "codigo_pais"})
    largo["anio"] = largo["anio"].astype(int)
    largo = largo.merge(meta.rename(columns={"Country Code": "codigo_pais", "Region": "region",
                                             "IncomeGroup": "grupo_ingreso"}), on="codigo_pais", how="left")
    largo["region"] = largo["region"].map(REGIONES)

    # Las filas sin región son agregados (Mundo, América Latina, "ingreso alto"...), no países
    es_pais = largo["region"].notna()
    con_valor = largo["pib_per_capita_usd"].notna()
    resumen = pd.Series({
        "celdas del archivo ancho": len(largo),
        "agregado regional o por ingreso, no es país": int((~es_pais).sum()),
        "país sin valor en el año": int((es_pais & ~con_valor).sum()),
        "aceptada": int((es_pais & con_valor).sum()),
    }, name="filas")
    assert resumen.iloc[1:].sum() == resumen.iloc[0], "las celdas no cuadran"
    columnas = ["codigo_pais", "nombre_pais", "region", "grupo_ingreso", "anio", "pib_per_capita_usd"]
    return largo.loc[es_pais & con_valor, columnas], largo.loc[~es_pais & con_valor], resumen


def oro(paises, agregados):
    ultimo = (paises.sort_values("anio").groupby("codigo_pais").tail(1)
              .sort_values("pib_per_capita_usd", ascending=False).reset_index(drop=True))
    todo = pd.concat([paises, agregados])
    serie = (todo[todo["codigo_pais"].isin(SERIE)].assign(nombre=lambda d: d["codigo_pais"].map(SERIE))
             .pivot(index="anio", columns="nombre", values="pib_per_capita_usd").reset_index())
    serie["colombia_frente_a_america_latina_pct"] = 100 * serie["Colombia"] / serie["América Latina y el Caribe"]
    return {"ultimo_valor_por_pais": ultimo.round(2), "colombia_america_latina_mundo": serie.round(2)}


if __name__ == "__main__":
    ORO.mkdir(exist_ok=True)
    paises, agregados, resumen = plata()
    assert not paises.duplicated(["codigo_pais", "anio"]).any() and (paises["pib_per_capita_usd"] > 0).all()
    paises.round(2).to_csv(ORO / "pib_per_capita_paises.csv", index=False)
    resumen.rename_axis("resultado").to_csv(ORO / "resumen_capas.csv")
    for nombre, tabla in oro(paises, agregados).items():
        tabla.to_csv(ORO / f"{nombre}.csv", index=False)
    print(resumen.to_string())
