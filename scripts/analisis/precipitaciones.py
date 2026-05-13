"""
Análisis de precipitaciones — H2 (reducción y extremos)
Devuelve DataFrames listos para graficar, sin ningún plt.
"""
import pandas as pd
from scripts.variables import CIUDADES


def calcular_precipitacion_anual(ciudad) -> dict:
    """Precipitación total anual."""
    df    = ciudad.df
    serie = df.groupby("año")["precipitation_sum"].sum()
    return {
        "ciudad": ciudad,
        "años":   serie.index.tolist(),
        "precip": serie.values.tolist(),
    }


def calcular_dias_intensos(ciudad, umbral: float = 30.0) -> dict:
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
