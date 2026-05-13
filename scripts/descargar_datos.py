"""
Descarga de datos históricos del clima — Euskal Herria
Fuente: Open-Meteo / ERA5, sin API key

Instalación:
    pip install requests pandas tqdm
"""
import requests
import pandas as pd
import time
from tqdm import tqdm
from pathlib import Path
from scripts.variables import CIUDADES, AÑO_INICIO, AÑO_FIN

# ── Configuración ──────────────────────────────────────────────────────────────
VARIABLES      = "temperature_2m_mean,temperature_2m_min,temperature_2m_max,precipitation_sum,wind_speed_10m_max"
BLOQUE         = 10   # años por petición
PAUSA          = 3    # segundos entre peticiones
MAX_REINTENTOS = 5


def _descargar_ciudad(ciudad, data_dir: Path) -> pd.DataFrame | None:
    """Descarga los datos de una ciudad y los guarda en CSV."""
    url    = "https://archive-api.open-meteo.com/v1/archive"
    frames = []

    for inicio in tqdm(range(AÑO_INICIO, AÑO_FIN + 1, BLOQUE),
                       desc=f"  {ciudad.nombre}", leave=False):
        fin    = min(inicio + BLOQUE - 1, AÑO_FIN)
        params = {
            "latitude":   ciudad.lat,
            "longitude":  ciudad.lon,
            "start_date": f"{inicio}-01-01",
            "end_date":   f"{fin}-12-31",
            "daily":      VARIABLES,
            "timezone":   "Europe/Madrid",
        }

        espera = PAUSA
        for intento in range(MAX_REINTENTOS):
            try:
                r = requests.get(url, params=params, timeout=30)

                if r.status_code == 429:
                    print(f"\n    429 en {ciudad.nombre} {inicio}-{fin} — esperando {espera:.0f}s...")
                    time.sleep(espera)
                    espera *= 2
                    continue

                r.raise_for_status()
                df_bloque = pd.DataFrame(r.json()["daily"])
                df_bloque["time"] = pd.to_datetime(df_bloque["time"])
                frames.append(df_bloque)
                time.sleep(PAUSA)
                break

            except requests.exceptions.HTTPError as e:
                if intento == MAX_REINTENTOS - 1:
                    print(f"\n    Error tras {MAX_REINTENTOS} intentos en {ciudad.nombre} {inicio}-{fin}: {e}")
                else:
                    time.sleep(espera)
                    espera *= 2

            except Exception as e:
                print(f"\n    Error inesperado en {ciudad.nombre} {inicio}-{fin}: {e}")
                time.sleep(espera)
                espera *= 2

    if not frames:
        print(f"  ⚠️  No se pudieron descargar datos para {ciudad.nombre}")
        return None

    df = pd.concat(frames, ignore_index=True)
    df["año"] = df["time"].dt.year
    df["mes"] = df["time"].dt.month
    ciudad.df = df
    ciudad.guardar(data_dir)
    return df


def descargar_datos(data_dir: Path = Path("data")) -> None:
    """Descarga los datos de todas las ciudades y los guarda en CSV."""
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"Descargando datos {AÑO_INICIO}–{AÑO_FIN} para {len(CIUDADES)} ciudades")
    print(f"Pausa entre peticiones: {PAUSA}s  |  Reintentos máx: {MAX_REINTENTOS}\n")

    guardados = []
    for ciudad in CIUDADES:
        print(f"\n→ {ciudad.nombre}")
        df = _descargar_ciudad(ciudad, data_dir)
        if df is not None:
            nombre_csv = f"clima_{ciudad.nombre}.csv"
            guardados.append(nombre_csv)
            print(f"  ✅ Guardado: {nombre_csv}  ({len(df):,} filas)")

    print("\n" + "=" * 45)
    print(f"DESCARGA COMPLETADA — {len(guardados)} archivos generados")
    for f in guardados:
        print(f"  {f}")
