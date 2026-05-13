"""
Gráficos de precipitaciones — H2
Recibe los dicts calculados por analisis/precipitaciones.py
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN
from scripts.funciones_variables import estilo_ax

WINDOW = 10


def _media_movil(valores, window=WINDOW):
    return np.convolve(np.array(valores), np.ones(window) / window, mode="valid")


# ── H2: Precipitación total anual ─────────────────────────────────────────────
def graficar_precipitacion_anual(resultados: list[dict]) -> None:
    for r in resultados:
        ciudad = r["ciudad"]
        años   = r["años"]
        precip = np.array(r["precip"])

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#F8F9FA")

        colors = ["#60A5FA" if p >= 1400 else "#93C5FD" if p >= 1000 else "#FCA5A5"
                  for p in precip]
        ax.bar(años, precip, color=colors, alpha=0.75, width=0.8, zorder=2)

        if len(precip) >= WINDOW:
            mm      = _media_movil(precip)
            años_mm = np.array(años)[WINDOW - 1:]
            ax.plot(años_mm, mm, color="#1E3A8A", linewidth=2.5,
                    label=f"Media móvil {WINDOW} años", zorder=3)

        estilo_ax(ax,
                  f"Precipitación total anual\n{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
                  "Año", "Precipitación anual (mm)")
        ax.legend(fontsize=10)

        for año, p in zip(años, precip):
            if p < 800:
                ax.annotate(f"{int(p)}", xy=(año, p), xytext=(0, 5),
                            textcoords="offset points", ha="center",
                            fontsize=9, color="#B91C1C", fontweight="bold")

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["precipitacion"] / f"precip_anual_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()


# ── H2: Días con precipitación intensa ────────────────────────────────────────
def graficar_dias_intensos(resultados: list[dict]) -> None:
    for r in resultados:
        ciudad = r["ciudad"]
        años   = r["años"]
        dias   = np.array(r["dias"])

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#F8F9FA")

        colors = ["#DC2626" if d >= 10 else "#F59E0B" if d >= 5
                  else "#10B981" if d >= 1 else "#94A3B8" for d in dias]
        ax.bar(años, dias, color=colors, alpha=0.75, width=0.8, zorder=2)

        if len(dias) >= WINDOW:
            mm      = _media_movil(dias)
            años_mm = np.array(años)[WINDOW - 1:]
            ax.plot(años_mm, mm, color="#1E3A8A", linewidth=2.5,
                    label=f"Media móvil {WINDOW} años", zorder=3)

        estilo_ax(ax,
                  f"Días con precipitación > {r['umbral']:.0f} mm por año\n{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
                  "Año", "Número de días")
        ax.legend(fontsize=10)

        for año, d in zip(años, dias):
            if d > 10:
                ax.annotate(f"{int(d)}", xy=(año, d), xytext=(0, 5),
                            textcoords="offset points", ha="center",
                            fontsize=9, color="#991B1B", fontweight="bold")

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["precipitacion"] / f"dias_intensos_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()


# ── H2: Heatmap precipitación mensual por año (seaborn) ───────────────────────
def graficar_heatmap_precip_mensual(ciudades: list) -> None:
    """
    Heatmap año × mes de precipitación total mensual.
    Seaborn aporta aquí: escala de color continua sobre matriz 2D.
    """
    MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
             "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    for ciudad in ciudades:
        if ciudad.df is None:
            continue

        pivot = (
            ciudad.df.groupby(["año", "mes"])["precipitation_sum"]
            .sum().unstack(level="mes")
        )
        pivot.columns = MESES

        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor("#F8F9FA")

        sns.heatmap(
            pivot, ax=ax,
            cmap="Blues",
            linewidths=0,
            cbar_kws={"label": "Precipitación total mensual (mm)", "shrink": 0.6},
            yticklabels=10,
        )

        ax.set_title(
            f"Precipitación mensual por año\n{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
            fontsize=14, fontweight="bold", color="#021B2E", pad=15,
        )
        ax.set_xlabel("Mes", fontsize=11, color="#021B2E")
        ax.set_ylabel("Año", fontsize=11, color="#021B2E")
        ax.tick_params(colors="#475569")

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["precipitacion"] / f"heatmap_precip_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()
