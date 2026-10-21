"""
Gráficos de estacionalidad y comparativa entre ciudades — H3 y H5
Recibe los dicts calculados por analisis/estacionalidad.py
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import seaborn as sns
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN
from scripts.funciones_variables import estilo_ax, guardar_grafico

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


# ── H3: Comparativa temperatura media anual entre ciudades ────────────────────
def graficar_comparativa_ciudades(datos: dict) -> None:
    series   = datos["series"]
    ciudades = datos["ciudades"]
    variable = datos["variable"]

    es_precip = "precipitation" in variable
    ylabel    = "Precipitación total anual (mm)" if es_precip else "Temperatura media anual (°C)"
    titulo    = "Comparación de precipitación anual" if es_precip else "Comparación de temperatura media anual"
    fname     = "comp_precip_ciudades.png" if es_precip else "comp_temp_ciudades.png"

    fig, ax = plt.subplots(figsize=(15, 7))
    fig.patch.set_facecolor("#0E0E0E")

    for ciudad in ciudades:
        serie = series.get(ciudad.nombre)
        if serie is None:
            continue
        ax.plot(serie.index, serie.values,
                label=ciudad.nombre.capitalize(),
                linewidth=2.2, color=ciudad.color)

    estilo_ax(ax, f"{titulo}\n({AÑO_INICIO}–{AÑO_FIN})", "Año", ylabel)
    ax.legend(title="Ciudades", fontsize=11)

    guardar_grafico(OUTPUT_DIRS["comp_ciudades"] / fname)


# ── H3: Violinplot distribución anual entre ciudades (seaborn) ────────────────
def graficar_violin_ciudades(ciudades: list) -> None:
    """
    Distribución de la temperatura media diaria por ciudad.
    Seaborn aporta aquí: violinplot con densidad KDE y quartiles.
    """
    frames = []
    for ciudad in ciudades:
        if ciudad.df is None:
            continue
        tmp = ciudad.df[["temperature_2m_mean"]].copy()
        tmp["ciudad"] = ciudad.nombre.capitalize()
        tmp["color"]  = ciudad.color
        frames.append(tmp)

    data   = pd.concat(frames, ignore_index=True)
    orden  = data.groupby("ciudad")["temperature_2m_mean"].median().sort_values().index.tolist()
    paleta = {c.nombre.capitalize(): c.color for c in ciudades}

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor("#0E0E0E")
    ax.set_facecolor("#0E0E0E")

    sns.violinplot(
        data=data, x="ciudad", y="temperature_2m_mean",
        hue="ciudad", order=orden, palette=paleta, legend=False,
        inner="quartile", linewidth=1.2, ax=ax,
    )
    ax.set_facecolor("#0E0E0E")

    ax.set_title(
        f"Distribución de temperatura media diaria por ciudad\n({AÑO_INICIO}–{AÑO_FIN})",
        fontsize=14, fontweight="bold", color="#D0D0D0", pad=15,
    )
    ax.set_xlabel("Ciudad", fontsize=11, color="#D0D0D0")
    ax.set_ylabel("Temperatura media diaria (°C)", fontsize=11, color="#D0D0D0")
    ax.tick_params(colors="#686868")
    ax.grid(axis="y", color="#303030", linestyle="--", alpha=0.6)
    ax.spines[["top", "right"]].set_visible(False)

    guardar_grafico(OUTPUT_DIRS["comp_ciudades"] / "violin_temp_ciudades.png")


# ── H5: Estacionalidad por quinquenios ────────────────────────────────────────
def graficar_estacionalidad(resultados: list[dict]) -> None:
    """
    Ciclo anual de temperatura media mensual agrupado por quinquenios.
    Paleta secuencial azul→rojo: décadas antiguas en azul, recientes en rojo.
    La dirección del color comunica directamente el calentamiento temporal.
    """
    n_periodos = max(len(r["periodos"]) for r in resultados)
    cmap       = plt.cm.get_cmap("RdYlBu_r", n_periodos)

    for r in resultados:
        ciudad   = r["ciudad"]
        periodos = r["periodos"]

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#0E0E0E")

        n = len(periodos)
        for i, (periodo, mensual) in enumerate(periodos.items()):
            color = cmap(i / max(n - 1, 1))
            lw    = 2.5 if i in (0, n - 1) else 1.4
            alpha = 1.0 if i in (0, n - 1) else 0.65
            ax.plot(mensual.index, mensual.values,
                    label=periodo, linewidth=lw, color=color, alpha=alpha)

        sm = cm.ScalarMappable(cmap="RdYlBu_r",
                               norm=mcolors.Normalize(vmin=0, vmax=n - 1))
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, shrink=0.6, pad=0.01)
        cbar.set_label("Quinquenio (0=antiguo → reciente)", fontsize=9, color="#D0D0D0")
        cbar.set_ticks([0, (n - 1) / 2, n - 1])
        etiquetas = list(periodos.keys())
        cbar.set_ticklabels([etiquetas[0], etiquetas[n // 2], etiquetas[-1]])
        cbar.ax.tick_params(labelsize=8, colors="#686868")

        ax.set_title(
            f"Estacionalidad de la temperatura media mensual\n"
            f"{ciudad.nombre.capitalize()} (quinquenios {AÑO_INICIO}–{AÑO_FIN})",
            fontsize=14, fontweight="bold", color="#D0D0D0", pad=15,
        )
        ax.set_xlabel("Mes", fontsize=11, color="#D0D0D0")
        ax.set_ylabel("Temperatura media (°C)", fontsize=11, color="#D0D0D0")
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(MESES)
        ax.tick_params(colors="#686868")
        ax.grid(axis="y", color="#303030", linestyle="--", alpha=0.5)
        ax.spines[["top", "right"]].set_visible(False)

        guardar_grafico(OUTPUT_DIRS["estacionalidad"] / f"estacionalidad_{ciudad.nombre}.png")


# ── H5: Amplitud térmica por quinquenios entre ciudades ──────────────────────
def graficar_amplitud_termica(resultados: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(15, 7))
    fig.patch.set_facecolor("#0E0E0E")
    ax.set_facecolor("#0E0E0E")

    for r in resultados:
        ciudad     = r["ciudad"]
        amplitudes = r["amplitudes"]
        etiquetas  = list(amplitudes.keys())
        valores    = list(amplitudes.values())

        ax.plot(etiquetas, valores,
                label=ciudad.nombre.capitalize(),
                linewidth=2.2, color=ciudad.color, marker="o")

    ax.set_title(
        f"Variación de la amplitud térmica estacional por quinquenios\n({AÑO_INICIO}–{AÑO_FIN})",
        fontsize=14, fontweight="bold", color="#D0D0D0", pad=15,
    )
    ax.set_xlabel("Periodo (5 años)", fontsize=11, color="#D0D0D0")
    ax.set_ylabel("Amplitud térmica (°C)", fontsize=11, color="#D0D0D0")
    ax.tick_params(colors="#686868")
    plt.xticks(rotation=45)
    ax.grid(axis="y", color="#303030", linestyle="--", alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Ciudades", fontsize=11)

    guardar_grafico(OUTPUT_DIRS["estacionalidad"] / "amplitud_termica_ciudades.png")
