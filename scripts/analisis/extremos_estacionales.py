"""
Concentración estacional de extremos — ¿en qué mes se acumulan los días extremos?
Enriquece H4: no solo cuántos días extremos hay, sino cuándo dentro del año.
"""
import numpy as np
import pandas as pd
from scripts.variables import CIUDADES, UMBRAL_CALOR


def calcular_concentracion_mensual(ciudad,
                                    umbral: float = UMBRAL_CALOR) -> dict:
    """
    Para cada quinquenio, cuenta cuántos días extremos (Tmax > umbral) caen
    en cada mes. Devuelve un pivot DataFrame: quinquenio (fila) × mes (columna).
    """
    df = ciudad.df.copy()
    df = df[df["temperature_2m_max"] > umbral].copy()

    if df.empty:
        return {"ciudad": ciudad, "pivot": pd.DataFrame(), "umbral": umbral}

    año_min = int(ciudad.df["año"].min())
    año_max = int(ciudad.df["año"].max())

    # Asignar quinquenio
    df["quinquenio"] = (df["año"] // 5 * 5).astype(str) + "–" + \
                       ((df["año"] // 5 * 5) + 4).astype(str)

    # Contar días extremos por quinquenio y mes
    conteo = df.groupby(["quinquenio", "mes"]).size().reset_index(name="dias")

    pivot = conteo.pivot(index="quinquenio", columns="mes", values="dias").fillna(0)
    pivot.columns = ["Ene","Feb","Mar","Abr","May","Jun",
                     "Jul","Ago","Sep","Oct","Nov","Dic"][: len(pivot.columns)]

    # Ordenar quinquenios cronológicamente
    pivot = pivot.sort_index()

    return {
        "ciudad": ciudad,
        "pivot":  pivot,
        "umbral": umbral,
    }


def calcular_todos(ciudades=None, umbral: float = UMBRAL_CALOR) -> list[dict]:
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    return [calcular_concentracion_mensual(c, umbral) for c in ciudades]
