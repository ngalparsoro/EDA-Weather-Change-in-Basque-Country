"""
Análisis de precipitaciones — H2 (reducción y extremos)
Devuelve DataFrames listos para graficar, sin ningún plt.
"""
import numpy as np
import pandas as pd
from scipy.stats import linregress
import pymannkendall as mk
from scripts.variables import CIUDADES, UMBRAL_LLUVIA_INTENSA, UMBRAL_RACHA_SECA


def calcular_precipitacion_anual(ciudad) -> dict:
    """
    Precipitación total anual con tendencia lineal y test Mann-Kendall.
    """
    df    = ciudad.df
    serie = df.groupby("año")["precipitation_sum"].sum()
    años  = np.array(serie.index.tolist())
    precip = serie.values

    slope, intercept, r_value, p_value, _ = linregress(años, precip)
    mk_result = mk.original_test(precip)

    return {
        "ciudad":    ciudad,
        "años":      años.tolist(),
        "precip":    precip.tolist(),
        "tendencia": (slope * años + intercept).tolist(),
        "slope":     slope,
        "p_value":   p_value,
        "r2":        r_value ** 2,
        "mk_trend":  mk_result.trend,
        "mk_p":      mk_result.p,
    }


def calcular_dias_intensos(ciudad, umbral: float = UMBRAL_LLUVIA_INTENSA) -> dict:
    """Días con precipitación > umbral mm por año, rellenando años vacíos con 0."""
    df      = ciudad.df
    serie   = df[df["precipitation_sum"] > umbral].groupby("año").size()
    año_min, año_max = df["año"].min(), df["año"].max()
    serie   = serie.reindex(range(año_min, año_max + 1), fill_value=0)
    return {
        "ciudad": ciudad,
        "años":   serie.index.tolist(),
        "dias":   serie.values.tolist(),
        "umbral": umbral,
    }


def calcular_todos(ciudades=None) -> dict:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return {
        "precip_anual":  [calcular_precipitacion_anual(c) for c in ciudades],
        "dias_intensos": [calcular_dias_intensos(c)       for c in ciudades],
    }
