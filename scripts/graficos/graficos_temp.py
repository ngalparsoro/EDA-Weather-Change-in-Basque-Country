"""
Gráficos de temperatura — H1 (aumento) y H4 (extremos)
Recibe los dicts calculados por analisis/temperaturas.py
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN
from scripts.funciones_variables import estilo_ax

WINDOW = 10


def _media_movil(valores, window=WINDOW):
    return np.convolve(valores, np.ones(window) / window, mode="valid")


# ── H1: Días con Tmax > 30°C ──────────────────────────────────────────────────
def graficar_dias_30(resultados: list[dict]) -> None:
    for r in resultados:
        ciudad = r["ciudad"]
        años   = r["años"]
        dias   = np.array(r["dias"])

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#F8F9FA")

        colors = ["#0D9488" if d <= 8 else "#F59E0B" if d <= 13 else "#EF4444" for d in dias]
        ax.bar(años, dias, color=colors, alpha=0.7, width=0.8, zorder=2)

        if len(dias) >= WINDOW:
            mm      = _media_movil(dias)
            años_mm = np.array(años)[WINDOW - 1:]
            ax.plot(años_mm, mm, color="#021B2E", linewidth=2.5,
                    label=f"Media móvil {WINDOW} años", zorder=3)

        estilo_ax(ax,
                  f"Días con temperatura máxima > 30°C por año\n{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
                  "Año", "Número de días")
        ax.legend(fontsize=10)

        for año, dia in zip(años, dias):
            if dia >= 14:
                ax.annotate(f"{dia}", xy=(año, dia), xytext=(0, 5),
                            textcoords="offset points", ha="center",
                            fontsize=9, color="#EF4444", fontweight="bold")

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["temp_30"] / f"dias_30_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()


# ── H1: Temperatura media anual ───────────────────────────────────────────────
def graficar_temp_media_anual(resultados: list[dict]) -> None:
    for r in resultados:
        ciudad = r["ciudad"]
        años   = r["años"]
        temps  = r["temps"]

        mm      = _media_movil(temps)
        años_mm = np.array(años)[WINDOW - 1:]

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#F8F9FA")

        ax.plot(años, temps, color="#EF4444", linewidth=1.5, alpha=0.6,
                label="Temperatura media anual", marker="o", markersize=3, zorder=2)
        ax.plot(años_mm, mm, color="#0D9488", linewidth=2.5,
                label=f"Media móvil {WINDOW} años", zorder=3)
        ax.plot(años, r["tendencia"], color="#021B2E", linewidth=2,
                linestyle="--",
                label=f"Tendencia lineal (+{r['slope'] * 10:.2f}°C/década)",
                zorder=3)
        ax.fill_between(años, temps, alpha=0.1, color="#EF4444")

        estilo_ax(ax,
                  f"Temperatura media anual\n{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
                  "Año", "Temperatura media (°C)")
        ax.set_ylim(9, 16)
        ax.legend(fontsize=10)

        idx_max = np.argmax(temps)
        idx_min = np.argmin(temps)
        ax.annotate(f"{temps[idx_max]:.1f}°C", xy=(años[idx_max], temps[idx_max]),
                    xytext=(5, 5), textcoords="offset points",
                    fontsize=9, color="#EF4444", fontweight="bold")
        ax.annotate(f"{temps[idx_min]:.1f}°C", xy=(años[idx_min], temps[idx_min]),
                    xytext=(5, -10), textcoords="offset points",
                    fontsize=9, color="#0D9488", fontweight="bold")

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["temp_media"] / f"temp_media_anual_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()


# ── H1: Heatmap de temperatura media mensual (seaborn) ────────────────────────
def graficar_heatmap_temp_mensual(ciudades: list) -> None:
    """
    Heatmap año × mes de temperatura media para cada ciudad.
    Seaborn aporta aquí: escala de color continua sobre una matriz 2D.
    """
    MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
             "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    for ciudad in ciudades:
        if ciudad.df is None:
            continue

        pivot = (
            ciudad.df.groupby(["año", "mes"])["temperature_2m_mean"]
            .mean().unstack(level="mes")
        )
        pivot.columns = MESES

        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor("#F8F9FA")

        sns.heatmap(
            pivot,
            ax=ax,
            cmap="RdYlBu_r",
            linewidths=0,
            cbar_kws={"label": "Temperatura media (°C)", "shrink": 0.6},
            yticklabels=10,
        )

        ax.set_title(
            f"Temperatura media mensual por año\n{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
            fontsize=14, fontweight="bold", color="#021B2E", pad=15,
        )
        ax.set_xlabel("Mes", fontsize=11, color="#021B2E")
        ax.set_ylabel("Año", fontsize=11, color="#021B2E")
        ax.tick_params(colors="#475569")

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["temp_media"] / f"heatmap_temp_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()


# ── H4: Días con Tmax > 35°C ──────────────────────────────────────────────────
def graficar_dias_extremos(resultados: list[dict]) -> None:
    for r in resultados:
        ciudad = r["ciudad"]
        años   = r["años"]
        dias   = np.array(r["dias"])

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#F8F9FA")

        colors = ["#F59E0B" if d <= 3 else "#EF4444" if d <= 7 else "#7F1D1D" for d in dias]
        ax.bar(años, dias, color=colors, alpha=0.75, width=0.8, zorder=2)

        if len(dias) >= WINDOW:
            mm      = _media_movil(dias)
            años_mm = np.array(años)[WINDOW - 1:]
            ax.plot(años_mm, mm, color="#1E3A8A", linewidth=2.5,
                    label=f"Media móvil {WINDOW} años", zorder=3)

        estilo_ax(ax,
                  f"Días con temperatura extrema > {r['umbral']:.0f}°C por año\n{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
                  "Año", "Número de días extremos")
        ax.legend(fontsize=10)

        for año, dia in zip(años, dias):
            if dia >= 8:
                ax.annotate(f"{dia}", xy=(año, dia), xytext=(0, 5),
                            textcoords="offset points", ha="center",
                            fontsize=9, color="#7F1D1D", fontweight="bold")

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["extremos_35"] / f"extremos_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()


# ── H4: Boxplot de distribución por décadas (seaborn) ─────────────────────────
def graficar_boxplot_decadas(ciudades: list) -> None:
    """
    Distribución de temperaturas máximas por décadas para cada ciudad.
    Seaborn aporta aquí: boxplot con notch y swarmplot superpuesto.
    """
    for ciudad in ciudades:
        if ciudad.df is None:
            continue

        df = ciudad.df.copy()
        df["decada"] = (df["año"] // 10 * 10).astype(str) + "s"

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#F8F9FA")
        ax.set_facecolor("#F8F9FA")

        sns.boxplot(
            data=df, x="decada", y="temperature_2m_max",
            palette="RdYlBu_r", notch=True, ax=ax,
            linewidth=1.2, flierprops={"marker": ".", "alpha": 0.3},
        )

        ax.set_title(
            f"Distribución de temperatura máxima diaria por décadas\n{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
            fontsize=14, fontweight="bold", color="#021B2E", pad=15,
        )
        ax.set_xlabel("Década", fontsize=11, color="#021B2E")
        ax.set_ylabel("Temperatura máxima diaria (°C)", fontsize=11, color="#021B2E")
        ax.tick_params(colors="#475569")
        ax.grid(axis="y", color="#CBD5E1", linestyle="--", alpha=0.6, zorder=1)
        ax.spines[["top", "right"]].set_visible(False)

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["extremos_35"] / f"boxplot_decadas_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()
