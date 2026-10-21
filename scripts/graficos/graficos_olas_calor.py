"""
Gráficos de olas de calor — refuerzo H4
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN, WINDOW
from scripts.funciones_variables import estilo_ax, media_movil, guardar_grafico


def graficar_duracion_olas(resultados: list[dict]) -> None:
    """
    Dos paneles por ciudad: número de olas por año y duración máxima.
    """
    for r in resultados:
        ciudad = r["ciudad"]

        if r["num_olas_anual"].empty:
            print(f"  ⚠️  {ciudad.nombre}: sin olas de calor detectadas")
            continue

        años_num = r["num_olas_anual"].index.tolist()
        num_olas = r["num_olas_anual"].values
        años_dur = r["duracion_max"].index.tolist()
        dur_max  = r["duracion_max"].values

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        fig.patch.set_facecolor("#0E0E0E")

        colors1 = ["#F59E0B" if n == 1 else "#EF4444" if n == 2 else "#7F1D1D"
                   for n in num_olas]
        ax1.bar(años_num, num_olas, color=colors1, alpha=0.8, width=0.8, zorder=2)
        if len(num_olas) >= WINDOW:
            mm = media_movil(num_olas)
            ax1.plot(años_num[WINDOW - 1:], mm, color="#D0D0D0",
                     linewidth=2.5, label=f"Media móvil {WINDOW} años", zorder=3)
        estilo_ax(ax1,
                  f"Número de olas de calor por año\n{ciudad.nombre.capitalize()} "
                  f"(≥ {r['min_dias']} días consecutivos con Tmax > {r['umbral']:.0f}°C)",
                  "", "Nº de olas")
        ax1.legend(fontsize=10)

        colors2 = ["#F59E0B" if d <= 5 else "#EF4444" if d <= 10 else "#7F1D1D"
                   for d in dur_max]
        ax2.bar(años_dur, dur_max, color=colors2, alpha=0.8, width=0.8, zorder=2)
        if len(dur_max) >= WINDOW:
            mm2 = media_movil(dur_max)
            ax2.plot(años_dur[WINDOW - 1:], mm2, color="#D0D0D0",
                     linewidth=2.5, label=f"Media móvil {WINDOW} años", zorder=3)

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

        guardar_grafico(OUTPUT_DIRS["extremos_35"] / f"olas_calor_{ciudad.nombre}.png")


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
    pivot = pivot.loc[:, pivot.columns >= 1960]

    fig, ax = plt.subplots(figsize=(18, 4))
    fig.patch.set_facecolor("#0E0E0E")

    sns.heatmap(
        pivot, ax=ax,
        cmap="YlOrRd",
        linewidths=0.3,
        linecolor="#0E0E0E",
        cbar_kws={"label": "Días totales en ola de calor", "shrink": 0.7},
        yticklabels=True,
        xticklabels=5,
    )

    ax.set_title(
        f"Días totales en ola de calor por ciudad y año\n"
        f"(olas ≥ {resultados[0]['min_dias']} días con Tmax > {resultados[0]['umbral']:.0f}°C)",
        fontsize=13, fontweight="bold", color="#D0D0D0", pad=12,
    )
    ax.set_xlabel("Año", fontsize=11, color="#D0D0D0")
    ax.set_ylabel("", fontsize=11)
    ax.tick_params(colors="#686868", axis="x", rotation=45)
    ax.tick_params(colors="#686868", axis="y", rotation=0)

    guardar_grafico(OUTPUT_DIRS["extremos_35"] / "calendario_olas_calor.png")


def graficar_calendario_olas_p95(resultados: list[dict]) -> None:
    """
    Heatmap de olas de calor con umbral relativo p95 local por ciudad.
    Al usar percentil local, todas las ciudades (incluidas las costeras) registran olas.
    """
    rows = []
    for r in resultados:
        if r["duracion_total"].empty:
            continue
        umbral_val = r.get("umbral_valor", r.get("umbral", ""))
        ciudad_lbl = f"{r['ciudad'].nombre.capitalize()} (>{umbral_val}°C)"
        for año, dur in r["duracion_total"].items():
            rows.append({"ciudad": ciudad_lbl, "año": año, "dias": dur})

    if not rows:
        print("⚠️  Sin datos p95 de olas de calor")
        return

    data  = pd.DataFrame(rows)
    pivot = data.pivot(index="ciudad", columns="año", values="dias").fillna(0)
    pivot = pivot.loc[:, pivot.columns >= 1960]

    fig, ax = plt.subplots(figsize=(18, 5))
    fig.patch.set_facecolor("#0E0E0E")

    sns.heatmap(
        pivot, ax=ax,
        cmap="YlOrRd",
        linewidths=0.3,
        linecolor="#0E0E0E",
        cbar_kws={"label": "Días totales en ola de calor (p95 local)", "shrink": 0.7},
        yticklabels=True,
        xticklabels=5,
    )

    ax.set_title(
        "Días totales en ola de calor por ciudad y año (umbral relativo p95)\n"
        "Cada ciudad usa su propio percentil 95 de Tmax — comparable entre costeras e interior",
        fontsize=13, fontweight="bold", color="#D0D0D0", pad=12,
    )
    ax.set_xlabel("Año", fontsize=11, color="#D0D0D0")
    ax.set_ylabel("", fontsize=11)
    ax.tick_params(colors="#686868", axis="x", rotation=45)
    ax.tick_params(colors="#686868", axis="y", rotation=0)

    guardar_grafico(OUTPUT_DIRS["extremos_35"] / "calendario_olas_p95.png")
