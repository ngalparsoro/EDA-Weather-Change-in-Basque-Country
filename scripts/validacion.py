"""
Validación de datos antes del pipeline de análisis.
Llama a validar_datos() en regenerar_graficos.py tras cargar_datos().
"""
import pandas as pd
from scripts.variables import CIUDADES

COLUMNAS_REQUERIDAS = [
    "time",
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "wind_speed_10m_max",
]
MAX_NAN_PCT = 5.0   # % de NaN aceptable por columna


def validar_datos(ciudades=None, verbose: bool = True) -> list[str]:
    """
    Verifica columnas, rango de fechas y NaN para cada ciudad cargada.
    Devuelve lista de warnings (vacía si todo está OK).
    Imprime un resumen si verbose=True.
    """
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    warnings = []

    for ciudad in ciudades:
        df = ciudad.df
        tag = ciudad.nombre

        # Columnas requeridas
        faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
        if faltantes:
            warnings.append(f"[{tag}] Columnas faltantes: {faltantes}")

        # Rango de fechas
        if "time" in df.columns:
            año_min = df["time"].dt.year.min()
            año_max = df["time"].dt.year.max()
            if año_min > 1945:
                warnings.append(f"[{tag}] Serie empieza en {año_min}, esperado ≤ 1945")
            if año_max < 2020:
                warnings.append(f"[{tag}] Serie termina en {año_max}, esperado ≥ 2020")

        # NaN por columna
        for col in COLUMNAS_REQUERIDAS:
            if col not in df.columns:
                continue
            pct = df[col].isna().mean() * 100
            if pct > MAX_NAN_PCT:
                warnings.append(
                    f"[{tag}] {col}: {pct:.1f}% NaN (máx. permitido {MAX_NAN_PCT}%)"
                )

        # Fechas duplicadas
        dupes = df["time"].duplicated().sum() if "time" in df.columns else 0
        if dupes > 0:
            warnings.append(f"[{tag}] {dupes} fechas duplicadas")

    if verbose:
        if warnings:
            print("⚠️  Advertencias de validación:")
            for w in warnings:
                print(f"   {w}")
        else:
            print("✅ Validación OK — todos los datasets pasan los checks")
        print()

    return warnings
