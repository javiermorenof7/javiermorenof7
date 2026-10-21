"""¿Es el producto A una buena recomendación para el producto B? Respuesta con canastas reales.

Usa las facturas de venta de Online Retail II que deja la capa plata de area_ventas
(correr antes area_ventas/procesamiento/ingesta_ventas.py y capas_ventas.py).

Para cada par A -> B calcula el soporte, la confianza P(B|A) y el lift. Un par es buena
recomendación si, con el 95 % de confianza (límite inferior del intervalo de Wilson), al menos
1 de cada 5 compradores de A también compra B, y si comprar A al menos duplica la probabilidad
de comprar B (lift de 2 o más).

Uso: python analisis_probabilistico_tiendas/reglas_asociacion.py
"""
from math import sqrt
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PLATA_VENTAS = RAIZ / "area_ventas" / "data" / "plata" / "lineas_venta.csv"
ORO = Path(__file__).resolve().parent / "data" / "oro"
SOPORTE_MINIMO = 0.01  # el producto aparece en al menos el 1 % de las facturas
CONFIANZA_MINIMA = 0.20
LIFT_MINIMO = 2
Z = 1.96


def limite_inferior_wilson(exitos, total):
    p = exitos / total
    centro = p + Z**2 / (2 * total)
    margen = Z * sqrt(p * (1 - p) / total + Z**2 / (4 * total**2))
    return (centro - margen) / (1 + Z**2 / total)


def canastas():
    lineas = pd.read_csv(PLATA_VENTAS, dtype=str, usecols=["numero_factura", "codigo_producto",
                                                            "descripcion_producto", "tipo_movimiento"])
    ventas = lineas[lineas["tipo_movimiento"] == "venta"]
    nombres = (ventas.groupby(["codigo_producto", "descripcion_producto"]).size().rename("n").reset_index()
               .sort_values("n", ascending=False).drop_duplicates("codigo_producto")
               .set_index("codigo_producto")["descripcion_producto"])
    return ventas[["numero_factura", "codigo_producto"]].drop_duplicates(), nombres


def reglas(items):
    facturas = items["numero_factura"].nunique()
    frecuencia = items["codigo_producto"].value_counts()
    frecuentes = frecuencia[frecuencia / facturas >= SOPORTE_MINIMO].index
    items = items[items["codigo_producto"].isin(frecuentes)]

    pares = items.merge(items, on="numero_factura", suffixes=("_a", "_b"))
    pares = pares[pares["codigo_producto_a"] != pares["codigo_producto_b"]]
    r = pares.groupby(["codigo_producto_a", "codigo_producto_b"]).size().rename("facturas_ab").reset_index()
    r["facturas_a"] = r["codigo_producto_a"].map(frecuencia)
    r["probabilidad_base_b"] = r["codigo_producto_b"].map(frecuencia) / facturas
    r["soporte"] = r["facturas_ab"] / facturas
    r["confianza"] = r["facturas_ab"] / r["facturas_a"]
    r["lift"] = r["confianza"] / r["probabilidad_base_b"]
    r["confianza_minima_95"] = [limite_inferior_wilson(x, n) for x, n in zip(r["facturas_ab"], r["facturas_a"])]
    r["buena_recomendacion"] = (r["confianza_minima_95"] >= CONFIANZA_MINIMA) & (r["lift"] >= LIFT_MINIMO)
    return r, facturas, len(frecuentes)


if __name__ == "__main__":
    ORO.mkdir(parents=True, exist_ok=True)
    items, nombres = canastas()
    r, facturas, productos = reglas(items)
    assert r["confianza"].between(0, 1).all() and (r["confianza_minima_95"] <= r["confianza"]).all()

    top = r[r["buena_recomendacion"]].nlargest(30, "lift").copy()
    top.insert(1, "descripcion_a", top["codigo_producto_a"].map(nombres))
    top.insert(3, "descripcion_b", top["codigo_producto_b"].map(nombres))
    top.round(4).to_csv(ORO / "mejores_recomendaciones.csv", index=False)
    resumen = pd.Series({"facturas": facturas, "productos_frecuentes": productos, "pares_evaluados": len(r),
                         "pares_buena_recomendacion": int(r["buena_recomendacion"].sum())}, name="valor")
    resumen.rename_axis("indicador").to_csv(ORO / "resumen.csv")
    print(resumen.to_string())
