"""
Análisis del régimen de vientos — H6
Devuelve DataFrames listos para graficar, sin ningún plt.
"""
import numpy as np
import pandas as pd
from scipy.stats import linregress
import pymannkendall as mk
from scripts.variables import (CIUDADES, UMBRAL_VIENTO_FUERTE,
                               UMBRAL_VIENTO_MUY_FUERTE, PERIODOS_HISTORICOS)

UMBRAL_FUERTE     = UMBRAL_VIENTO_FUERTE
UMBRAL_MUY_FUERTE = UMBRAL_VIENTO_MUY_FUERTE
PERIODOS          = PERIODOS_HISTORICOS


def calcular_viento_anual(ciudad) -> dict:
    """
    Velocidad media anual del viento (máx. diaria) + tendencia OLS + Mann-Kendall.
    """
    df     = ciudad.df
    serie  = df.groupby("año")["wind_speed_10m_max"].mean()
    años   = np.array(serie.index.tolist())
    viento = serie.values

    slope, intercept, r_value, p_value, _ = linregress(años, viento)
    tendencia = slope * años + intercept
    mk_result = mk.original_test(viento)

    return {
        "ciudad":    ciudad,
        "años":      años.tolist(),
        "viento":    viento,
        "tendencia": tendencia,
        "slope":     slope,
        "p_value":   p_value,
        "r2":        r_value ** 2,
        "mk_trend":  mk_result.trend,
        "mk_p":      mk_result.p,
    }


def calcular_dias_viento_fuerte(ciudad, umbral: float = UMBRAL_FUERTE) -> dict:
    """Días con viento máximo > umbral por año, años sin eventos rellenados con 0."""
    df    = ciudad.df
    serie = df[df["wind_speed_10m_max"] > umbral].groupby("año").size()
    año_min, año_max = df["año"].min(), df["año"].max()
    serie = serie.reindex(range(año_min, año_max + 1), fill_value=0)
    return {
        "ciudad": ciudad,
        "años":   serie.index.tolist(),
        "dias":   serie.values.tolist(),
        "umbral": umbral,
    }


def calcular_perfil_mensual(ciudades) -> pd.DataFrame:
    """
    Perfil mensual de viento por ciudad y período (media de wind_speed_10m_max por mes).
    """
    MESES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    rows  = []
    for ciudad in ciudades:
        df = ciudad.df
        for periodo, (p_ini, p_fin) in PERIODOS.items():
            sub     = df[df["año"].between(p_ini, p_fin)]
            mensual = sub.groupby("mes")["wind_speed_10m_max"].mean()
            for mes_num, mes_str in enumerate(MESES, start=1):
                rows.append({
                    "ciudad":  ciudad.nombre,
                    "color":   ciudad.color,
                    "periodo": periodo,
                    "mes":     mes_num,
                    "mes_str": mes_str,
                    "viento":  mensual.get(mes_num, np.nan),
                })
    return pd.DataFrame(rows)


def calcular_comparativa(ciudades) -> pd.DataFrame:
    """Velocidad media anual por ciudad — para boxplot comparativo."""
    frames = []
    for ciudad in ciudades:
        anual = (ciudad.df.groupby("año")["wind_speed_10m_max"]
                 .mean().reset_index()
                 .rename(columns={"wind_speed_10m_max": "viento_medio"}))
        anual["ciudad"]   = ciudad.nombre
        anual["color"]    = ciudad.color
        anual["dist_mar"] = ciudad.dist_mar
        anual["altitud"]  = ciudad.altitud
        frames.append(anual)
    return pd.concat(frames, ignore_index=True)


def calcular_todos(ciudades=None) -> dict:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return {
        "viento_anual":   [calcular_viento_anual(c) for c in ciudades],
        "dias_fuerte":    [calcular_dias_viento_fuerte(c) for c in ciudades],
        "perfil_mensual": calcular_perfil_mensual(ciudades),
        "comparativa":    calcular_comparativa(ciudades),
        "ciudades":       ciudades,
    }
