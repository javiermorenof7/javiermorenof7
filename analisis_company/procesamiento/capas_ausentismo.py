"""Lleva Absenteeism at work de bronce a plata y oro con un modelo dimensional.

Plata: una ausencia por fila con nombres de columna claros y los registros que no son ausencias
apartados con su motivo. Oro: dimensiones de empleado y de motivo, hecho de ausencias y horas
perdidas por motivo, mes y día de la semana.

Uso (después de ingesta_ausentismo.py): python analisis_company/procesamiento/capas_ausentismo.py
"""
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).resolve().parents[1] / "data"
BRONCE, ORO = DATOS / "raw", DATOS / "oro"
COLUMNAS = {
    "ID": "id_empleado", "Reason for absence": "codigo_motivo", "Month of absence": "mes",
    "Day of the week": "codigo_dia_semana", "Seasons": "codigo_estacion",
    "Transportation expense": "gasto_transporte", "Distance from Residence to Work": "distancia_trabajo_km",
    "Service time": "antiguedad_anios", "Age": "edad", "Work load Average/day ": "carga_trabajo_promedio_dia",
    "Hit target": "cumplimiento_meta", "Disciplinary failure": "falta_disciplinaria", "Education": "codigo_educacion",
    "Son": "numero_hijos", "Social drinker": "consume_alcohol", "Social smoker": "fuma", "Pet": "numero_mascotas",
    "Weight": "peso_kg", "Height": "estatura_cm", "Body mass index": "indice_masa_corporal",
    "Absenteeism time in hours": "horas_ausencia",
}
# Motivos 1 a 21: capítulos de la Clasificación Internacional de Enfermedades (CIE-10); 22 a 28, otros
MOTIVOS = {
    1: "Enfermedades infecciosas y parasitarias", 2: "Tumores", 3: "Enfermedades de la sangre",
    4: "Enfermedades endocrinas y metabólicas", 5: "Trastornos mentales", 6: "Sistema nervioso",
    7: "Ojo", 8: "Oído", 9: "Sistema circulatorio", 10: "Sistema respiratorio", 11: "Sistema digestivo",
    12: "Piel", 13: "Sistema osteomuscular", 14: "Sistema genitourinario", 15: "Embarazo y parto",
    16: "Afecciones perinatales", 17: "Malformaciones congénitas", 18: "Síntomas no clasificados",
    19: "Lesiones y envenenamientos", 20: "Causas externas", 21: "Factores que influyen en la salud",
    22: "Seguimiento de paciente", 23: "Consulta médica", 24: "Donación de sangre",
    25: "Examen de laboratorio", 26: "Ausencia injustificada", 27: "Fisioterapia", 28: "Consulta odontológica",
}
DIAS = {2: "Lunes", 3: "Martes", 4: "Miércoles", 5: "Jueves", 6: "Viernes"}
ATRIBUTOS_EMPLEADO = ["edad", "antiguedad_anios", "codigo_educacion", "numero_hijos", "numero_mascotas",
                      "consume_alcohol", "fuma", "peso_kg", "estatura_cm", "indice_masa_corporal",
                      "distancia_trabajo_km", "gasto_transporte"]


def plata():
    b = pd.read_csv(BRONCE / "absenteeism_at_work.csv", sep=";").rename(columns=COLUMNAS)
    b["motivo_rechazo"] = None
    b.loc[(b["codigo_motivo"] == 0) & (b["horas_ausencia"] == 0), "motivo_rechazo"] = "registro sin ausencia"
    b.loc[b["motivo_rechazo"].isna() & (b["horas_ausencia"] == 0), "motivo_rechazo"] = "ausencia sin horas"
    rechazos = b[b["motivo_rechazo"].notna()]
    p = b[b["motivo_rechazo"].isna()].drop(columns="motivo_rechazo").reset_index(drop=True)
    assert p["codigo_motivo"].isin(MOTIVOS).all() and p["mes"].between(1, 12).all()

    resumen = rechazos["motivo_rechazo"].value_counts()
    resumen["aceptada"] = len(p)
    # Filas idénticas: sin fecha exacta no se puede probar que sean la misma ausencia, se conservan
    resumen["aceptada, idéntica a otra (se conserva)"] = int(p.duplicated().sum())
    assert resumen.drop("aceptada, idéntica a otra (se conserva)").sum() == len(b)
    return p, resumen.rename("filas")


def oro(p):
    # Un empleado puede llegar con atributos distintos entre registros; queda el valor más frecuente
    inconsistentes = int((p.groupby("id_empleado")[ATRIBUTOS_EMPLEADO].nunique() > 1).any(axis=1).sum())
    dim_empleado = p.groupby("id_empleado")[ATRIBUTOS_EMPLEADO].agg(lambda s: s.mode().iloc[0]).reset_index()
    dim_motivo = pd.DataFrame({"codigo_motivo": list(MOTIVOS), "nombre_motivo": list(MOTIVOS.values())})
    dim_motivo["grupo_motivo"] = ["Enfermedad (CIE-10)" if c <= 21 else "Otro" for c in MOTIVOS]

    hecho = p[["id_empleado", "codigo_motivo", "mes", "codigo_dia_semana", "codigo_estacion",
               "carga_trabajo_promedio_dia", "cumplimiento_meta", "falta_disciplinaria", "horas_ausencia"]]
    hecho.insert(0, "id_ausencia", range(1, len(hecho) + 1))

    con_motivo = hecho.merge(dim_motivo, on="codigo_motivo")
    por_motivo = (con_motivo.groupby(["codigo_motivo", "nombre_motivo", "grupo_motivo"])
                  .agg(ausencias=("id_ausencia", "count"), horas_ausencia=("horas_ausencia", "sum"))
                  .sort_values("horas_ausencia", ascending=False).reset_index())
    por_mes = hecho.groupby("mes").agg(ausencias=("id_ausencia", "count"),
                                       horas_ausencia=("horas_ausencia", "sum")).reset_index()
    por_dia = (hecho.assign(dia_semana=hecho["codigo_dia_semana"].map(DIAS))
               .groupby(["codigo_dia_semana", "dia_semana"])
               .agg(ausencias=("id_ausencia", "count"), horas_ausencia=("horas_ausencia", "sum")).reset_index())
    tablas = {"dim_empleado": dim_empleado, "dim_motivo": dim_motivo, "hecho_ausencia": hecho,
              "horas_por_motivo": por_motivo, "horas_por_mes": por_mes, "horas_por_dia": por_dia}
    return tablas, inconsistentes


if __name__ == "__main__":
    ORO.mkdir(exist_ok=True)
    p, resumen = plata()
    tablas, inconsistentes = oro(p)
    resumen["empleados con atributos distintos entre registros"] = inconsistentes
    resumen.rename_axis("resultado").to_csv(ORO / "resumen_capas.csv")
    for nombre, tabla in tablas.items():
        tabla.to_csv(ORO / f"{nombre}.csv", index=False)
    print(resumen.to_string())
