"""
Análisis de temperaturas — H1 (aumento) y H4 (extremos)
Devuelve DataFrames listos para graficar, sin ningún plt.
"""
import numpy as np
import pandas as pd
from scipy.stats import linregress
import pymannkendall as mk
from scripts.variables import CIUDADES


def calcular_dias_p90(ciudad) -> dict:
    """
    Días con Tmax > percentil 90 local por año.
    El umbral se calcula sobre todo el período, lo que hace la métrica
    comparable entre ciudades con climas muy distintos.
    """
    df     = ciudad.df
    umbral = df["temperature_2m_max"].quantile(0.90)
    serie  = df[df["temperature_2m_max"] > umbral].groupby("año").size()
    año_min, año_max = df["año"].min(), df["año"].max()
    serie  = serie.reindex(range(año_min, año_max + 1), fill_value=0)
    return {
        "ciudad": ciudad,
        "años":   serie.index.tolist(),
        "dias":   serie.values.tolist(),
        "umbral": round(umbral, 1),
    }


def calcular_temp_media_anual(ciudad) -> dict:
    """
    Temperatura media anual con tendencia lineal (OLS) y test Mann-Kendall.
    Devuelve slope (°C/año), p-valor OLS, R², y resultado Mann-Kendall.
    """
    df    = ciudad.df
    serie = df.groupby("año")["temperature_2m_mean"].mean()
    años  = np.array(serie.index.tolist())
    temps = serie.values

    slope, intercept, r_value, p_value, _ = linregress(años, temps)
    tendencia = slope * años + intercept

    mk_result = mk.original_test(temps)

    return {
        "ciudad":    ciudad,
        "años":      años.tolist(),
        "temps":     temps,
        "tendencia": tendencia,
        "slope":     slope,
        "p_value":   p_value,
        "r2":        r_value ** 2,
        "mk_trend":  mk_result.trend,
        "mk_p":      mk_result.p,
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
        "dias_p90":     [calcular_dias_p90(c)          for c in ciudades],
        "temp_media":   [calcular_temp_media_anual(c)   for c in ciudades],
        "dias_extremos":[calcular_dias_extremos(c)      for c in ciudades],
    }
