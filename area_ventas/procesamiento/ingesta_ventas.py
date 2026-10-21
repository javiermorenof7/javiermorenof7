"""Descarga a la capa bronce local las ventas reales de Online Retail II (UCI Machine Learning
Repository, CC BY 4.0): 1.067.371 líneas de factura de un minorista del Reino Unido, 2009-2011.

El libro trae una hoja por periodo; bronce las une en un CSV con la hoja de origen. El conjunto
es estático: si el CSV y su archivo de control ya existen, no se vuelve a descargar.

Uso: python area_ventas/procesamiento/ingesta_ventas.py
Leer el Excel necesita openpyxl (sin instalarlo: uv run --with pandas --with openpyxl --with requests ...)
"""
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
BRONCE = Path(__file__).resolve().parents[1] / "data" / "raw"


def descargar():
    destino, control = BRONCE / "online_retail_ii.csv", BRONCE / "online_retail_ii.control.json"
    if destino.exists() and control.exists():
        print("online_retail_ii: ya está en bronce, se omite")
        return

    r = requests.get(URL, timeout=300)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        libro = next(n for n in z.namelist() if n.endswith(".xlsx"))
        hojas = pd.read_excel(z.open(libro), sheet_name=None, dtype=str)
    bronce = pd.concat([h.assign(hoja=nombre) for nombre, h in hojas.items()], ignore_index=True)
    bronce.to_csv(destino, index=False)

    control.write_text(json.dumps({
        "fuente": URL,
        "filas": len(bronce),
        "hojas": {nombre: len(h) for nombre, h in hojas.items()},
        "huella_sha256_zip": hashlib.sha256(r.content).hexdigest(),
        "licencia": "CC BY 4.0",
        "fecha_ingesta": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, indent=2))
    print(f"online_retail_ii: {len(bronce)} filas descargadas")


if __name__ == "__main__":
    BRONCE.mkdir(parents=True, exist_ok=True)
    descargar()
