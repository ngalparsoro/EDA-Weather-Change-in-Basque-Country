"""
Longitud del verano meteorológico (días consecutivos con Tmedia > 20°C)
Refuerzo de H5 — Estacionalidad marcada
"""
import numpy as np
import pandas as pd
from scripts.variables import CIUDADES

UMBRAL_VERANO = 20.0  # °C


def _longitud_verano_anual(df_ciudad: pd.DataFrame,
                            umbral: float = UMBRAL_VERANO) -> pd.Series:
    """
    Para cada año calcula la racha más larga de días consecutivos
    con temperatura media > umbral (verano meteorológico).
    """
    df = df_ciudad.sort_values("time").copy()
    df["calido"] = (df["temperature_2m_mean"] > umbral).astype(int)

    resultados = {}
    for año, grupo in df.groupby("año"):
        max_racha = 0
        racha     = 0
        for calido in grupo["calido"]:
            if calido:
                racha    += 1
                max_racha = max(max_racha, racha)
            else:
                racha = 0
        resultados[año] = max_racha

    return pd.Series(resultados)


def calcular_verano(ciudad, umbral: float = UMBRAL_VERANO) -> dict:
    serie  = _longitud_verano_anual(ciudad.df, umbral)
    años   = serie.index.tolist()
    dias   = serie.values

    window  = 10
    mm      = np.convolve(dias, np.ones(window) / window, mode="valid")
    años_mm = años[window - 1:]

    z         = np.polyfit(años, dias, 1)
    tendencia = np.poly1d(z)

    return {
        "ciudad":     ciudad,
        "años":       años,
        "dias":       dias.tolist(),
        "media_movil":mm.tolist(),
        "años_mm":    años_mm,
        "tendencia":  tendencia(años).tolist(),
        "slope":      z[0],   # días/año
        "umbral":     umbral,
    }


def calcular_todos(ciudades=None) -> list[dict]:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return [calcular_verano(c) for c in ciudades]
