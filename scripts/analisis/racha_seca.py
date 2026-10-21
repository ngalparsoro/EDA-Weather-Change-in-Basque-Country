"""
Racha seca máxima anual (días consecutivos sin lluvia)
Refuerzo de H2 — Reducción de precipitaciones
"""
import numpy as np
import pandas as pd
from scipy.stats import linregress
import pymannkendall as mk
from scripts.variables import CIUDADES, WINDOW, UMBRAL_RACHA_SECA

UMBRAL_MM = UMBRAL_RACHA_SECA  # mm mínimos para considerar un día como "con lluvia"


def _max_racha(s: pd.Series) -> int:
    """Racha máxima de 1s consecutivos en una Serie binaria."""
    if not s.any():
        return 0
    run_id = (s != s.shift()).cumsum()
    return int(s.groupby(run_id).sum().max())


def _racha_seca_anual(df_ciudad: pd.DataFrame, umbral: float = UMBRAL_MM) -> pd.Series:
    """Para cada año, racha seca máxima (días consecutivos con precipitación < umbral)."""
    df = df_ciudad.sort_values("time")
    seco = (df["precipitation_sum"] < umbral).astype(int)
    return df.assign(seco=seco).groupby("año")["seco"].apply(_max_racha)


def calcular_racha_seca(ciudad, umbral: float = UMBRAL_MM) -> dict:
    serie  = _racha_seca_anual(ciudad.df, umbral)
    año_min, año_max = ciudad.df["año"].min(), ciudad.df["año"].max()
    serie  = serie.reindex(range(año_min, año_max + 1), fill_value=0)
    años   = np.array(serie.index.tolist())
    rachas = serie.values

    mm      = np.convolve(rachas, np.ones(WINDOW) / WINDOW, mode="valid")
    años_mm = años[WINDOW - 1:]

    slope, _, _, p_value, _ = linregress(años, rachas)
    mk_result = mk.original_test(rachas)

    return {
        "ciudad":      ciudad,
        "años":        años.tolist(),
        "rachas":      rachas.tolist(),
        "media_movil": mm.tolist(),
        "años_mm":     años_mm,
        "tendencia":   (slope * años + (rachas.mean() - slope * años.mean())).tolist(),
        "slope":       slope,
        "p_value":     p_value,
        "mk_trend":    mk_result.trend,
        "mk_p":        mk_result.p,
        "umbral":      umbral,
    }


def calcular_todos(ciudades=None) -> list[dict]:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return [calcular_racha_seca(c) for c in ciudades]
