"""Descarga a la capa bronce local los casos semanales de SIVIGILA (INS) y el maestro DIVIPOLA
de municipios (DANE), publicados en datos.gov.co.

Cada año de SIVIGILA es un conjunto distinto del portal. La descarga es idempotente: si el archivo local
ya corresponde a la última actualización publicada, no se vuelve a bajar.

Uso: python analisis_gcp/procesamiento/ingesta_sivigila.py
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

PORTAL = "https://www.datos.gov.co"
CONJUNTOS = {
    "sivigila_2017": "84d4-vfax",
    "sivigila_2018": "xd2n-cu8j",
    "sivigila_2019": "qvnt-2igj",
    "sivigila_2021": "fhc4-jjti",
    "divipola": "gdxc-w37w",
}
LOTE = 50000
BRONCE = Path(__file__).resolve().parents[1] / "data" / "raw"


def metadatos(id_conjunto):
    meta = requests.get(f"{PORTAL}/api/views/{id_conjunto}.json", timeout=60).json()
    conteo = requests.get(f"{PORTAL}/resource/{id_conjunto}.json",
                          params={"$select": "count(*)"}, timeout=60).json()
    return {"filas": int(conteo[0]["count"]), "actualizado": meta["rowsUpdatedAt"],
            "licencia": meta.get("license", {}).get("name")}


def descargar(nombre, id_conjunto):
    destino = BRONCE / f"{nombre}.csv"
    control = BRONCE / f"{nombre}.control.json"
    meta = metadatos(id_conjunto)
    if destino.exists() and control.exists():
        previo = json.loads(control.read_text())
        if previo["actualizado"] == meta["actualizado"] and previo["filas"] == meta["filas"]:
            print(f"{nombre}: sin cambios en el portal, se omite")
            return

    # Paginado con orden estable (:id) para no perder ni repetir filas entre lotes
    lineas, offset = [], 0
    while True:
        r = requests.get(f"{PORTAL}/resource/{id_conjunto}.csv", timeout=300,
                         params={"$limit": LOTE, "$offset": offset, "$order": ":id"})
        r.raise_for_status()
        lote = r.text.splitlines()
        if len(lote) <= 1:
            break
        lineas.extend(lote if not lineas else lote[1:])
        offset += LOTE

    filas = len(lineas) - 1
    if filas != meta["filas"]:
        raise RuntimeError(f"{nombre}: se bajaron {filas} filas y el portal publica {meta['filas']}")

    contenido = "\n".join(lineas) + "\n"
    destino.write_text(contenido, encoding="utf-8")
    control.write_text(json.dumps({
        "conjunto": id_conjunto,
        "filas": filas,
        "actualizado": meta["actualizado"],
        "licencia": meta["licencia"],
        "huella_sha256": hashlib.sha256(contenido.encode("utf-8")).hexdigest(),
        "fecha_ingesta": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, indent=2))
    print(f"{nombre}: {filas} filas descargadas")


if __name__ == "__main__":
    BRONCE.mkdir(parents=True, exist_ok=True)
    for nombre, id_conjunto in CONJUNTOS.items():
        descargar(nombre, id_conjunto)
