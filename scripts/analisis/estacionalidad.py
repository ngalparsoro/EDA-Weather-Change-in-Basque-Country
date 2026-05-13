"""
Análisis de estacionalidad y comparativa entre ciudades — H3 y H5
Devuelve DataFrames listos para graficar, sin ningún plt.
"""
import numpy as np
import pandas as pd
from scripts.variables import CIUDADES


def calcular_media_mensual_por_quinquenio(ciudad, inicio: int = 1950, fin: int = 2025) -> dict:
    """
    Temperatura media mensual agrupada por quinquenios.
    Devuelve un dict con los periodos y sus series mensuales.
    """
    df = ciudad.df
    periodos = {}
    for año in range(inicio, fin + 1, 5):
        etiqueta = f"{año}–{min(año + 4, fin)}"
        sub = df[(df["año"] >= año) & (df["año"] <= año + 4)]
        if not sub.empty:
            periodos[etiqueta] = sub.groupby("mes")["temperature_2m_mean"].mean()

    return {"ciudad": ciudad, "periodos": periodos}


def calcular_amplitud_termica(ciudad, inicio: int = 1950, fin: int = 2025) -> dict:
    """
    Amplitud térmica estacional (Julio - Enero) por quinquenio.
    """
    df = ciudad.df
    amplitudes = {}
    for año in range(inicio, fin + 1, 5):
        etiqueta = f"{año}–{min(año + 4, fin)}"
        sub = df[(df["año"] >= año) & (df["año"] <= año + 4)]
        if sub.empty:
            amplitudes[etiqueta] = np.nan
            continue
        mensual = sub.groupby("mes")["temperature_2m_mean"].mean()
        amplitudes[etiqueta] = (
            mensual.get(7, np.nan) - mensual.get(1, np.nan)
        )

    return {"ciudad": ciudad, "amplitudes": amplitudes}


def calcular_comparativa_ciudades(variable: str = "temperature_2m_mean",
                                   agg_func: str = "mean",
                                   ciudades=None) -> dict:
    """
    Serie anual de una variable para todas las ciudades (para H3).
    """
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    series = {}
    for ciudad in ciudades:
        grupo = ciudad.df.groupby("año")[variable]
        series[ciudad.nombre] = grupo.mean() if agg_func == "mean" else grupo.sum()

    return {"variable": variable, "series": series, "ciudades": ciudades}


def calcular_todos(ciudades=None) -> dict:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return {
        "estacionalidad":   [calcular_media_mensual_por_quinquenio(c) for c in ciudades],
        "amplitud":         [calcular_amplitud_termica(c)              for c in ciudades],
        "comp_temp":        calcular_comparativa_ciudades("temperature_2m_mean", "mean",  ciudades),
        "comp_precip":      calcular_comparativa_ciudades("precipitation_sum",   "sum",   ciudades),
    }
