from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scripts.variables import CIUDADES

mpl.rcParams.update({
    "figure.facecolor":   "#0E0E0E",
    "axes.facecolor":     "#0E0E0E",
    "savefig.facecolor":  "#0E0E0E",
    "text.color":         "#C8C8C8",
    "axes.labelcolor":    "#909090",
    "xtick.color":        "#686868",
    "ytick.color":        "#686868",
    "axes.edgecolor":     "#2A2A2A",
    "grid.color":         "#242424",
    "legend.facecolor":   "#141414",
    "legend.edgecolor":   "#303030",
    "legend.labelcolor":  "#C8C8C8",
})


def media_movil(valores, window: int = 10) -> np.ndarray:
    return np.convolve(np.array(valores), np.ones(window) / window, mode="valid")


def guardar_grafico(ruta, dpi: int = 180) -> None:
    plt.tight_layout()
    plt.savefig(ruta, dpi=dpi, bbox_inches="tight", facecolor="#0E0E0E")
    plt.show()


def cargar_datos(data_dir: Path = Path("data")) -> None:
    """Carga el CSV de cada ciudad y puebla ciudad.df."""
    print("📂 Cargando datos...")
    for ciudad in CIUDADES:
        try:
            ciudad.cargar(data_dir)
            print(f"  ✅ {ciudad.nombre}: {len(ciudad.df):,} filas")
        except FileNotFoundError:
            print(f"  ⚠️  {ciudad.nombre}: archivo no encontrado — se omite")
    print()


def estilo_ax(ax, titulo: str, xlabel: str, ylabel: str,
              x_multiple: int | None = 10) -> None:
    """Aplica el estilo visual estándar a un eje de matplotlib."""
    ax.set_facecolor("#0E0E0E")
    ax.set_title(titulo, fontsize=14, fontweight="bold", color="#DEDEDE", pad=15)
    ax.set_xlabel(xlabel, fontsize=11, color="#909090")
    ax.set_ylabel(ylabel, fontsize=11, color="#909090")
    ax.tick_params(colors="#686868")
    if x_multiple:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(x_multiple))
    ax.grid(axis="y", color="#242424", linestyle="--", alpha=1.0, zorder=1)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["bottom", "left"]].set_color("#2A2A2A")
