"""
Gráficos de racha seca máxima anual — refuerzo H2
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN, CIUDADES
from scripts.funciones_variables import estilo_ax


def graficar_racha_seca(resultados: list[dict]) -> None:
    """Racha seca máxima por año con tendencia lineal. Una figura por ciudad."""
    for r in resultados:
        ciudad = r["ciudad"]
        años   = r["años"]
        rachas = np.array(r["rachas"])

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#F8F9FA")

        colors = ["#F59E0B" if d <= 20 else "#EF4444" if d <= 35 else "#7F1D1D"
                  for d in rachas]
        ax.bar(años, rachas, color=colors, alpha=0.75, width=0.8, zorder=2)

        ax.plot(r["años_mm"], r["media_movil"],
                color="#1E3A8A", linewidth=2.5,
                label="Media móvil 10 años", zorder=3)

        ax.plot(años, r["tendencia"],
                color="#021B2E", linewidth=1.8, linestyle="--",
                label=f"Tendencia ({r['slope'] * 10:+.1f} días/década)", zorder=3)

        estilo_ax(ax,
                  f"Racha seca máxima anual\n{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
                  "Año", f"Días consecutivos sin lluvia (< {r['umbral']} mm)")
        ax.legend(fontsize=10)

        # Anotar rachas extremas (> percentil 90)
        umbral_anot = np.percentile(rachas, 90)
        for año, d in zip(años, rachas):
            if d > umbral_anot:
                ax.annotate(f"{int(d)}", xy=(año, d), xytext=(0, 5),
                            textcoords="offset points", ha="center",
                            fontsize=9, color="#7F1D1D", fontweight="bold")

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["precipitacion"] / f"racha_seca_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()


def graficar_racha_comparativa(resultados: list[dict]) -> None:
    """
    Comparativa de racha seca entre ciudades (media móvil).
    Permite ver si el interior se seca más que la costa.
    """
    fig, ax = plt.subplots(figsize=(15, 7))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    for r in resultados:
        ciudad = r["ciudad"]
        ax.plot(r["años"], r["rachas"],
                color=ciudad.color, linewidth=1, alpha=0.3)
        ax.plot(r["años_mm"], r["media_movil"],
                color=ciudad.color, linewidth=2.2,
                label=ciudad.nombre.capitalize())

    estilo_ax(ax,
              f"Racha seca máxima anual por ciudad\n(media móvil 10 años, {AÑO_INICIO}–{AÑO_FIN})",
              "Año", "Días consecutivos sin lluvia")
    ax.legend(title="Ciudades", fontsize=10)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["precipitacion"] / "racha_seca_comparativa.png",
                dpi=180, bbox_inches="tight")
    plt.show()


def graficar_violin_rachas_decadas(ciudades: list = None) -> None:
    """
    Distribución de la racha seca máxima por décadas para todas las ciudades.
    Seaborn: violinplot permite ver cómo cambia la distribución, no solo la media.
    """
    import pandas as pd
    from scripts.analisis.racha_seca import _racha_seca_anual

    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    frames   = []
    for ciudad in ciudades:
        serie = _racha_seca_anual(ciudad.df)
        tmp   = serie.reset_index()
        tmp.columns = ["año", "racha"]
        tmp["ciudad"] = ciudad.nombre.capitalize()
        tmp["decada"] = (tmp["año"] // 10 * 10).astype(str) + "s"
        frames.append(tmp)

    data   = pd.concat(frames, ignore_index=True)
    paleta = {c.nombre.capitalize(): c.color for c in ciudades}

    fig, ax = plt.subplots(figsize=(16, 7))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    sns.violinplot(
        data=data, x="decada", y="racha", hue="ciudad",
        palette=paleta, inner="quartile",
        linewidth=1.0, ax=ax,
    )

    ax.set_title(
        f"Distribución de la racha seca máxima por décadas\n({AÑO_INICIO}–{AÑO_FIN})",
        fontsize=14, fontweight="bold", color="#021B2E", pad=15,
    )
    ax.set_xlabel("Década", fontsize=11, color="#021B2E")
    ax.set_ylabel("Días consecutivos sin lluvia", fontsize=11, color="#021B2E")
    ax.tick_params(colors="#475569")
    ax.grid(axis="y", color="#CBD5E1", linestyle="--", alpha=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Ciudad", fontsize=9, ncol=2)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["precipitacion"] / "violin_rachas_decadas.png",
                dpi=180, bbox_inches="tight")
    plt.show()
