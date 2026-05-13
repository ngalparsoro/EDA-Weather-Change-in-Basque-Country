"""
Clustering jerárquico de ciudades por perfil climático completo
Refuerzo de H3 — Diferencias entre ciudades
"""
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import pdist
from sklearn.preprocessing import StandardScaler
from scripts.variables import CIUDADES


def calcular_perfil_climatico(ciudades=None) -> pd.DataFrame:
    """
    Construye un perfil climático por ciudad con las siguientes features:
    - Temperatura media anual
    - Temperatura máxima media
    - Temperatura mínima media
    - Amplitud térmica media (Tmax - Tmin)
    - Precipitación total anual media
    - Días con Tmax > 30°C (media anual)
    - Días con Tmax > 35°C (media anual)
    - Días con precipitación > 30 mm (media anual)
    - Racha seca máxima media
    - Variabilidad interanual de temperatura (desv. estándar)
    """
    from scripts.analisis.racha_seca import _racha_seca_anual

    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    filas    = []

    for ciudad in ciudades:
        df = ciudad.df

        temp_media    = df.groupby("año")["temperature_2m_mean"].mean().mean()
        temp_max      = df.groupby("año")["temperature_2m_max"].mean().mean()
        temp_min      = df.groupby("año")["temperature_2m_min"].mean().mean()
        amplitud      = (df["temperature_2m_max"] - df["temperature_2m_min"]).mean()
        precip_anual  = df.groupby("año")["precipitation_sum"].sum().mean()
        dias_30       = df[df["temperature_2m_max"] > 30].groupby("año").size().mean()
        dias_35       = df[df["temperature_2m_max"] > 35].groupby("año").size().reindex(
                            range(df["año"].min(), df["año"].max() + 1), fill_value=0).mean()
        dias_intensos = df[df["precipitation_sum"] > 30].groupby("año").size().mean()
        racha_seca    = _racha_seca_anual(df).mean()
        variab_temp   = df.groupby("año")["temperature_2m_mean"].mean().std()

        filas.append({
            "ciudad":        ciudad.nombre,
            "color":         ciudad.color,
            "dist_mar":      ciudad.dist_mar,
            "temp_media":    temp_media,
            "temp_max":      temp_max,
            "temp_min":      temp_min,
            "amplitud":      amplitud,
            "precip_anual":  precip_anual,
            "dias_30":       dias_30,
            "dias_35":       dias_35,
            "dias_intensos": dias_intensos,
            "racha_seca":    racha_seca,
            "variab_temp":   variab_temp,
        })

    return pd.DataFrame(filas)


def calcular_clustering(ciudades=None) -> dict:
    """
    Clustering jerárquico (Ward) sobre el perfil climático estandarizado.
    Devuelve la matriz de linkage, el perfil y los grupos asignados.
    """
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    perfil   = calcular_perfil_climatico(ciudades)

    features = ["temp_media", "temp_max", "temp_min", "amplitud",
                "precip_anual", "dias_30", "dias_35", "dias_intensos",
                "racha_seca", "variab_temp"]

    X       = perfil[features].values
    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    Z      = linkage(X_scaled, method="ward", metric="euclidean")
    grupos = fcluster(Z, t=3, criterion="maxclust")  # 3 grupos por defecto

    perfil["grupo"] = grupos

    return {
        "perfil":    perfil,
        "linkage":   Z,
        "features":  features,
        "ciudades":  ciudades,
        "X_scaled":  X_scaled,
        "grupos":    grupos,
    }


def calcular_todos(ciudades=None) -> dict:
    return calcular_clustering(ciudades)
