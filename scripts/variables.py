import pandas as pd
from pathlib import Path
import math

# ── Rango temporal ─────────────────────────────────────────────────────────────
AÑO_INICIO = 1940
AÑO_FIN    = 2025

# ── Costa Cantábrica/Atlántica ─────────────────────────────────────────────────
_COSTA = [
    (43.372, -3.170), (43.385, -3.000), (43.363, -2.937),
    (43.373, -2.800), (43.370, -2.700), (43.367, -2.600),
    (43.373, -2.400), (43.320, -2.200), (43.310, -2.050),
    (43.318, -1.981), (43.356, -1.800), (43.390, -1.650),
    (43.420, -1.550), (43.480, -1.480), (43.510, -1.400),
    (43.530, -1.300), (43.520, -1.200), (43.480, -1.100),
    (43.450, -0.900),
]

def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Clase Ciudad ───────────────────────────────────────────────────────────────
class Ciudad:
    def __init__(self, nombre: str, lat: float, lon: float, color: str):
        self.nombre   = nombre
        self.lat      = lat
        self.lon      = lon
        self.color    = color
        self.dist_mar = round(min(_haversine(lat, lon, c[0], c[1]) for c in _COSTA), 1)
        self.df: pd.DataFrame | None = None

    def cargar(self, data_dir: Path = Path("data")) -> pd.DataFrame:
        path = data_dir / f"clima_{self.nombre.lower()}.csv"
        self.df = pd.read_csv(path, parse_dates=["time"])
        self.df["año"] = self.df["time"].dt.year
        self.df["mes"] = self.df["time"].dt.month
        return self.df

    def guardar(self, data_dir: Path = Path("data")) -> None:
        if self.df is None:
            raise ValueError(f"{self.nombre}: no hay datos que guardar")
        path = data_dir / f"clima_{self.nombre.lower()}.csv"
        self.df.to_csv(path, index=False, encoding="utf-8")

    def __repr__(self):
        cargado = f"{len(self.df):,} filas" if self.df is not None else "sin cargar"
        return f"Ciudad({self.nombre}, {self.lat}, {self.lon}, {self.dist_mar} km mar, {cargado})"


# ── Instancias ─────────────────────────────────────────────────────────────────
CIUDADES = [
    Ciudad("bilbo",     43.263, -2.935, "#10B981"),
    Ciudad("donostia",  43.318, -1.981, "#0EA5E9"),
    Ciudad("gasteiz",   42.846, -2.672, "#EF4444"),
    Ciudad("iruna",     42.812, -1.645, "#F59E0B"),
    Ciudad("baiona",    43.493, -1.474, "#6366F1"),
    Ciudad("arrasate",  43.079, -2.490, "#8B5CF6"),
    Ciudad("maule",     43.224, -0.887, "#EC4899"),
]

# ── Directorios de output ──────────────────────────────────────────────────────
OUTPUT_DIRS = {
    "temp_30":         Path("img/temp_30"),
    "temp_media":      Path("img/temp_media"),
    "precipitacion":   Path("img/precipitacion"),
    "comp_ciudades":   Path("img/comp_ciudades"),
    "extremos_35":     Path("img/extremos_35"),
    "estacionalidad":  Path("img/estacionalidad"),
    "correlacion_mar": Path("img/correlacion_mar"),
}

def crear_dirs():
    for d in OUTPUT_DIRS.values():
        d.mkdir(parents=True, exist_ok=True)
