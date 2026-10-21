"""Lleva Online Retail II de bronce a plata y oro.

Plata: una línea de venta o devolución por fila, con nombres de columna claros y las líneas que
no son ventas de producto apartadas con su motivo. Oro: ventas mensuales, por país, top de
productos y el maestro de productos.

Uso (después de ingesta_ventas.py): python area_ventas/procesamiento/capas_ventas.py
"""
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).resolve().parents[1] / "data"
BRONCE, PLATA, ORO = DATOS / "raw", DATOS / "plata", DATOS / "oro"
COLUMNAS = {
    "Invoice": "numero_factura", "StockCode": "codigo_producto", "Description": "descripcion_producto",
    "Quantity": "cantidad", "InvoiceDate": "fecha_factura", "Price": "precio_unitario",
    "Customer ID": "id_cliente", "Country": "pais", "hoja": "hoja_origen",
}
# Los productos tienen 5 dígitos y a veces una letra de variante (85123A); lo demás son cargos
# y ajustes: POST (envío), M (manual), D (descuento), BANK CHARGES, AMAZONFEE...
PRODUCTO = r"\d{5}[A-Za-z]*"


def plata():
    b = pd.read_csv(BRONCE / "online_retail_ii.csv", dtype=str).rename(columns=COLUMNAS)
    filas_bronce = len(b)
    b["cantidad"] = b["cantidad"].astype(int)
    b["precio_unitario"] = b["precio_unitario"].astype(float)
    b["fecha_factura"] = pd.to_datetime(b["fecha_factura"])
    b["id_cliente"] = b["id_cliente"].str.removesuffix(".0")

    # Las reglas se aplican en orden: cada fila queda con el primer motivo que cumple
    b["motivo_rechazo"] = None
    reglas = [
        # La hoja 2009-2010 repite del 1 al 9 de diciembre de 2010, que ya está en la hoja siguiente
        ((b["hoja_origen"] == "Year 2009-2010") & (b["fecha_factura"] >= "2010-12-01"),
         "repetida en las dos hojas del libro"),
        (b.drop(columns="motivo_rechazo").duplicated(), "línea duplicada"),
        (~b["codigo_producto"].str.fullmatch(PRODUCTO), "cargo o ajuste, no es producto"),
        (b["precio_unitario"] <= 0, "precio en cero o negativo"),
    ]
    for condicion, motivo in reglas:
        b.loc[b["motivo_rechazo"].isna() & condicion, "motivo_rechazo"] = motivo

    rechazos = b[b["motivo_rechazo"].notna()]
    p = b[b["motivo_rechazo"].isna()].drop(columns="motivo_rechazo")
    p["tipo_movimiento"] = p["numero_factura"].str.startswith("C").map({True: "devolucion", False: "venta"})
    p["importe"] = (p["cantidad"] * p["precio_unitario"]).round(2)

    resumen = rechazos["motivo_rechazo"].value_counts()
    resumen["aceptada"] = len(p)
    assert resumen.sum() == filas_bronce, "las filas no cuadran entre bronce y plata"
    # Una devolución resta y una venta suma: el signo de la cantidad tiene que coincidir
    assert ((p["cantidad"] < 0) == (p["tipo_movimiento"] == "devolucion")).all()
    return p, rechazos, resumen.rename("filas")


def oro(p):
    p = p.assign(mes=p["fecha_factura"].dt.to_period("M").astype(str))
    ventas, devoluciones = p[p["tipo_movimiento"] == "venta"], p[p["tipo_movimiento"] == "devolucion"]

    mensual = pd.DataFrame({
        "ventas_brutas": ventas.groupby("mes")["importe"].sum(),
        "devoluciones": -devoluciones.groupby("mes")["importe"].sum(),
        "facturas": ventas.groupby("mes")["numero_factura"].nunique(),
        "clientes_identificados": ventas.groupby("mes")["id_cliente"].nunique(),
    }).fillna(0).reset_index()
    mensual["ventas_netas"] = mensual["ventas_brutas"] - mensual["devoluciones"]
    mensual["porcentaje_devolucion"] = 100 * mensual["devoluciones"] / mensual["ventas_brutas"]

    por_pais = (p.groupby("pais").agg(ventas_netas=("importe", "sum"),
                                     facturas=("numero_factura", "nunique"),
                                     clientes_identificados=("id_cliente", "nunique"))
                .sort_values("ventas_netas", ascending=False).reset_index())

    # Un código puede llegar con varias descripciones; el maestro se queda con la más usada
    productos = (p.groupby(["codigo_producto", "descripcion_producto"]).size().rename("lineas").reset_index()
                 .sort_values(["codigo_producto", "lineas"], ascending=[True, False])
                 .drop_duplicates("codigo_producto")[["codigo_producto", "descripcion_producto"]])
    top = (p.groupby("codigo_producto").agg(ventas_netas=("importe", "sum"), unidades=("cantidad", "sum"))
           .nlargest(20, "ventas_netas").reset_index().merge(productos, on="codigo_producto"))
    top = top[["codigo_producto", "descripcion_producto", "ventas_netas", "unidades"]]

    return {"ventas_mensuales": mensual.round(2), "ventas_por_pais": por_pais.round(2),
            "top_productos": top.round(2), "maestro_productos": productos}


if __name__ == "__main__":
    PLATA.mkdir(exist_ok=True)
    ORO.mkdir(exist_ok=True)
    p, rechazos, resumen = plata()
    p.to_csv(PLATA / "lineas_venta.csv", index=False)
    rechazos.to_csv(PLATA / "lineas_rechazadas.csv", index=False)
    resumen.rename_axis("resultado").to_csv(ORO / "resumen_capas.csv")
    for nombre, tabla in oro(p).items():
        tabla.to_csv(ORO / f"{nombre}.csv", index=False)
    print(resumen.to_string())
