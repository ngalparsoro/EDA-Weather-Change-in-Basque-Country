"""
Racha seca máxima anual (días consecutivos sin lluvia)
Refuerzo de H2 — Reducción de precipitaciones
"""
import numpy as np
import pandas as pd
from scripts.variables import CIUDADES

UMBRAL_MM = 1.0  # mm mínimos para considerar un día como "con lluvia"


def _racha_seca_anual(df_ciudad: pd.DataFrame, umbral: float = UMBRAL_MM) -> pd.Series:
    """
    Para cada año calcula la racha seca máxima (días consecutivos con
    precipitación < umbral).
    """
    df = df_ciudad.sort_values("time").copy()
    df["seco"] = (df["precipitation_sum"] < umbral).astype(int)

    resultados = {}
    for año, grupo in df.groupby("año"):
        max_racha = 0
        racha     = 0
        for seco in grupo["seco"]:
            if seco:
                racha    += 1
                max_racha = max(max_racha, racha)
            else:
                racha = 0
        resultados[año] = max_racha

    return pd.Series(resultados)


def calcular_racha_seca(ciudad, umbral: float = UMBRAL_MM) -> dict:
    serie  = _racha_seca_anual(ciudad.df, umbral)
    años   = serie.index.tolist()
    rachas = serie.values

    window  = 10
    mm      = np.convolve(rachas, np.ones(window) / window, mode="valid")
    años_mm = años[window - 1:]

    z         = np.polyfit(años, rachas, 1)
    tendencia = np.poly1d(z)

    return {
        "ciudad":     ciudad,
        "años":       años,
        "rachas":     rachas.tolist(),
        "media_movil":mm.tolist(),
        "años_mm":    años_mm,
        "tendencia":  tendencia(años).tolist(),
        "slope":      z[0],   # días/año
        "umbral":     umbral,
    }


def calcular_todos(ciudades=None) -> list[dict]:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return [calcular_racha_seca(c) for c in ciudades]
