"""Descarga a la capa bronce local Absenteeism at work (UCI Machine Learning Repository, CC BY 4.0):
740 registros reales de ausencias en una empresa de mensajería de Brasil, julio de 2007 a julio
de 2010. Los empleados llegan anonimizados con un número.

El conjunto es estático: si el CSV y su archivo de control ya existen, no se vuelve a descargar.

Uso: python analisis_company/procesamiento/ingesta_ausentismo.py
"""
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests

URL = "https://archive.ics.uci.edu/static/public/445/absenteeism+at+work.zip"
BRONCE = Path(__file__).resolve().parents[1] / "data" / "raw"


def descargar():
    destino, control = BRONCE / "absenteeism_at_work.csv", BRONCE / "absenteeism_at_work.control.json"
    if destino.exists() and control.exists():
        print("absenteeism_at_work: ya está en bronce, se omite")
        return

    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        contenido = z.read("Absenteeism_at_work.csv")
    destino.write_bytes(contenido)
    filas = contenido.decode("utf-8").count("\n") - 1
    control.write_text(json.dumps({
        "fuente": URL,
        "filas": filas,
        "huella_sha256_zip": hashlib.sha256(r.content).hexdigest(),
        "licencia": "CC BY 4.0",
        "fecha_ingesta": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, indent=2))
    print(f"absenteeism_at_work: {filas} filas descargadas")


if __name__ == "__main__":
    BRONCE.mkdir(parents=True, exist_ok=True)
    descargar()
