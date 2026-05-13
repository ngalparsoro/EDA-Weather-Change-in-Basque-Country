"""
Gráficos de estacionalidad y comparativa entre ciudades — H3 y H5
Recibe los dicts calculados por analisis/estacionalidad.py
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN
from scripts.funciones_variables import estilo_ax

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
    fig.patch.set_facecolor("#F8F9FA")

    for ciudad in ciudades:
        serie = series.get(ciudad.nombre)
        if serie is None:
            continue
        ax.plot(serie.index, serie.values,
                label=ciudad.nombre.capitalize(),
                linewidth=2.2, color=ciudad.color)

    estilo_ax(ax, f"{titulo}\n({AÑO_INICIO}–{AÑO_FIN})", "Año", ylabel)
    ax.legend(title="Ciudades", fontsize=11)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["comp_ciudades"] / fname, dpi=180, bbox_inches="tight")
    plt.show()


# ── H3: Violinplot distribución anual entre ciudades (seaborn) ────────────────
def graficar_violin_ciudades(ciudades: list) -> None:
    """
    Distribución de la temperatura media diaria por ciudad.
    Seaborn aporta aquí: violinplot con densidad KDE y quartiles.
    """
    import pandas as pd

    frames = []
    for ciudad in ciudades:
        if ciudad.df is None:
            continue
        tmp = ciudad.df[["temperature_2m_mean"]].copy()
        tmp["ciudad"] = ciudad.nombre.capitalize()
        tmp["color"]  = ciudad.color
        frames.append(tmp)

    data = pd.concat(frames, ignore_index=True)
    orden = data.groupby("ciudad")["temperature_2m_mean"].median().sort_values().index.tolist()
    paleta = {c.nombre.capitalize(): c.color for c in ciudades}

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    sns.violinplot(
        data=data, x="ciudad", y="temperature_2m_mean",
        order=orden, palette=paleta,
        inner="quartile", linewidth=1.2, ax=ax,
    )

    ax.set_title(
        f"Distribución de temperatura media diaria por ciudad\n({AÑO_INICIO}–{AÑO_FIN})",
        fontsize=14, fontweight="bold", color="#021B2E", pad=15,
    )
    ax.set_xlabel("Ciudad", fontsize=11, color="#021B2E")
    ax.set_ylabel("Temperatura media diaria (°C)", fontsize=11, color="#021B2E")
    ax.tick_params(colors="#475569")
    ax.grid(axis="y", color="#CBD5E1", linestyle="--", alpha=0.6)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["comp_ciudades"] / "violin_temp_ciudades.png",
                dpi=180, bbox_inches="tight")
    plt.show()


# ── H5: Estacionalidad por quinquenios ────────────────────────────────────────
def graficar_estacionalidad(resultados: list[dict]) -> None:
    n_periodos = max(len(r["periodos"]) for r in resultados)
    cmap       = plt.cm.get_cmap("turbo", n_periodos)
    colores    = [cmap(i) for i in range(n_periodos)]

    for r in resultados:
        ciudad   = r["ciudad"]
        periodos = r["periodos"]

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#F8F9FA")

        for (periodo, mensual), color in zip(periodos.items(), colores):
            ax.plot(mensual.index, mensual.values,
                    label=periodo, linewidth=1.8, color=color, alpha=0.8)

        ax.set_title(
            f"Estacionalidad de la temperatura media mensual\n{ciudad.nombre.capitalize()} (quinquenios {AÑO_INICIO}–{AÑO_FIN})",
            fontsize=14, fontweight="bold", color="#021B2E", pad=15,
        )
        ax.set_xlabel("Mes", fontsize=11, color="#021B2E")
        ax.set_ylabel("Temperatura media (°C)", fontsize=11, color="#021B2E")
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(MESES)
        ax.tick_params(colors="#475569")
        ax.grid(axis="y", color="#CBD5E1", linestyle="--", alpha=0.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(title="Periodos (5 años)", fontsize=9, ncol=3)

        plt.tight_layout()
        plt.savefig(OUTPUT_DIRS["estacionalidad"] / f"estacionalidad_{ciudad.nombre}.png",
                    dpi=180, bbox_inches="tight")
        plt.show()


# ── H5: Amplitud térmica por quinquenios entre ciudades ──────────────────────
def graficar_amplitud_termica(resultados: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(15, 7))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

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
        fontsize=14, fontweight="bold", color="#021B2E", pad=15,
    )
    ax.set_xlabel("Periodo (5 años)", fontsize=11, color="#021B2E")
    ax.set_ylabel("Amplitud térmica (°C)", fontsize=11, color="#021B2E")
    ax.tick_params(colors="#475569")
    plt.xticks(rotation=45)
    ax.grid(axis="y", color="#CBD5E1", linestyle="--", alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Ciudades", fontsize=11)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["estacionalidad"] / "amplitud_termica_ciudades.png",
                dpi=180, bbox_inches="tight")
    plt.show()
