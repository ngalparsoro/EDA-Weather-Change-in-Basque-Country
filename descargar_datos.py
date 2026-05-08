# ============================================================
# Descarga de datos históricos del clima — Euskal Herria
# Genera un CSV por ciudad en la carpeta actual
# Fuente: Open-Meteo / ERA5 (1940–2024), sin API key
# ============================================================
#
# Instalación:
#   pip install requests pandas tqdm
#
# Tiempo estimado: ~5-8 minutos (pausa entre peticiones)
# ============================================================

import requests
import pandas as pd
import time
from tqdm import tqdm
from variables import CIUDADES

# ============================================================
# CONFIGURACIÓN
# ============================================================

START_YEAR = 1940
END_YEAR   = 2024

VARIABLES  = "temperature_2m_mean,temperature_2m_min,temperature_2m_max,precipitation_sum"
BLOQUE     = 10    # años por petición
PAUSA      = 3   # segundos entre peticiones (evita 429)
MAX_REINTENTOS = 5

# ============================================================
# FUNCIÓN DE DESCARGA
# ============================================================

def descargar_ciudad(nombre, lat, lon):
    url = "https://archive-api.open-meteo.com/v1/archive"
    frames = []

    bloques = list(range(START_YEAR, END_YEAR + 1, BLOQUE))
    for inicio in tqdm(bloques, desc=f"  {nombre}", leave=False):
        fin = min(inicio + BLOQUE - 1, END_YEAR)
        params = {
            "latitude":   lat,
            "longitude":  lon,
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
                    # Rate limit: espera exponencial
                    print(f"\n    429 en {nombre} {inicio}-{fin} — esperando {espera:.0f}s...")
                    time.sleep(espera)
                    espera *= 2   # duplica la espera en cada reintento
                    continue

                r.raise_for_status()
                datos = r.json()["daily"]
                df_bloque = pd.DataFrame(datos)
                df_bloque["time"] = pd.to_datetime(df_bloque["time"])
                frames.append(df_bloque)
                time.sleep(PAUSA)  # pausa cortés entre peticiones exitosas
                break

            except requests.exceptions.HTTPError as e:
                if intento == MAX_REINTENTOS - 1:
                    print(f"\n    Error tras {MAX_REINTENTOS} intentos en {nombre} {inicio}-{fin}: {e}")
                else:
                    time.sleep(espera)
                    espera *= 2

            except Exception as e:
                print(f"\n    Error inesperado en {nombre} {inicio}-{fin}: {e}")
                time.sleep(espera)
                espera *= 2

    if not frames:
        print(f"  No se pudieron descargar datos para {nombre}")
        return None

    df = pd.concat(frames, ignore_index=True)
    df["ciudad"] = nombre
    df["año"]    = df["time"].dt.year
    df["mes"]    = df["time"].dt.month
    return df


# ============================================================
# DESCARGA Y GUARDADO
# ============================================================

print(f"Descargando datos {START_YEAR}–{END_YEAR} para {len(CIUDADES)} ciudades")
print(f"Pausa entre peticiones: {PAUSA}s  |  Reintentos máx: {MAX_REINTENTOS}\n")

archivos_guardados = []

for nombre, coords in CIUDADES.items():
    print(f"\n→ {nombre}")
    df_ciudad = descargar_ciudad(nombre, coords["lat"], coords["lon"])

    if df_ciudad is not None:
        nombre_archivo = f"clima_{nombre.lower().replace('ñ','n').replace('ï','i')}.csv"
        df_ciudad.to_csv(f'data/{nombre_archivo}', index=False, encoding="utf-8")
        archivos_guardados.append(nombre_archivo)
        print(f"  Guardado: {nombre_archivo}  ({len(df_ciudad):,} filas)")

print("\n" + "="*45)
print("DESCARGA COMPLETADA")
print("="*45)
print(f"Archivos generados ({len(archivos_guardados)}):")
for f in archivos_guardados:
    print(f"  {f}")

# Created by DeepSeek - https://deepseek.com
