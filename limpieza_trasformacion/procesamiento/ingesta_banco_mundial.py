"""Descarga a la capa bronce local el PIB per cápita (US$ a precios actuales, NY.GDP.PCAP.CD) de
los Indicadores del Desarrollo Mundial del Banco Mundial (CC BY 4.0), tal como lo entrega su
descarga en CSV: un zip con el indicador en formato ancho y los metadatos de países.

Si el portal entrega el mismo zip (misma huella SHA-256), no se reescribe bronce.

Uso: python limpieza_trasformacion/procesamiento/ingesta_banco_mundial.py
"""
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests

INDICADOR = "NY.GDP.PCAP.CD"
URL = f"https://api.worldbank.org/v2/country/all/indicator/{INDICADOR}?downloadformat=csv"
BRONCE = Path(__file__).resolve().parents[1] / "data" / "raw"


def descargar():
    control = BRONCE / "banco_mundial.control.json"
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    huella = hashlib.sha256(r.content).hexdigest()
    if control.exists() and json.loads(control.read_text())["huella_sha256_zip"] == huella:
        print("banco_mundial: sin cambios en el portal, se omite")
        return

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        for nombre in z.namelist():
            # API_<indicador>... trae los valores; Metadata_Country... la región y el grupo de ingreso
            destino = "indicador.csv" if nombre.startswith("API_") else (
                "metadatos_paises.csv" if nombre.startswith("Metadata_Country") else None)
            if destino:
                (BRONCE / destino).write_bytes(z.read(nombre))
    control.write_text(json.dumps({
        "fuente": URL, "indicador": INDICADOR, "huella_sha256_zip": huella, "licencia": "CC BY 4.0",
        "fecha_ingesta": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, indent=2))
    print(f"banco_mundial: {INDICADOR} descargado")


if __name__ == "__main__":
    BRONCE.mkdir(parents=True, exist_ok=True)
    descargar()
