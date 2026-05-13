"""
Gráficos de correlación distancia al mar
Recibe los dicts calculados por analisis/correlacion_mar.py
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN
from scripts.funciones_variables import estilo_ax

PERIODO_COLORS = {
    "1940–1979": "#94A3B8",
    "1980–2009": "#60A5FA",
    "2010–2025": "#EF4444",
}


def _scatter_reg(ax, x, y, ciudades_obj, titulo, ylabel):
    """Panel de scatter + regresión + IC 95%."""
    ax.set_facecolor("#F8F9FA")
    x_arr = np.array(x, dtype=float)
    y_arr = np.array(y, dtype=float)

    for xi, yi, ciudad in zip(x_arr, y_arr, ciudades_obj):
        ax.scatter(xi, yi, color=ciudad.color, s=120, zorder=4,
                   edgecolors="white", linewidths=0.9)
        ax.annotate(ciudad.nombre.capitalize(), (xi, yi),
                    textcoords="offset points", xytext=(6, 4),
                    fontsize=8.5, color=ciudad.color, fontweight="bold")

    slope, intercept, r, p, _ = stats.linregress(x_arr, y_arr)
    x_line = np.linspace(x_arr.min() - 3, x_arr.max() + 8, 200)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, color="#475569", linewidth=1.8,
            linestyle="--", alpha=0.7, zorder=3)

    n  = len(x_arr)
    se = np.sqrt(np.sum((y_arr - (slope * x_arr + intercept))**2) / (n - 2))
    t  = stats.t.ppf(0.975, df=n - 2)
    ci = t * se * np.sqrt(1/n + (x_line - x_arr.mean())**2 / np.sum((x_arr - x_arr.mean())**2))
    ax.fill_between(x_line, y_line - ci, y_line + ci,
                    color="#475569", alpha=0.09, zorder=2)

    star  = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
    p_str = "< 0.001" if p < 0.001 else f"= {p:.3f}"
    ax.text(0.97, 0.05,
            f"r = {r:.3f} {star}\np {p_str}\n{slope:+.3f} por km",
            transform=ax.transAxes, fontsize=9, ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", alpha=0.85, ec="#CBD5E1"))

    ax.set_title(titulo, fontsize=11, fontweight="bold", color="#021B2E", pad=8)
    ax.set_xlabel("Distancia al mar (km)", fontsize=10, color="#021B2E")
    ax.set_ylabel(ylabel, fontsize=10, color="#021B2E")
    ax.tick_params(colors="#475569")
    ax.grid(axis="y", color="#CBD5E1", linestyle="--", alpha=0.6, zorder=1)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(x_arr.min() - 8, x_arr.max() + 12)


# ── Figura 1: 4 paneles de correlación ────────────────────────────────────────
def graficar_correlacion_paneles(datos: dict) -> None:
    resumen  = datos["resumen"]
    variab   = datos["variab"]
    ciudades = datos["ciudades"]
    periodos = datos["periodos"]

    fig = plt.figure(figsize=(14, 11))
    fig.patch.set_facecolor("#F8F9FA")
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.48, wspace=0.35)

    # Panel 1 — temperatura media por período
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor("#F8F9FA")
    all_x, all_y = [], []

    for periodo in periodos:
        sub = resumen[resumen["periodo"] == periodo]
        color = PERIODO_COLORS.get(periodo, "#94A3B8")
        ax1.scatter(sub["dist_mar"], sub["temp_media"],
                    color=color, s=80, zorder=4,
                    edgecolors="white", linewidths=0.8, label=periodo, alpha=0.85)

        ultimo_periodo = list(periodos.keys())[-1]
        if periodo == ultimo_periodo:
            ciudad_map = {c.nombre: c for c in ciudades}
            for _, row in sub.iterrows():
                ciudad = ciudad_map.get(row["ciudad"])
                if ciudad:
                    ax1.annotate(ciudad.nombre.capitalize(),
                                 (row["dist_mar"], row["temp_media"]),
                                 textcoords="offset points", xytext=(5, 3),
                                 fontsize=8, color=ciudad.color, fontweight="bold")
        all_x.extend(sub["dist_mar"].tolist())
        all_y.extend(sub["temp_media"].tolist())

    sl, ic, rg, pg, _ = stats.linregress(all_x, all_y)
    x_l = np.linspace(-3, max(all_x) + 10, 200)
    ax1.plot(x_l, sl * x_l + ic, color="#021B2E", linewidth=1.8,
             linestyle="--", alpha=0.6)
    star = "***" if pg < 0.001 else ("**" if pg < 0.01 else ("*" if pg < 0.05 else "ns"))
    p_s  = "< 0.001" if pg < 0.001 else f"= {pg:.3f}"
    ax1.text(0.97, 0.05, f"r = {rg:.3f} {star}\np {p_s}\n{sl:+.3f} °C/km",
             transform=ax1.transAxes, fontsize=9, ha="right", va="bottom",
             bbox=dict(boxstyle="round,pad=0.4", fc="white", alpha=0.85, ec="#CBD5E1"))
    ax1.set_title("Temperatura media anual vs. distancia al mar\n(coloreado por período)",
                  fontsize=11, fontweight="bold", color="#021B2E", pad=8)
    ax1.set_xlabel("Distancia al mar (km)", fontsize=10, color="#021B2E")
    ax1.set_ylabel("Temperatura media anual (°C)", fontsize=10, color="#021B2E")
    ax1.tick_params(colors="#475569")
    ax1.legend(fontsize=9, loc="upper right")
    ax1.grid(axis="y", color="#CBD5E1", linestyle="--", alpha=0.6, zorder=1)
    ax1.spines[["top", "right"]].set_visible(False)

    # Panel 2 — días > 30°C
    ultimo = list(periodos.keys())[-1]
    sub_rec      = resumen[resumen["periodo"] == ultimo].copy()
    ciudad_map   = {c.nombre: c for c in ciudades}
    ciudades_sub = [ciudad_map[n] for n in sub_rec["ciudad"] if n in ciudad_map]

    ax2 = fig.add_subplot(gs[0, 1])
    _scatter_reg(ax2, sub_rec["dist_mar"], sub_rec["dias_30"], ciudades_sub,
                 f"Días con Tmax > 30°C vs. distancia al mar\n(media {ultimo})",
                 "Días/año con Tmax > 30°C")

    # Panel 3 — días > 35°C
    ax3 = fig.add_subplot(gs[1, 0])
    _scatter_reg(ax3, sub_rec["dist_mar"], sub_rec["dias_35"], ciudades_sub,
                 f"Días con Tmax > 35°C vs. distancia al mar\n(media {ultimo})",
                 "Días/año con Tmax > 35°C")

    # Panel 4 — variabilidad interanual
    ciudades_var = [ciudad_map[n] for n in variab["ciudad"] if n in ciudad_map]
    ax4 = fig.add_subplot(gs[1, 1])
    _scatter_reg(ax4, variab["dist_mar"], variab["variabilidad"], ciudades_var,
                 "Variabilidad interanual vs. distancia al mar\n(desv. estándar temp. media anual)",
                 "Desv. estándar (°C)")

    fig.suptitle(
        f"Efecto termorregulador del mar · Euskal Herria {AÑO_INICIO}–{AÑO_FIN}\n"
        "Correlación de Pearson · IC 95% sombreado · *** p < 0.001",
        fontsize=13, fontweight="bold", color="#021B2E", y=1.02,
    )
    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["correlacion_mar"] / "correlacion_distancia_mar.png",
                dpi=180, bbox_inches="tight")
    plt.show()


# ── Figura 2: Gradiente por décadas ───────────────────────────────────────────
def graficar_gradiente_decadas(datos: dict) -> None:
    gdf = datos["gradiente"]

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    bar_colors = ["#0D9488" if s < 0 else "#EF4444" for s in gdf["slope_10km"]]
    bars = ax.bar(gdf["decada"], gdf["slope_10km"],
                  color=bar_colors, alpha=0.7, edgecolor="white",
                  linewidth=0.8, zorder=2, width=0.6)

    for bar, row in zip(bars, gdf.itertuples()):
        star = "***" if row.p < 0.001 else ("**" if row.p < 0.01 else ("*" if row.p < 0.05 else ""))
        ypos = bar.get_height() + 0.005 if bar.get_height() >= 0 else bar.get_height() - 0.045
        ax.text(bar.get_x() + bar.get_width() / 2, ypos,
                f"r={row.r:.2f}{star}", ha="center", fontsize=9, color="#021B2E")

    ax.axhline(0, color="#94A3B8", linewidth=1)
    ax.set_title(
        "Gradiente térmico mar–interior por décadas\n"
        "°C de diferencia en temperatura media por cada 10 km adicionales al mar",
        fontsize=11, fontweight="bold", color="#021B2E", pad=10,
    )
    ax.set_xlabel("Década", fontsize=11, color="#021B2E")
    ax.set_ylabel("Gradiente (°C / 10 km)", fontsize=11, color="#021B2E")
    ax.tick_params(colors="#475569")
    ax.grid(axis="y", color="#CBD5E1", linestyle="--", alpha=0.6, zorder=1)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["correlacion_mar"] / "gradiente_decadas.png",
                dpi=180, bbox_inches="tight")
    plt.show()


# ── Figura 3: Pairplot entre variables climáticas (seaborn) ───────────────────
def graficar_pairplot_variables(ciudades: list) -> None:
    """
    Pairplot de las variables climáticas principales agregadas por año.
    Seaborn aporta aquí: matriz de dispersión con densidad KDE en la diagonal.
    """
    import pandas as pd

    frames = []
    for ciudad in ciudades:
        if ciudad.df is None:
            continue
        anual = ciudad.df.groupby("año").agg(
            temp_media=("temperature_2m_mean", "mean"),
            temp_max=("temperature_2m_max", "mean"),
            precip=("precipitation_sum", "sum"),
            viento=("wind_speed_10m_max", "mean"),
        ).reset_index()
        anual["ciudad"]   = ciudad.nombre.capitalize()
        anual["dist_mar"] = ciudad.dist_mar
        frames.append(anual)

    data   = pd.concat(frames, ignore_index=True)
    paleta = {c.nombre.capitalize(): c.color for c in ciudades}

    g = sns.pairplot(
        data,
        vars=["temp_media", "temp_max", "precip", "viento"],
        hue="ciudad", palette=paleta,
        diag_kind="kde", plot_kws={"alpha": 0.4, "s": 20},
        diag_kws={"linewidth": 1.5},
    )
    g.figure.suptitle(
        f"Relaciones entre variables climáticas por ciudad\n({AÑO_INICIO}–{AÑO_FIN})",
        y=1.02, fontsize=13, fontweight="bold", color="#021B2E",
    )
    g.figure.patch.set_facecolor("#F8F9FA")

    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["correlacion_mar"] / "pairplot_variables.png",
                dpi=180, bbox_inches="tight")
    plt.show()
