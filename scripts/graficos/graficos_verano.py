"""
Gráficos de longitud del verano meteorológico — refuerzo H5
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN, CIUDADES
from scripts.funciones_variables import estilo_ax

WINDOW = 10


def graficar_longitud_verano(resultados: list[dict]) -> None:
    """Longitud del verano por año con tendencia. Una figura por ciudad."""
    for r in resultados:
        ciudad = r["ciudad"]
        años   = r["años"]
        dias   = np.array(r["dias"])

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#F8F9FA")

        colors = ["#0D9488" if d <= 30 else "#F59E0B" if d <= 60 else "#EF4444"
                  for d in dias]
        ax.bar(años, dias, color=colors, alpha=0.75, width=0.8, zorder=2)

        ax.plot(r["años_mm"], r["media_movil"],
                color="#021B2E", linewidth=2.5,
                label=f"Media móvil {WINDOW} años", zorder=3)

        ax.plot(años, r["tendencia"],
                color="#475569", linewidth=1.8, linestyle="--",
                label=f"Tendencia ({r['slope'] * 10:+.1f} días/década)", zorder=3)

        estilo_ax(ax,
                  f"Longitud del verano meteorológico\n{ciudad.nombre.capitalize()} "
                  f"(días consecutivos con Tmedia > {r['umbral']:.0f}°C, {AÑO_INICIO}–{AÑO_FIN})",
                  "Año", "Días de verano meteorológico")
        ax.legend(fontsize=10)

        # Anotar máximo histórico
        idx_max = np.argmax(dias)
        ax.annotate(f"{int(dias[idx_max])} días",
                    xy=(años[idx_max], dias[idx_max]),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", fontsize=9, color="#EF4444", fontweight="bold")

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["estacionalidad"] / f"verano_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()


def graficar_verano_comparativa(resultados: list[dict]) -> None:
    """
    Media móvil de la longitud del verano para todas las ciudades.
    Permite ver si el verano se alarga más en el interior que en la costa.
    """
    fig, ax = plt.subplots(figsize=(15, 7))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    for r in resultados:
        ciudad = r["ciudad"]
        ax.plot(r["años"], r["dias"],
                color=ciudad.color, linewidth=1, alpha=0.25)
        ax.plot(r["años_mm"], r["media_movil"],
                color=ciudad.color, linewidth=2.2,
                label=f"{ciudad.nombre.capitalize()} ({r['slope'] * 10:+.1f} d/déc.)")

    estilo_ax(ax,
              f"Longitud del verano meteorológico por ciudad\n"
              f"(media móvil 10 años, Tmedia > {resultados[0]['umbral']:.0f}°C, {AÑO_INICIO}–{AÑO_FIN})",
              "Año", "Días de verano meteorológico")
    ax.legend(title="Ciudades (tendencia/década)", fontsize=10)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["estacionalidad"] / "verano_comparativa.png",
                dpi=180, bbox_inches="tight")
    plt.show()


def graficar_boxplot_verano_decadas(ciudades: list = None) -> None:
    """
    Distribución de la longitud del verano por décadas y ciudad.
    Seaborn: boxplot para ver cómo cambia la mediana y dispersión.
    """
    from scripts.analisis.verano_meteorologico import _longitud_verano_anual

    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    frames   = []
    for ciudad in ciudades:
        serie = _longitud_verano_anual(ciudad.df)
        tmp   = serie.reset_index()
        tmp.columns = ["año", "dias"]
        tmp["ciudad"] = ciudad.nombre.capitalize()
        tmp["decada"] = (tmp["año"] // 10 * 10).astype(str) + "s"
        frames.append(tmp)

    data   = pd.concat(frames, ignore_index=True)
    paleta = {c.nombre.capitalize(): c.color for c in ciudades}

    fig, ax = plt.subplots(figsize=(16, 7))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    sns.boxplot(
        data=data, x="decada", y="dias", hue="ciudad",
        palette=paleta, notch=False,
        linewidth=1.0, flierprops={"marker": ".", "alpha": 0.3},
        ax=ax,
    )

    ax.set_title(
        f"Distribución de la longitud del verano meteorológico por décadas\n({AÑO_INICIO}–{AÑO_FIN})",
        fontsize=14, fontweight="bold", color="#021B2E", pad=15,
    )
    ax.set_xlabel("Década", fontsize=11, color="#021B2E")
    ax.set_ylabel("Días de verano meteorológico", fontsize=11, color="#021B2E")
    ax.tick_params(colors="#475569")
    ax.grid(axis="y", color="#CBD5E1", linestyle="--", alpha=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Ciudad", fontsize=9, ncol=2)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["estacionalidad"] / "boxplot_verano_decadas.png",
                dpi=180, bbox_inches="tight")
    plt.show()
