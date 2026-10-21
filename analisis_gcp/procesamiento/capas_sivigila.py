"""Lleva SIVIGILA de bronce a plata y oro.

Plata: un solo esquema para todos los años, códigos DIVIPOLA completos y filas rechazadas
apartadas con su motivo. Oro: tablas agregadas listas para tableros.

Uso (después de ingesta_sivigila.py): python analisis_gcp/procesamiento/capas_sivigila.py
"""
import re
import unicodedata
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).resolve().parents[1] / "data"
BRONCE, PLATA, ORO = DATOS / "raw", DATOS / "plata", DATOS / "oro"
ANIOS = (2017, 2018, 2019, 2021)
LLAVE = ["anio", "semana", "codigo_evento", "codigo_municipio"]

# Cada año llega con nombres de columna distintos; se llevan todos al mismo esquema
COLUMNAS = {
    "ano": "anio", "semana": "semana", "cod_eve": "codigo_evento",
    "nombre": "nombre_evento", "nombre_evento": "nombre_evento",
    "cod_dpto": "codigo_departamento", "cod_dpto_o": "codigo_departamento",
    "cod_mun": "codigo_municipio", "cod_mun_o": "codigo_municipio",
    "nom_mun": "nombre_municipio", "municipio_ocurrencia": "nombre_municipio",
    "departamento_ocurrencia": "nombre_departamento",
    "conteo_casos": "casos", "conteo": "casos",
}
# Nombres de departamento que SIVIGILA escribe distinto al DANE
DEPARTAMENTOS = {"SAN ANDRES": "ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA",
                 "BOGOTA": "BOGOTA, D.C.", "NORTE SANTANDER": "NORTE DE SANTANDER",
                 "VALLE": "VALLE DEL CAUCA", "GUAJIRA": "LA GUAJIRA"}
# Municipios que no se resuelven por el nombre base, el paréntesis ni el nombre dentro del oficial
MUNICIPIOS = {
    ("MAGDALENA", "SANTA MARTHA"): "SANTA MARTA",
    ("GUAINIA", "PUERTO INIRIDA"): "INIRIDA",
    ("BOLIVAR", "MOMPOS"): "SANTA CRUZ DE MOMPOX",
    ("CHOCO", "ITSMINA"): "ISTMINA",
    ("CHOCO", "LITORAL DEL BAJO SAN JUAN"): "EL LITORAL DEL SAN JUAN",
    ("CHOCO", "CANTON DE SAN PABLO"): "EL CANTON DEL SAN PABLO",
    ("CORDOBA", "SAN ANDRES SOTAVENTO"): "SAN ANDRES DE SOTAVENTO",
    ("ANTIOQUIA", "SAN PEDRO"): "SAN PEDRO DE LOS MILAGROS",
    ("TOLIMA", "VILLARICA"): "VILLARRICA",
    ("VALLE DEL CAUCA", "DARIEN"): "CALIMA",
    ("META", "LA URIBE"): "URIBE",
    ("CUNDINAMARCA", "SAN ANTONIO DE TEQUENDAMA"): "SAN ANTONIO DEL TEQUENDAMA",
    ("MAGDALENA", "CERRO SAN ANTONIO"): "CERRO DE SAN ANTONIO",
    ("SANTANDER", "PALMAS SOCORRO"): "PALMAS DEL SOCORRO",
    ("VAUPES", "PAPUNAUA"): "PAPUNAHUA",
}


def normalizar(texto):
    sin_tildes = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return " ".join(sin_tildes.upper().split())


def leer_divipola():
    d = pd.read_csv(BRONCE / "divipola.csv", dtype=str)
    d = d.rename(columns={"cod_dpto": "codigo_departamento", "dpto": "nombre_departamento",
                          "cod_mpio": "codigo_municipio", "nom_mpio": "nombre_municipio"})
    d["llave_departamento"] = d["nombre_departamento"].map(normalizar)
    d["llave_municipio"] = d["nombre_municipio"].map(normalizar)
    return d[["codigo_departamento", "nombre_departamento", "codigo_municipio",
              "nombre_municipio", "llave_departamento", "llave_municipio"]]


def con_codigos(b):
    """2017-2019: los códigos llegan sin ceros a la izquierda (5 y 250 en vez de 05 y 05250)."""
    dpto = b["codigo_departamento"].str.zfill(2)
    b["codigo_municipio"] = dpto + b["codigo_municipio"].str.zfill(3)
    b["motivo_rechazo"] = None
    b.loc[dpto == "01", "motivo_rechazo"] = "caso del exterior"
    b.loc[dpto == "00", "motivo_rechazo"] = "procedencia desconocida"
    # SIVIGILA usa el código 000 cuando conoce el departamento pero no el municipio
    b.loc[b["motivo_rechazo"].isna() & b["codigo_municipio"].str.endswith("000"),
          "motivo_rechazo"] = "municipio desconocido"
    return b


def compacto(nombre):
    return re.sub(r"[^A-Z]", "", nombre)


def buscar_codigo(departamento, municipio, oficiales):
    """Código DIVIPOLA de un nombre de SIVIGILA dentro de su departamento, o None si no se resuelve."""
    # "ROBLES (LA PAZ)": se prueba el nombre sin paréntesis y el que va dentro
    base = re.sub(r"\(.*", "", municipio).strip()
    dentro = re.findall(r"\(([^()]*)\)", municipio)
    candidatos = [municipio, base, MUNICIPIOS.get((departamento, base)), *dentro]
    por_compacto = {compacto(nombre): codigo for nombre, codigo in oficiales.items()}
    for candidato in filter(None, candidatos):
        if candidato in oficiales:
            return oficiales[candidato]
        if compacto(candidato) in por_compacto:  # "POLO NUEVO" y "POLONUEVO"
            return por_compacto[compacto(candidato)]
    # Nombre corto dentro del oficial ("CALI" en "SANTIAGO DE CALI"), solo si hay uno
    patron = re.compile(rf"\b{re.escape(base)}\b")
    encontrados = [codigo for nombre, codigo in oficiales.items() if patron.search(nombre)]
    return encontrados[0] if len(encontrados) == 1 else None


def con_nombres(b, divipola):
    """2021: solo trae nombres; el código se busca en DIVIPOLA por departamento y municipio."""
    dpto = b["nombre_departamento"].map(normalizar).replace(DEPARTAMENTOS)
    b["llave_departamento"], b["llave_municipio"] = dpto, b["nombre_municipio"].map(normalizar)
    oficiales = {d: dict(zip(g["llave_municipio"], g["codigo_municipio"]))
                 for d, g in divipola.groupby("llave_departamento")}
    pares = b[["llave_departamento", "llave_municipio"]].drop_duplicates()
    pares["codigo_municipio"] = [buscar_codigo(d, m, oficiales.get(d, {}))
                                 for d, m in zip(pares["llave_departamento"], pares["llave_municipio"])]
    b = b.merge(pares, on=["llave_departamento", "llave_municipio"], how="left")
    b["motivo_rechazo"] = None
    b.loc[b["codigo_municipio"].isna(), "motivo_rechazo"] = "municipio sin código en DIVIPOLA"
    b.loc[dpto.str.startswith("EXTERIOR"), "motivo_rechazo"] = "caso del exterior"
    b.loc[dpto == "PROCEDENCIA DESCONOCIDA", "motivo_rechazo"] = "procedencia desconocida"
    return b


def leer_bronce(anio):
    return pd.read_csv(BRONCE / f"sivigila_{anio}.csv", dtype=str).rename(columns=lambda c: COLUMNAS[c.lower()])


def plata(divipola):
    filas, resumen = [], []
    for anio in ANIOS:
        b = leer_bronce(anio)
        b = con_codigos(b) if "codigo_municipio" in b else con_nombres(b, divipola)
        validos = b["codigo_municipio"].isin(divipola["codigo_municipio"])
        b.loc[b["motivo_rechazo"].isna() & ~validos, "motivo_rechazo"] = "código de municipio inexistente"
        resumen.append(b["motivo_rechazo"].fillna("aceptada").value_counts().rename(anio))
        filas.append(b)

    todo = pd.concat(filas, ignore_index=True)
    todo["casos"] = todo["casos"].astype(int)
    rechazos = todo[todo["motivo_rechazo"].notna()]
    # Los nombres y el departamento salen siempre de DIVIPOLA, no de la fuente
    aceptadas = todo[todo["motivo_rechazo"].isna()].drop(
        columns=["nombre_municipio", "codigo_departamento", "nombre_departamento",
                 "llave_departamento", "llave_municipio"], errors="ignore")
    aceptadas = aceptadas.merge(divipola.drop(columns=["llave_departamento", "llave_municipio"]),
                                on="codigo_municipio")
    # Una fila por llave: si el portal repite una combinación, se suman sus casos
    columnas = LLAVE + ["nombre_evento", "codigo_departamento", "nombre_departamento", "nombre_municipio"]
    aceptadas = aceptadas.groupby(columnas, as_index=False)["casos"].sum()
    aceptadas[["anio", "semana"]] = aceptadas[["anio", "semana"]].astype(int)
    return aceptadas, rechazos, pd.concat(resumen, axis=1).fillna(0).astype(int)


def oro(p):
    por_semana = p.groupby(["anio", "semana"], as_index=False)["casos"].sum()
    por_evento = (p.groupby(["anio", "codigo_evento", "nombre_evento"], as_index=False)["casos"].sum()
                  .sort_values(["anio", "casos"], ascending=[True, False]))
    por_departamento = p.groupby(["anio", "codigo_departamento", "nombre_departamento"],
                                 as_index=False)["casos"].sum()
    return {"casos_por_semana": por_semana, "casos_por_evento": por_evento,
            "casos_por_departamento": por_departamento}


if __name__ == "__main__":
    PLATA.mkdir(exist_ok=True)
    ORO.mkdir(exist_ok=True)
    p, rechazos, resumen = plata(leer_divipola())
    assert not p.duplicated(LLAVE).any()
    # Cuadre: ningún caso se pierde entre bronce y plata, o está aceptado o está apartado
    bronce = sum(leer_bronce(anio)["casos"].astype(int).sum() for anio in ANIOS)
    assert bronce == p["casos"].sum() + rechazos["casos"].sum(), "los casos no cuadran entre capas"
    p.to_csv(PLATA / "sivigila_casos.csv", index=False)
    rechazos.to_csv(PLATA / "sivigila_rechazos.csv", index=False)
    resumen.rename_axis("resultado").to_csv(ORO / "resumen_capas.csv")
    for nombre, tabla in oro(p).items():
        tabla.to_csv(ORO / f"{nombre}.csv", index=False)
    print(resumen.to_string())
    print(f"plata: {len(p)} filas, {p['casos'].sum()} casos")
