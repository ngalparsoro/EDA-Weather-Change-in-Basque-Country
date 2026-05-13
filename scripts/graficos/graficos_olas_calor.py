"""
Gráficos de olas de calor — refuerzo H4
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN
from scripts.funciones_variables import estilo_ax

WINDOW = 10


def graficar_duracion_olas(resultados: list[dict]) -> None:
    """
    Dos paneles por ciudad: número de olas por año y duración máxima.
    """
    for r in resultados:
        ciudad = r["ciudad"]

        if r["num_olas_anual"].empty:
            print(f"  ⚠️  {ciudad.nombre}: sin olas de calor detectadas")
            continue

        años_num  = r["num_olas_anual"].index.tolist()
        num_olas  = r["num_olas_anual"].values
        años_dur  = r["duracion_max"].index.tolist()
        dur_max   = r["duracion_max"].values

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        fig.patch.set_facecolor("#F8F9FA")

        # Panel 1 — número de olas
        colors1 = ["#F59E0B" if n == 1 else "#EF4444" if n == 2 else "#7F1D1D"
                   for n in num_olas]
        ax1.bar(años_num, num_olas, color=colors1, alpha=0.8, width=0.8, zorder=2)
        if len(num_olas) >= WINDOW:
            mm = np.convolve(num_olas, np.ones(WINDOW) / WINDOW, mode="valid")
            ax1.plot(años_num[WINDOW - 1:], mm, color="#021B2E",
                     linewidth=2.5, label=f"Media móvil {WINDOW} años", zorder=3)
        estilo_ax(ax1,
                  f"Número de olas de calor por año\n{ciudad.nombre.capitalize()} "
                  f"(≥ {r['min_dias']} días consecutivos con Tmax > {r['umbral']:.0f}°C)",
                  "", "Nº de olas")
        ax1.legend(fontsize=10)

        # Panel 2 — duración máxima
        colors2 = ["#F59E0B" if d <= 5 else "#EF4444" if d <= 10 else "#7F1D1D"
                   for d in dur_max]
        ax2.bar(años_dur, dur_max, color=colors2, alpha=0.8, width=0.8, zorder=2)
        if len(dur_max) >= WINDOW:
            mm2 = np.convolve(dur_max, np.ones(WINDOW) / WINDOW, mode="valid")
            ax2.plot(años_dur[WINDOW - 1:], mm2, color="#021B2E",
                     linewidth=2.5, label=f"Media móvil {WINDOW} años", zorder=3)

        # Anotar olas más largas (> percentil 90)
        umbral_anot = np.percentile(dur_max[dur_max > 0], 90) if any(dur_max > 0) else 999
        for año, d in zip(años_dur, dur_max):
            if d >= umbral_anot and d > 0:
                ax2.annotate(f"{int(d)}d", xy=(año, d), xytext=(0, 5),
                             textcoords="offset points", ha="center",
                             fontsize=9, color="#7F1D1D", fontweight="bold")

        estilo_ax(ax2,
                  "Duración máxima de ola de calor por año",
                  "Año", "Días consecutivos")
        ax2.legend(fontsize=10)

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["extremos_35"] / f"olas_calor_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()


def graficar_calendario_olas(resultados: list[dict]) -> None:
    """
    Heatmap: ciudad × año coloreado por duración total de olas de calor.
    Seaborn: una sola figura que compara todas las ciudades de un vistazo.
    """
    rows = []
    for r in resultados:
        if r["duracion_total"].empty:
            continue
        for año, dur in r["duracion_total"].items():
            rows.append({
                "ciudad": r["ciudad"].nombre.capitalize(),
                "año":    año,
                "dias":   dur,
            })

    if not rows:
        print("⚠️  Sin datos de olas de calor para el calendario")
        return

    data  = pd.DataFrame(rows)
    pivot = data.pivot(index="ciudad", columns="año", values="dias").fillna(0)

    # Mostrar solo desde 1960
    pivot = pivot.loc[:, pivot.columns >= 1960]

    fig, ax = plt.subplots(figsize=(18, 4))
    fig.patch.set_facecolor("#F8F9FA")

    sns.heatmap(
        pivot, ax=ax,
        cmap="YlOrRd",
        linewidths=0.3,
        linecolor="#F8F9FA",
        cbar_kws={"label": "Días totales en ola de calor", "shrink": 0.7},
        yticklabels=True,
        xticklabels=5,
    )

    ax.set_title(
        f"Días totales en ola de calor por ciudad y año\n"
        f"(olas ≥ {resultados[0]['min_dias']} días con Tmax > {resultados[0]['umbral']:.0f}°C)",
        fontsize=13, fontweight="bold", color="#021B2E", pad=12,
    )
    ax.set_xlabel("Año", fontsize=11, color="#021B2E")
    ax.set_ylabel("", fontsize=11)
    ax.tick_params(colors="#475569", axis="x", rotation=45)
    ax.tick_params(colors="#475569", axis="y", rotation=0)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["extremos_35"] / "calendario_olas_calor.png",
                dpi=180, bbox_inches="tight")
    plt.show()
