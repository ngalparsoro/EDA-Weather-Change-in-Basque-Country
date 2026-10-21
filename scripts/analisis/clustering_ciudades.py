"""
Clustering jerárquico de ciudades por perfil climático completo
Refuerzo de H3 — Diferencias entre ciudades
"""
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.stats import linregress
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scripts.variables import CIUDADES
from scripts.analisis.racha_seca import _racha_seca_anual


def calcular_perfil_climatico(ciudades=None) -> pd.DataFrame:
    """
    Construye un perfil climático por ciudad con las siguientes features:
    temperatura, precipitación, extremos, racha seca, variabilidad y tendencia.
    """
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    filas    = []

    for ciudad in ciudades:
        df = ciudad.df
        idx_años = range(df["año"].min(), df["año"].max() + 1)

        # Un solo groupby para todas las columnas de temperatura y precipitación
        anual = df.groupby("año").agg(
            temp_media=("temperature_2m_mean", "mean"),
            temp_max=("temperature_2m_max", "mean"),
            temp_min=("temperature_2m_min", "mean"),
            precip_sum=("precipitation_sum", "sum"),
        )

        dias_30       = (df[df["temperature_2m_max"] > 30].groupby("año").size()
                         .reindex(idx_años, fill_value=0))
        dias_35       = (df[df["temperature_2m_max"] > 35].groupby("año").size()
                         .reindex(idx_años, fill_value=0))
        dias_intensos = (df[df["precipitation_sum"] > 30].groupby("año").size()
                         .reindex(idx_años, fill_value=0))

        amplitud   = (df["temperature_2m_max"] - df["temperature_2m_min"]).mean()
        racha_seca = _racha_seca_anual(df).mean()
        años_arr   = anual.index.to_numpy()
        slope_temp, _, _, _, _ = linregress(años_arr, anual["temp_media"].values)

        filas.append({
            "ciudad":        ciudad.nombre,
            "color":         ciudad.color,
            "dist_mar":      ciudad.dist_mar,
            "altitud":       ciudad.altitud,
            "temp_media":    float(anual["temp_media"].mean()),
            "temp_max":      float(anual["temp_max"].mean()),
            "temp_min":      float(anual["temp_min"].mean()),
            "amplitud":      float(amplitud),
            "precip_anual":  float(anual["precip_sum"].mean()),
            "dias_30":       float(dias_30.mean()),
            "dias_35":       float(dias_35.mean()),
            "dias_intensos": float(dias_intensos.mean()),
            "racha_seca":    float(racha_seca),
            "variab_temp":   float(anual["temp_media"].std()),
            "trend_calent":  slope_temp * 10,
        })

    return pd.DataFrame(filas)


def calcular_clustering(ciudades=None) -> dict:
    """
    Clustering jerárquico (Ward) sobre el perfil climático estandarizado.
    Incluye PCA para identificar qué variables explican la varianza entre ciudades.
    """
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    perfil   = calcular_perfil_climatico(ciudades)

    features = ["temp_media", "temp_max", "temp_min", "amplitud",
                "precip_anual", "dias_30", "dias_35", "dias_intensos",
                "racha_seca", "variab_temp", "trend_calent", "altitud"]

    X        = perfil[features].values
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    Z      = linkage(X_scaled, method="ward", metric="euclidean")
    grupos = fcluster(Z, t=3, criterion="maxclust")
    perfil["grupo"] = grupos

    # PCA sobre las mismas variables estandarizadas
    pca       = PCA(n_components=2)
    X_pca     = pca.fit_transform(X_scaled)
    loadings  = pd.DataFrame(
        pca.components_.T,
        index=features,
        columns=["PC1", "PC2"],
    )
    explained = pca.explained_variance_ratio_

    return {
        "perfil":        perfil,
        "linkage":       Z,
        "features":      features,
        "ciudades":      ciudades,
        "X_scaled":      X_scaled,
        "grupos":        grupos,
        "X_pca":         X_pca,
        "loadings":      loadings,
        "explained":     explained,
    }


def calcular_todos(ciudades=None) -> dict:
    return calcular_clustering(ciudades)
