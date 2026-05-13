from pathlib import Path
import matplotlib.ticker as ticker
from scripts.variables import CIUDADES


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
    ax.set_facecolor("#F8F9FA")
    ax.set_title(titulo, fontsize=14, fontweight="bold", color="#021B2E", pad=15)
    ax.set_xlabel(xlabel, fontsize=11, color="#021B2E")
    ax.set_ylabel(ylabel, fontsize=11, color="#021B2E")
    ax.tick_params(colors="#475569")
    if x_multiple:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(x_multiple))
    ax.grid(axis="y", color="#CBD5E1", linestyle="--", alpha=0.6, zorder=1)
    ax.spines[["top", "right"]].set_visible(False)
