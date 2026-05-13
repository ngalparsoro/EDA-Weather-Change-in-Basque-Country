"""
Análisis de correlación distancia al mar — métricas y regresiones
Devuelve DataFrames listos para graficar, sin ningún plt.
"""
import numpy as np
import pandas as pd
from scipy import stats
from scripts.variables import CIUDADES

PERIODOS = {
    "1940–1979": (1940, 1979),
    "1980–2009": (1980, 2009),
    "2010–2025": (2010, 2025),
}


def _metricas_anuales(ciudades) -> pd.DataFrame:
    """Construye DataFrame consolidado con métricas anuales por ciudad."""
    frames = []
    for ciudad in ciudades:
        df = ciudad.df.copy()
        df["ciudad"]   = ciudad.nombre
        df["dist_mar"] = ciudad.dist_mar
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)

    temp_anual = (
        data.groupby(["ciudad", "año", "dist_mar"])["temperature_2m_mean"]
        .mean().reset_index().rename(columns={"temperature_2m_mean": "temp_media"})
    )
    dias_30 = (
        data[data["temperature_2m_max"] > 30]
        .groupby(["ciudad", "año"]).size().reset_index(name="dias_30")
    )
    dias_35 = (
        data[data["temperature_2m_max"] > 35]
        .groupby(["ciudad", "año"]).size().reset_index(name="dias_35")
    )
    metricas = (
        temp_anual
        .merge(dias_30, on=["ciudad", "año"], how="left")
        .merge(dias_35, on=["ciudad", "año"], how="left")
        .fillna({"dias_30": 0, "dias_35": 0})
    )
    return metricas


def calcular_resumen_periodos(ciudades=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Devuelve (resumen_por_periodo, variabilidad_interanual).
    """
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    metricas = _metricas_anuales(ciudades)

    variab = (
        metricas.groupby(["ciudad", "dist_mar"])["temp_media"]
        .std().reset_index().rename(columns={"temp_media": "variabilidad"})
    )

    rows = []
    for periodo, (p_ini, p_fin) in PERIODOS.items():
        sub = metricas[metricas["año"].between(p_ini, p_fin)]
        agg = sub.groupby(["ciudad", "dist_mar"]).agg(
            temp_media=("temp_media", "mean"),
            dias_30=("dias_30", "mean"),
            dias_35=("dias_35", "mean"),
        ).reset_index()
        agg["periodo"] = periodo
        rows.append(agg)

    resumen = pd.concat(rows, ignore_index=True).merge(variab, on=["ciudad", "dist_mar"])
    return resumen, variab


def calcular_gradiente_decadas(ciudades=None) -> pd.DataFrame:
    """
    Gradiente térmico mar–interior (°C / 10 km) por décadas.
    """
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    metricas = _metricas_anuales(ciudades)

    rows = []
    for dec in range(1940, 2026, 10):
        sub = metricas[metricas["año"].between(dec, dec + 9)]
        med = sub.groupby(["ciudad", "dist_mar"])["temp_media"].mean().reset_index()
        if len(med) >= 4:
            s, i, r, p, _ = stats.linregress(med["dist_mar"], med["temp_media"])
            rows.append({"decada": f"{dec}s", "slope_10km": s * 10, "r": r, "p": p})

    return pd.DataFrame(rows)


def calcular_regresion(x, y) -> dict:
    """Regresión lineal + IC 95% sobre arrays x, y."""
    x, y = np.array(x, dtype=float), np.array(y, dtype=float)
    slope, intercept, r, p, _ = stats.linregress(x, y)
    x_line = np.linspace(x.min() - 3, x.max() + 8, 200)
    y_line = slope * x_line + intercept

    n  = len(x)
    se = np.sqrt(np.sum((y - (slope * x + intercept))**2) / (n - 2))
    t  = stats.t.ppf(0.975, df=n - 2)
    ci = t * se * np.sqrt(1/n + (x_line - x.mean())**2 / np.sum((x - x.mean())**2))

    return {
        "x": x, "y": y,
        "x_line": x_line, "y_line": y_line,
        "ci": ci,
        "r": r, "p": p, "slope": slope, "intercept": intercept,
    }


def calcular_todos(ciudades=None) -> dict:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    resumen, variab = calcular_resumen_periodos(ciudades)
    gradiente       = calcular_gradiente_decadas(ciudades)
    return {
        "resumen":   resumen,
        "variab":    variab,
        "gradiente": gradiente,
        "ciudades":  ciudades,
        "periodos":  PERIODOS,
    }
