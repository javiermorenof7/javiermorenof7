"""Lleva el informe semanal de tasas de la Superintendencia Financiera de bronce a plata y oro.

Plata: nombres de columna claros, texto con la codificación corregida, una fila por llave y
filas que no sirven para promediar apartadas con su motivo. Oro: tasas mensuales ponderadas por
monto y margen de intermediación (tasa de crédito menos tasa de ahorro).

Uso (después de ingesta_tasas.py): python riesgo_credito/procesamiento/capas_tasas.py
"""
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).resolve().parents[1] / "data"
BRONCE, PLATA, ORO = DATOS / "raw", DATOS / "plata", DATOS / "oro"
LLAVE = ["fecha_corte", "codigo_tipo_entidad", "codigo_entidad", "codigo_unidad_captura", "codigo_subcuenta"]
AHORRO = "DEPOSITOS Y CUENTAS DE AHORRO"

COLUMNAS = {
    "fechacorte": "fecha_corte", "tipoentidad": "codigo_tipo_entidad", "codigoentidad": "codigo_entidad",
    "nombreentidad": "nombre_entidad", "unidad_de_captura": "codigo_unidad_captura",
    "nombre": "nombre_modalidad", "tipo": "nombre_tipo_credito", "subcuenta": "codigo_subcuenta",
    "nombre_sub": "nombre_subcuenta", "tasaefectivaanual": "tasa_efectiva_anual",
    "montos": "monto_desembolsado", "num_creditos_desembolsados": "numero_creditos",
}
TIPOS_ENTIDAD = {"1": "Establecimiento bancario", "4": "Compañía de financiamiento",
                 "22": "Institución oficial especial", "32": "Cooperativa financiera"}


def reparar(texto):
    """'ADQUISICIÃ“N' es UTF-8 leído como Windows-1252; se devuelve a 'ADQUISICIÓN'."""
    if not isinstance(texto, str) or "Ã" not in texto:
        return texto
    return texto.encode("cp1252").decode("utf-8")


def plata():
    b = pd.read_csv(BRONCE / "tasas_activas_semanal.csv", dtype=str).rename(columns=COLUMNAS)
    filas_bronce = len(b)
    for c in ("nombre_modalidad", "nombre_tipo_credito", "nombre_subcuenta"):
        b[c] = b[c].map(reparar)
    b["fecha_corte"] = pd.to_datetime(b["fecha_corte"]).dt.date
    b["nombre_tipo_entidad"] = b["codigo_tipo_entidad"].map(TIPOS_ENTIDAD)
    for c in ("tasa_efectiva_anual", "monto_desembolsado", "numero_creditos"):
        b[c] = pd.to_numeric(b[c])
    # Antes de 2011 la fuente no reporta el número de créditos y lo deja en 0: es un dato faltante
    b.loc[b["numero_creditos"] == 0, "numero_creditos"] = pd.NA

    # La misma entidad aparece con dos nombres en la misma semana ("Banco De Bogota" y "... S.A.")
    duplicadas = b.duplicated(LLAVE)
    b = b[~duplicadas]

    b["motivo_rechazo"] = None
    b.loc[b["monto_desembolsado"] <= 0, "motivo_rechazo"] = "sin monto desembolsado"
    b.loc[b["tasa_efectiva_anual"] <= 0, "motivo_rechazo"] = "tasa en cero"
    rechazos = b[b["motivo_rechazo"].notna()]
    aceptadas = b[b["motivo_rechazo"].isna()].drop(columns="motivo_rechazo")

    resumen = rechazos["motivo_rechazo"].value_counts()
    resumen["duplicada por cambio de nombre de la entidad"] = int(duplicadas.sum())
    resumen["aceptada"] = len(aceptadas)
    assert resumen.sum() == filas_bronce, "las filas no cuadran entre bronce y plata"
    return aceptadas, rechazos, resumen.rename("filas")


def ponderada(g):
    return (g["tasa_efectiva_anual"] * g["monto_desembolsado"]).sum() / g["monto_desembolsado"].sum()


def oro(p):
    p = p.assign(mes=pd.to_datetime(p["fecha_corte"]).dt.to_period("M").astype(str))
    credito, ahorro = p[p["nombre_modalidad"] != AHORRO], p[p["nombre_modalidad"] == AHORRO]

    por_modalidad = (credito.groupby(["mes", "nombre_modalidad"])
                     .apply(lambda g: pd.Series({"tasa_ponderada": ponderada(g),
                                                 "monto_desembolsado": g["monto_desembolsado"].sum()}))
                     .reset_index())
    margen = pd.DataFrame({
        "tasa_credito": credito.groupby("mes").apply(ponderada),
        "tasa_ahorro": ahorro.groupby("mes").apply(ponderada),
    }).dropna().reset_index()
    margen["margen_intermediacion"] = margen["tasa_credito"] - margen["tasa_ahorro"]
    por_tipo_entidad = (credito.assign(anio=credito["mes"].str[:4])
                        .groupby(["anio", "nombre_tipo_entidad", "nombre_modalidad"])
                        .apply(ponderada).rename("tasa_ponderada").reset_index())
    redondeo = {"tasa_ponderada": 2, "tasa_credito": 2, "tasa_ahorro": 2, "margen_intermediacion": 2}
    return {"tasas_por_modalidad": por_modalidad.round(redondeo),
            "margen_intermediacion": margen.round(redondeo),
            "tasas_por_tipo_entidad": por_tipo_entidad.round(redondeo)}


if __name__ == "__main__":
    PLATA.mkdir(exist_ok=True)
    ORO.mkdir(exist_ok=True)
    p, rechazos, resumen = plata()
    assert not p.duplicated(LLAVE).any()
    p.to_csv(PLATA / "tasas_semanales.csv", index=False)
    rechazos.to_csv(PLATA / "tasas_rechazos.csv", index=False)
    resumen.rename_axis("resultado").to_csv(ORO / "resumen_capas.csv")
    for nombre, tabla in oro(p).items():
        tabla.to_csv(ORO / f"{nombre}.csv", index=False)
    print(resumen.to_string())
