"""
Gráficos de clustering jerárquico de ciudades — refuerzo H3
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN


def graficar_dendrograma(datos: dict) -> None:
    """
    Dendrograma de clustering jerárquico (Ward).
    Las ciudades más cercanas en el árbol tienen perfiles climáticos más similares.
    """
    perfil   = datos["perfil"]
    Z        = datos["linkage"]
    ciudades = datos["ciudades"]

    labels  = perfil["ciudad"].str.capitalize().tolist()
    colores = {c.nombre.capitalize(): c.color for c in ciudades}

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    dend = dendrogram(
        Z,
        labels=labels,
        ax=ax,
        leaf_font_size=12,
        color_threshold=0,
        above_threshold_color="#475569",
    )

    # Colorear etiquetas según color de ciudad
    for lbl in ax.get_xticklabels():
        texto = lbl.get_text()
        lbl.set_color(colores.get(texto, "#021B2E"))
        lbl.set_fontweight("bold")

    ax.set_title(
        f"Clustering jerárquico de ciudades por perfil climático\n"
        f"(Ward, 10 variables estandarizadas, {AÑO_INICIO}–{AÑO_FIN})",
        fontsize=13, fontweight="bold", color="#021B2E", pad=12,
    )
    ax.set_ylabel("Distancia (Ward)", fontsize=11, color="#021B2E")
    ax.set_xlabel("")
    ax.tick_params(colors="#475569")
    ax.grid(axis="y", color="#CBD5E1", linestyle="--", alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIRS["comp_ciudades"] / "dendrograma_ciudades.png",
                dpi=180, bbox_inches="tight")
    plt.show()


def graficar_heatmap_perfil(datos: dict) -> None:
    """
    Heatmap de las variables climáticas estandarizadas por ciudad.
    Seaborn: permite ver qué variables diferencian cada grupo.
    """
    perfil   = datos["perfil"]
    features = datos["features"]
    ciudades = datos["ciudades"]

    labels_es = {
        "temp_media":   "Temp. media",
        "temp_max":     "Temp. máx. media",
        "temp_min":     "Temp. mín. media",
        "amplitud":     "Amplitud térmica",
        "precip_anual": "Precipitación anual",
        "dias_30":      "Días Tmax > 30°C",
        "dias_35":      "Días Tmax > 35°C",
        "dias_intensos":"Días precip > 30 mm",
        "racha_seca":   "Racha seca máx.",
        "variab_temp":  "Variabilidad interanual",
    }

    from sklearn.preprocessing import StandardScaler
    X_scaled = StandardScaler().fit_transform(perfil[features].values)

    import pandas as pd
    df_heat = pd.DataFrame(
        X_scaled,
        index=perfil["ciudad"].str.capitalize(),
        columns=[labels_es.get(f, f) for f in features],
    )

    # Ordenar ciudades por grupo
    df_heat["grupo"] = datos["grupos"]
    df_heat = df_heat.sort_values("grupo").drop(columns="grupo")

    paleta_ciudades = {c.nombre.capitalize(): c.color for c in ciudades}
    row_colors = pd.Series(
        [paleta_ciudades.get(c, "#94A3B8") for c in df_heat.index],
        index=df_heat.index, name="Ciudad"
    )

    g = sns.clustermap(
        df_heat,
        row_cluster=True,
        col_cluster=True,
        cmap="RdBu_r",
        center=0,
        linewidths=0.5,
        figsize=(14, 7),
        row_colors=row_colors,
        cbar_pos=(0.02, 0.8, 0.03, 0.15),
        dendrogram_ratio=(0.15, 0.1),
    )

    g.figure.suptitle(
        f"Perfil climático por ciudad (variables estandarizadas)\n({AÑO_INICIO}–{AÑO_FIN})",
        fontsize=13, fontweight="bold", color="#021B2E", y=1.02,
    )
    g.figure.patch.set_facecolor("#F8F9FA")

    # Leyenda de colores
    leyenda = [mpatches.Patch(color=c.color, label=c.nombre.capitalize())
               for c in ciudades]
    g.ax_heatmap.legend(handles=leyenda, loc="upper right",
                        bbox_to_anchor=(1.25, 1.1), fontsize=9, title="Ciudad")

    plt.savefig(OUTPUT_DIRS["comp_ciudades"] / "heatmap_perfil_climatico.png",
                dpi=180, bbox_inches="tight")
    plt.show()
