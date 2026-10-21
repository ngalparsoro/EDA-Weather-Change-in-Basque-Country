"""
Longitud del verano meteorológico (días consecutivos con Tmedia > 20°C)
Refuerzo de H5 — Estacionalidad marcada
"""
import numpy as np
import pandas as pd
from scipy.stats import linregress
from scripts.variables import CIUDADES, WINDOW, UMBRAL_VERANO


def _max_racha(s: pd.Series) -> int:
    """Racha máxima de 1s consecutivos en una Serie binaria."""
    if not s.any():
        return 0
    run_id = (s != s.shift()).cumsum()
    return int(s.groupby(run_id).sum().max())


def _longitud_verano_anual(df_ciudad: pd.DataFrame,
                            umbral: float = UMBRAL_VERANO) -> pd.Series:
    """Para cada año, racha más larga de días consecutivos con Tmedia > umbral."""
    df = df_ciudad.sort_values("time")
    calido = (df["temperature_2m_mean"] > umbral).astype(int)
    return df.assign(calido=calido).groupby("año")["calido"].apply(_max_racha)


def _inicio_fin_verano_anual(df_ciudad: pd.DataFrame,
                              umbral: float = UMBRAL_VERANO) -> pd.DataFrame:
    """
    Para cada año detecta el primer y último día de la racha más larga
    con Tmedia > umbral. Devuelve DataFrame con inicio_doy, fin_doy, duracion.
    """
    df = df_ciudad.sort_values("time").reset_index(drop=True)
    calido = df["temperature_2m_mean"] > umbral

    if not calido.any():
        return pd.DataFrame()

    df["doy"]    = df["time"].dt.dayofyear
    run_id = (calido != calido.shift()).cumsum()

    warm = df[calido].copy()
    warm["run_id"] = run_id[calido].values

    runs = warm.groupby("run_id").agg(
        inicio_doy=("doy", "first"),
        fin_doy=("doy", "last"),
        duracion=("doy", "count"),
        año=("año", "first"),
    ).reset_index(drop=True)

    idx    = runs.groupby("año")["duracion"].idxmax()
    result = runs.loc[idx].set_index("año")
    return result[["inicio_doy", "fin_doy", "duracion"]]


def calcular_verano(ciudad, umbral: float = UMBRAL_VERANO) -> dict:
    serie  = _longitud_verano_anual(ciudad.df, umbral)
    años   = serie.index.tolist()
    dias   = serie.values

    mm      = np.convolve(dias, np.ones(WINDOW) / WINDOW, mode="valid")
    años_mm = años[WINDOW - 1:]

    slope, intercept, _, p_value, _ = linregress(np.array(años, dtype=float),
                                                  dias.astype(float))

    return {
        "ciudad":      ciudad,
        "años":        años,
        "dias":        dias.tolist(),
        "media_movil": mm.tolist(),
        "años_mm":     años_mm,
        "tendencia":   (slope * np.array(años) + intercept).tolist(),
        "slope":       slope,
        "p_value":     p_value,
        "umbral":      umbral,
    }


def calcular_inicio_fin_verano(ciudad, umbral: float = UMBRAL_VERANO) -> dict:
    """
    Inicio y fin del verano meteorológico por año con tendencias lineales.
    Permite distinguir si el verano se alarga por empezar antes, terminar más
    tarde, o ambas cosas a la vez.
    """
    df_if = _inicio_fin_verano_anual(ciudad.df, umbral)

    if df_if.empty:
        return {"ciudad": ciudad, "vacio": True}

    años    = np.array(df_if.index.tolist())
    inicios = df_if["inicio_doy"].values.astype(float)
    fines   = df_if["fin_doy"].values.astype(float)

    slope_ini, _, _, p_ini, _ = linregress(años, inicios)
    slope_fin, _, _, p_fin, _ = linregress(años, fines)

    return {
        "ciudad":       ciudad,
        "años":         años.tolist(),
        "inicios":      inicios.tolist(),
        "fines":        fines.tolist(),
        "slope_inicio": slope_ini * 10,
        "slope_fin":    slope_fin * 10,
        "p_inicio":     p_ini,
        "p_fin":        p_fin,
        "umbral":       umbral,
        "vacio":        False,
    }


def calcular_todos(ciudades=None) -> list[dict]:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return [calcular_verano(c) for c in ciudades]


def calcular_todos_inicio_fin(ciudades=None) -> list[dict]:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return [calcular_inicio_fin_verano(c) for c in ciudades]
