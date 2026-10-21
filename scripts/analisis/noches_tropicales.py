"""
Noches tropicales y noches muy cálidas — indicador de calentamiento nocturno

Definiciones:
  - Noche tropical:    Tmin >= 20°C  (calor que impide la recuperación térmica)
  - Noche muy cálida:  Tmin >= 25°C  (estrés térmico severo)
"""
import numpy as np
import pandas as pd
from scipy.stats import linregress
from scripts.variables import (CIUDADES, WINDOW,
                               UMBRAL_NOCHE_TROPICAL, UMBRAL_NOCHE_CALIDA)

UMBRAL_TROPICAL   = UMBRAL_NOCHE_TROPICAL
UMBRAL_MUY_CALIDA = UMBRAL_NOCHE_CALIDA


def calcular_noches(ciudad, umbral: float = UMBRAL_TROPICAL) -> dict:
    df    = ciudad.df
    serie = (df[df["temperature_2m_min"] >= umbral]
             .groupby("año").size()
             .reindex(range(df["año"].min(), df["año"].max() + 1), fill_value=0))

    años    = np.array(serie.index.tolist())
    noches  = serie.values.astype(float)

    slope, intercept, _, p_value, _ = linregress(años, noches)
    tendencia = slope * años + intercept

    años_mm  = años[WINDOW - 1:]
    media_m  = np.convolve(noches, np.ones(WINDOW) / WINDOW, mode="valid")

    return {
        "ciudad":    ciudad,
        "años":      años.tolist(),
        "noches":    noches.tolist(),
        "tendencia": tendencia.tolist(),
        "años_mm":   años_mm.tolist(),
        "media_movil": media_m.tolist(),
        "slope":     slope,
        "p_value":   p_value,
        "umbral":    umbral,
    }


def calcular_todos(ciudades=None, umbral: float = UMBRAL_TROPICAL) -> list[dict]:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return [calcular_noches(c, umbral) for c in ciudades]


def calcular_todos_umbrales(ciudades=None) -> dict:
    """Devuelve resultados para ambos umbrales (20°C y 25°C)."""
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return {
        "tropicales":   calcular_todos(ciudades, UMBRAL_TROPICAL),
        "muy_calidas":  calcular_todos(ciudades, UMBRAL_MUY_CALIDA),
    }
