"""
Gráficos de clustering jerárquico de ciudades — refuerzo H3
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram
from sklearn.preprocessing import StandardScaler
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN
from scripts.funciones_variables import guardar_grafico


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
    fig.patch.set_facecolor("#0E0E0E")
    ax.set_facecolor("#0E0E0E")

    dend = dendrogram(
        Z,
        labels=labels,
        ax=ax,
        leaf_font_size=12,
        color_threshold=0,
        above_threshold_color="#686868",
    )

    # Colorear etiquetas según color de ciudad
    for lbl in ax.get_xticklabels():
        texto = lbl.get_text()
        lbl.set_color(colores.get(texto, "#D0D0D0"))
        lbl.set_fontweight("bold")

    ax.set_title(
        f"Clustering jerárquico de ciudades por perfil climático\n"
        f"(Ward, 10 variables estandarizadas, {AÑO_INICIO}–{AÑO_FIN})",
        fontsize=13, fontweight="bold", color="#D0D0D0", pad=12,
    )
    ax.set_ylabel("Distancia (Ward)", fontsize=11, color="#D0D0D0")
    ax.set_xlabel("")
    ax.tick_params(colors="#686868")
    ax.grid(axis="y", color="#303030", linestyle="--", alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)

    guardar_grafico(OUTPUT_DIRS["comp_ciudades"] / "dendrograma_ciudades.png")


def graficar_heatmap_perfil(datos: dict) -> None:
    """
    Heatmap de las variables climáticas estandarizadas por ciudad.
    Seaborn: permite ver qué variables diferencian cada grupo.
    """
    perfil   = datos["perfil"]
    features = datos["features"]
    ciudades = datos["ciudades"]

    labels_es = {
        "temp_media":    "Temp. media",
        "temp_max":      "Temp. máx. media",
        "temp_min":      "Temp. mín. media",
        "amplitud":      "Amplitud térmica",
        "precip_anual":  "Precipitación anual",
        "dias_30":       "Días Tmax > 30°C",
        "dias_35":       "Días Tmax > 35°C",
        "dias_intensos": "Días precip > 30 mm",
        "racha_seca":    "Racha seca máx.",
        "variab_temp":   "Variabilidad interanual",
        "trend_calent":  "Tendencia calent. (°C/déc.)",
    }

    X_scaled = StandardScaler().fit_transform(perfil[features].values)

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
        fontsize=13, fontweight="bold", color="#D0D0D0", y=1.02,
    )
    g.figure.patch.set_facecolor("#0E0E0E")
    for ax in g.figure.axes:
        ax.set_facecolor("#0E0E0E")
        ax.tick_params(colors="#686868")

    # Leyenda de colores
    leyenda = [mpatches.Patch(color=c.color, label=c.nombre.capitalize())
               for c in ciudades]
    g.ax_heatmap.legend(handles=leyenda, loc="upper right",
                        bbox_to_anchor=(1.25, 1.1), fontsize=9, title="Ciudad")

    # clustermap no admite tight_layout — guardar directamente
    plt.savefig(OUTPUT_DIRS["comp_ciudades"] / "heatmap_perfil_climatico.png",
                dpi=180, bbox_inches="tight", facecolor="#0E0E0E")
    plt.show()


def graficar_pca_loadings(datos: dict) -> None:
    """
    Biplot PCA: ciudades en el espacio de los dos primeros componentes
    y flechas de loadings que muestran qué variables generan la separación.
    """
    loadings  = datos["loadings"]
    X_pca     = datos["X_pca"]
    explained = datos["explained"]
    perfil    = datos["perfil"]
    ciudades  = datos["ciudades"]

    labels_es = {
        "temp_media":    "Temp. media",
        "temp_max":      "Temp. máx.",
        "temp_min":      "Temp. mín.",
        "amplitud":      "Amplitud",
        "precip_anual":  "Precipitación",
        "dias_30":       "Días >30°C",
        "dias_35":       "Días >35°C",
        "dias_intensos": "Días intens.",
        "racha_seca":    "Racha seca",
        "variab_temp":   "Variabilidad",
        "trend_calent":  "Tendencia",
    }

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor("#0E0E0E")
    ax.set_facecolor("#0E0E0E")

    paleta = {c.nombre: c.color for c in ciudades}
    for i, row in perfil.iterrows():
        ax.scatter(X_pca[i, 0], X_pca[i, 1],
                   color=paleta.get(row["ciudad"], "#94A3B8"),
                   s=160, zorder=3)
        ax.annotate(row["ciudad"].capitalize(),
                    (X_pca[i, 0], X_pca[i, 1]),
                    xytext=(6, 4), textcoords="offset points",
                    fontsize=10, fontweight="bold",
                    color=paleta.get(row["ciudad"], "#D0D0D0"))

    # Flechas de loadings escaladas
    escala = 2.5
    for feat, row in loadings.iterrows():
        ax.annotate("",
                    xy=(row["PC1"] * escala, row["PC2"] * escala),
                    xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color="#EF4444", lw=1.5))
        ax.text(row["PC1"] * escala * 1.12, row["PC2"] * escala * 1.12,
                labels_es.get(feat, feat),
                fontsize=8, color="#B91C1C", ha="center")

    ax.axhline(0, color="#303030", linewidth=0.8, linestyle="--")
    ax.axvline(0, color="#303030", linewidth=0.8, linestyle="--")
    ax.set_xlabel(f"PC1 ({explained[0] * 100:.1f}% varianza)", fontsize=11, color="#D0D0D0")
    ax.set_ylabel(f"PC2 ({explained[1] * 100:.1f}% varianza)", fontsize=11, color="#D0D0D0")
    ax.set_title(
        f"Biplot PCA — Variables que explican las diferencias entre ciudades\n"
        f"({explained[:2].sum() * 100:.1f}% varianza total explicada)",
        fontsize=13, fontweight="bold", color="#D0D0D0", pad=12,
    )
    ax.tick_params(colors="#686868")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color="#303030", linestyle="--", alpha=0.4)

    guardar_grafico(OUTPUT_DIRS["comp_ciudades"] / "pca_biplot_ciudades.png")
