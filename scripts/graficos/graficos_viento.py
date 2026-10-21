"""
Gráficos del régimen de vientos — H6
Recibe los dicts calculados por analisis/viento.py
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN, WINDOW
from scripts.funciones_variables import estilo_ax, media_movil, guardar_grafico

MESES  = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
PERIODO_COLORS = {
    "1940–1979": "#94A3B8",
    "1980–2009": "#F59E0B",
    "2010–2025": "#EF4444",
}


def graficar_viento_anual(resultados: list[dict]) -> None:
    """Serie temporal de velocidad media anual + tendencia OLS por ciudad."""
    for r in resultados:
        ciudad = r["ciudad"]
        años   = r["años"]
        viento = r["viento"]

        mm      = media_movil(viento)
        años_mm = np.array(años)[WINDOW - 1:]

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#0E0E0E")

        ax.plot(años, viento, color="#6B91B0", linewidth=1.5, alpha=0.6,
                label="Velocidad máx. media anual", marker="o", markersize=3, zorder=2)
        ax.plot(años_mm, mm, color="#0D5F8C", linewidth=2.5,
                label=f"Media móvil {WINDOW} años", zorder=3)

        slope_dec = r["slope"] * 10
        sign      = "+" if slope_dec >= 0 else ""
        trend_lbl = f"Tendencia lineal ({sign}{slope_dec:.2f} km/h/década)"
        if r.get("p_value") is not None:
            trend_lbl += f"\np={r['p_value']:.2e}, R²={r['r2']:.3f}"
        if r.get("mk_p") is not None:
            sig = "✓" if r["mk_p"] < 0.05 else "~"
            trend_lbl += f"\nMann-Kendall: {r['mk_trend']} {sig} (p={r['mk_p']:.3f})"

        ax.plot(años, r["tendencia"], color="#D0D0D0", linewidth=2,
                linestyle="--", label=trend_lbl, zorder=3)
        ax.fill_between(años, viento, alpha=0.08, color="#6B91B0")

        estilo_ax(ax,
                  f"Velocidad media del viento (máx. diaria) por año\n"
                  f"{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
                  "Año", "Velocidad media (km/h)")
        ax.legend(fontsize=9)

        guardar_grafico(OUTPUT_DIRS["viento"] / f"viento_anual_{ciudad.nombre}.png")


def graficar_dias_viento_fuerte(resultados: list[dict]) -> None:
    """Días con viento > umbral por año como barras con media móvil."""
    for r in resultados:
        ciudad = r["ciudad"]
        años   = r["años"]
        dias   = np.array(r["dias"])
        umbral = r["umbral"]

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#0E0E0E")

        colors = ["#9DB8D0" if d <= 20 else "#4472A0" if d <= 40 else "#1E3A8A"
                  for d in dias]
        ax.bar(años, dias, color=colors, alpha=0.75, width=0.8, zorder=2)

        if len(dias) >= WINDOW:
            mm      = media_movil(dias)
            años_mm = np.array(años)[WINDOW - 1:]
            ax.plot(años_mm, mm, color="#D0D0D0", linewidth=2.5,
                    label=f"Media móvil {WINDOW} años", zorder=3)

        ax.axhline(y=dias.mean(), color="#686868", linewidth=1.2, linestyle=":",
                   label=f"Media histórica ({dias.mean():.0f} días/año)", zorder=3)

        estilo_ax(ax,
                  f"Días con viento fuerte (máx. > {umbral:.0f} km/h) por año\n"
                  f"{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
                  "Año", "Número de días")
        ax.legend(fontsize=10)

        guardar_grafico(OUTPUT_DIRS["viento"] / f"dias_viento_fuerte_{ciudad.nombre}.png")


def graficar_perfil_mensual_comparativa(datos: dict) -> None:
    """Perfil mensual de viento — todas las ciudades superpuestas (media histórica)."""
    df_mensual = datos["perfil_mensual"]
    ciudades   = datos["ciudades"]

    df_media = (df_mensual
                .groupby(["ciudad","color","mes","mes_str"])["viento"]
                .mean().reset_index())

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor("#0E0E0E")

    for ciudad in ciudades:
        sub = df_media[df_media["ciudad"] == ciudad.nombre].sort_values("mes")
        if sub.empty:
            continue
        ax.plot(sub["mes"], sub["viento"], color=ciudad.color,
                linewidth=2, marker="o", markersize=5,
                label=ciudad.nombre.capitalize())

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MESES, fontsize=10)
    estilo_ax(ax,
              f"Ciclo estacional del viento — todas las ciudades ({AÑO_INICIO}–{AÑO_FIN})",
              "Mes", "Velocidad media (km/h)", x_multiple=None)
    ax.legend(fontsize=10, ncol=2)

    guardar_grafico(OUTPUT_DIRS["viento"] / "perfil_mensual_viento.png")


def graficar_comparativa_ciudades(datos: dict) -> None:
    """Boxplot de la distribución de viento anual, ordenado por distancia al mar."""
    df       = datos["comparativa"]
    ciudades = datos["ciudades"]

    orden   = [c.nombre for c in sorted(ciudades, key=lambda c: c.dist_mar)]
    colores = {c.nombre: c.color for c in ciudades}

    df = df.copy()
    df["ciudad_hue"] = df["ciudad"]

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#0E0E0E")
    ax.set_facecolor("#0E0E0E")

    sns.boxplot(
        data=df, x="ciudad", y="viento_medio", hue="ciudad_hue",
        order=orden, palette=colores, legend=False, notch=True,
        linewidth=1.2, flierprops={"marker": ".", "alpha": 0.4}, ax=ax,
    )
    ax.set_facecolor("#0E0E0E")
    ax.set_xticks(range(len(orden)))
    ax.set_xticklabels([n.capitalize() for n in orden])

    estilo_ax(ax,
              "Distribución de la velocidad media anual del viento por ciudad\n"
              "(ordenado por distancia al mar)",
              "Ciudad", "Velocidad media anual (km/h)", x_multiple=None)

    guardar_grafico(OUTPUT_DIRS["viento"] / "comparativa_viento_ciudades.png")


def graficar_periodos_ciudades(datos: dict) -> None:
    """Panel 4×2: perfil mensual de viento por ciudad y período histórico."""
    df_mensual = datos["perfil_mensual"]
    ciudades   = datos["ciudades"]

    n_cols = 4
    n_rows = 2
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 8), sharey=True)
    fig.patch.set_facecolor("#0E0E0E")
    axes = axes.flatten()

    for i, ciudad in enumerate(ciudades):
        if i >= len(axes):
            break
        ax  = axes[i]
        ax.set_facecolor("#0E0E0E")
        sub = df_mensual[df_mensual["ciudad"] == ciudad.nombre]
        for periodo, grp in sub.groupby("periodo"):
            grp_s = grp.sort_values("mes")
            ax.plot(grp_s["mes"], grp_s["viento"],
                    color=PERIODO_COLORS.get(periodo, "#999"),
                    linewidth=1.8, marker="o", markersize=3, label=periodo)
        ax.set_title(ciudad.nombre.capitalize(), fontsize=11,
                     fontweight="bold", color="#D0D0D0")
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(["E","F","M","A","M","J","J","A","S","O","N","D"],
                            fontsize=8)
        ax.tick_params(colors="#686868")
        ax.grid(axis="y", color="#303030", linestyle="--", alpha=0.6, zorder=1)
        ax.spines[["top","right"]].set_visible(False)

    for j in range(len(ciudades), len(axes)):
        axes[j].set_visible(False)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower right",
               bbox_to_anchor=(0.98, 0.02), fontsize=9, framealpha=0.0)

    fig.suptitle(
        f"Perfil mensual de viento por períodos históricos ({AÑO_INICIO}–{AÑO_FIN})",
        fontsize=13, fontweight="bold", color="#D0D0D0", y=1.01,
    )

    guardar_grafico(OUTPUT_DIRS["viento"] / "periodos_viento_ciudades.png")
