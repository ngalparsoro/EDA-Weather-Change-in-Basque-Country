"""
Anomalía térmica anual respecto al período base 1961–1990 (estándar OMM)
Refuerzo de H1 — Aumento de temperaturas
"""
import numpy as np
import pandas as pd
from scripts.variables import CIUDADES

PERIODO_BASE = (1961, 1990)


def calcular_anomalia(ciudad, periodo_base: tuple = PERIODO_BASE) -> dict:
    """
    Calcula la anomalía térmica anual de cada año respecto a la media
    del período base. Valores positivos = más cálido que la media histórica.
    """
    df         = ciudad.df
    temp_anual = df.groupby("año")["temperature_2m_mean"].mean()

    base = temp_anual.loc[periodo_base[0]:periodo_base[1]].mean()

    anomalia = temp_anual - base

    # Media móvil 10 años
    window   = 10
    valores  = anomalia.values
    mm       = np.convolve(valores, np.ones(window) / window, mode="valid")
    años_mm  = anomalia.index.tolist()[window - 1:]

    return {
        "ciudad":       ciudad,
        "años":         anomalia.index.tolist(),
        "anomalia":     anomalia.values.tolist(),
        "media_movil":  mm.tolist(),
        "años_mm":      años_mm,
        "base":         base,
        "periodo_base": periodo_base,
    }


def calcular_todos(ciudades=None) -> list[dict]:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return [calcular_anomalia(c) for c in ciudades]
