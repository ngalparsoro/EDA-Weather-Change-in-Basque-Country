"""
Detección y duración de olas de calor
Refuerzo de H4 — Frecuencia de temperaturas extremas

Definición usada: ≥ 3 días consecutivos con Tmax > 35°C
(adaptable mediante parámetros)
"""
import numpy as np
import pandas as pd
from scripts.variables import CIUDADES


def _detectar_olas(df_ciudad: pd.DataFrame,
                   umbral: float = 35.0,
                   min_dias: int = 3) -> pd.DataFrame:
    """
    Devuelve un DataFrame con cada ola de calor detectada:
    año, fecha_inicio, fecha_fin, duración (días).
    """
    df    = df_ciudad.sort_values("time").copy()
    df["extremo"] = (df["temperature_2m_max"] > umbral).astype(int)

    olas  = []
    racha = 0
    inicio = None

    for _, row in df.iterrows():
        if row["extremo"]:
            racha += 1
            if racha == 1:
                inicio = row["time"]
        else:
            if racha >= min_dias:
                olas.append({
                    "año":          inicio.year,
                    "fecha_inicio": inicio,
                    "fecha_fin":    row["time"] - pd.Timedelta(days=1),
                    "duracion":     racha,
                })
            racha  = 0
            inicio = None

    # Cerrar racha al final de la serie
    if racha >= min_dias:
        olas.append({
            "año":          inicio.year,
            "fecha_inicio": inicio,
            "fecha_fin":    df["time"].iloc[-1],
            "duracion":     racha,
        })

    return pd.DataFrame(olas) if olas else pd.DataFrame(
        columns=["año", "fecha_inicio", "fecha_fin", "duracion"]
    )


def calcular_olas_calor(ciudad,
                         umbral: float = 35.0,
                         min_dias: int = 3) -> dict:
    olas = _detectar_olas(ciudad.df, umbral, min_dias)

    if olas.empty:
        return {
            "ciudad":          ciudad,
            "olas":            olas,
            "num_olas_anual":  pd.Series(dtype=float),
            "duracion_max":    pd.Series(dtype=float),
            "duracion_total":  pd.Series(dtype=float),
            "umbral":          umbral,
            "min_dias":        min_dias,
        }

    num_olas_anual = olas.groupby("año").size()
    duracion_max   = olas.groupby("año")["duracion"].max()
    duracion_total = olas.groupby("año")["duracion"].sum()

    # Rellenar años sin olas con 0
    año_min = ciudad.df["año"].min()
    año_max = ciudad.df["año"].max()
    idx     = range(año_min, año_max + 1)
    num_olas_anual = num_olas_anual.reindex(idx, fill_value=0)
    duracion_max   = duracion_max.reindex(idx, fill_value=0)
    duracion_total = duracion_total.reindex(idx, fill_value=0)

    return {
        "ciudad":         ciudad,
        "olas":           olas,
        "num_olas_anual": num_olas_anual,
        "duracion_max":   duracion_max,
        "duracion_total": duracion_total,
        "umbral":         umbral,
        "min_dias":       min_dias,
    }


def calcular_todos(ciudades=None, umbral: float = 35.0, min_dias: int = 3) -> list[dict]:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return [calcular_olas_calor(c, umbral, min_dias) for c in ciudades]
