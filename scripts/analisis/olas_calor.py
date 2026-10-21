"""
Detección y duración de olas de calor
Refuerzo de H4 — Frecuencia de temperaturas extremas

Dos definiciones disponibles:
  - Absoluta: ≥ 3 días consecutivos con Tmax > 35°C (comparable entre ciudades)
  - Relativa:  ≥ 3 días consecutivos con Tmax > percentil 95 local (captura
               también olas en ciudades costeras donde 35°C es rarísimo)
"""
import pandas as pd
from scripts.variables import CIUDADES


def _detectar_olas(df_ciudad: pd.DataFrame,
                   umbral: float = 35.0,
                   min_dias: int = 3) -> pd.DataFrame:
    """
    Devuelve un DataFrame con cada ola de calor detectada:
    año, fecha_inicio, fecha_fin, duración (días).
    Implementación vectorizada con el truco cumsum para detectar rachas.
    """
    df = df_ciudad.sort_values("time")[["time", "temperature_2m_max"]].reset_index(drop=True)
    extremo = df["temperature_2m_max"] > umbral

    if not extremo.any():
        return pd.DataFrame(columns=["año", "fecha_inicio", "fecha_fin", "duracion"])

    run_id = (extremo != extremo.shift()).cumsum()
    hot = df[extremo].copy()
    hot["run_id"] = run_id[extremo].values

    olas = hot.groupby("run_id").agg(
        fecha_inicio=("time", "first"),
        fecha_fin=("time", "last"),
        duracion=("time", "count"),
    ).reset_index(drop=True)

    olas = olas[olas["duracion"] >= min_dias].copy()
    if olas.empty:
        return pd.DataFrame(columns=["año", "fecha_inicio", "fecha_fin", "duracion"])

    olas["año"] = olas["fecha_inicio"].dt.year
    return olas[["año", "fecha_inicio", "fecha_fin", "duracion"]]


def calcular_olas_calor(ciudad,
                         umbral: float = 35.0,
                         min_dias: int = 3) -> dict:
    olas = _detectar_olas(ciudad.df, umbral, min_dias)

    if olas.empty:
        return {
            "ciudad":          ciudad,
            "olas":            olas,
            "num_olas_anual":  pd.Series(dtype=float),
            "duracion_max":    pd.Series(dtype=float),
            "duracion_total":  pd.Series(dtype=float),
            "umbral":          umbral,
            "min_dias":        min_dias,
        }

    num_olas_anual = olas.groupby("año").size()
    duracion_max   = olas.groupby("año")["duracion"].max()
    duracion_total = olas.groupby("año")["duracion"].sum()

    idx = range(ciudad.df["año"].min(), ciudad.df["año"].max() + 1)
    num_olas_anual = num_olas_anual.reindex(idx, fill_value=0)
    duracion_max   = duracion_max.reindex(idx, fill_value=0)
    duracion_total = duracion_total.reindex(idx, fill_value=0)

    return {
        "ciudad":         ciudad,
        "olas":           olas,
        "num_olas_anual": num_olas_anual,
        "duracion_max":   duracion_max,
        "duracion_total": duracion_total,
        "umbral":         umbral,
        "min_dias":       min_dias,
    }


def calcular_olas_p95(ciudad, min_dias: int = 3) -> dict:
    """
    Olas de calor con umbral relativo: percentil 95 de Tmax de cada ciudad.
    Permite detectar episodios extremos también en ciudades costeras donde
    35°C es casi imposible.
    """
    umbral = ciudad.df["temperature_2m_max"].quantile(0.95)
    result = calcular_olas_calor(ciudad, umbral=umbral, min_dias=min_dias)
    result["umbral_tipo"]  = "p95"
    result["umbral_valor"] = round(umbral, 1)
    return result


def calcular_todos(ciudades=None, umbral: float = 35.0, min_dias: int = 3) -> list[dict]:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return [calcular_olas_calor(c, umbral, min_dias) for c in ciudades]


def calcular_todos_p95(ciudades=None, min_dias: int = 3) -> list[dict]:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return [calcular_olas_p95(c, min_dias) for c in ciudades]
