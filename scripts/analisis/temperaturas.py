"""
Análisis de temperaturas — H1 (aumento) y H4 (extremos)
Devuelve DataFrames listos para graficar, sin ningún plt.
"""
import numpy as np
import pandas as pd
from scripts.variables import CIUDADES


def calcular_dias_30(ciudad) -> dict:
    """Días con Tmax > 30°C por año."""
    df = ciudad.df
    serie = df[df["temperature_2m_max"] > 30].groupby("año").size()
    años  = serie.index.tolist()
    dias  = serie.values.tolist()
    return {"ciudad": ciudad, "años": años, "dias": dias}


def calcular_temp_media_anual(ciudad) -> dict:
    """Temperatura media anual con tendencia lineal."""
    df    = ciudad.df
    serie = df.groupby("año")["temperature_2m_mean"].mean()
    años  = serie.index.tolist()
    temps = serie.values

    z         = np.polyfit(años, temps, 1)
    tendencia = np.poly1d(z)

    return {
        "ciudad":    ciudad,
        "años":      años,
        "temps":     temps,
        "tendencia": tendencia(años),
        "slope":     z[0],          # °C/año
    }


def calcular_dias_extremos(ciudad, umbral: float = 35.0) -> dict:
    """Días con Tmax > umbral por año, rellenando años sin eventos con 0."""
    df     = ciudad.df
    serie  = df[df["temperature_2m_max"] > umbral].groupby("año").size()
    año_min, año_max = df["año"].min(), df["año"].max()
    serie  = serie.reindex(range(año_min, año_max + 1), fill_value=0)
    return {
        "ciudad": ciudad,
        "años":   serie.index.tolist(),
        "dias":   serie.values.tolist(),
        "umbral": umbral,
    }


def calcular_todos(ciudades=None) -> dict:
    """
    Calcula todas las métricas de temperatura para una lista de ciudades.
    Devuelve un dict con listas de resultados por análisis.
    """
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return {
        "dias_30":      [calcular_dias_30(c)          for c in ciudades],
        "temp_media":   [calcular_temp_media_anual(c)  for c in ciudades],
        "dias_extremos":[calcular_dias_extremos(c)     for c in ciudades],
    }
