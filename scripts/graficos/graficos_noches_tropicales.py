"""
Gráficos de noches tropicales (Tmin >= 20°C) y noches muy cálidas (Tmin >= 25°C)
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN, WINDOW
from scripts.funciones_variables import estilo_ax, guardar_grafico


def _tendencia(x: float) -> str:
    """Formatea una tendencia con signo y un decimal, sin mostrar '-0.0'."""
    return f"{round(x, 1) + 0.0:+.1f}"


def graficar_noches_anuales(resultados_20: list[dict],
                             resultados_25: list[dict]) -> None:
    """
    Una figura por ciudad con dos series solapadas:
    barras de 20°C (azul oscuro) + barras de 25°C encima (rojo),
    media móvil y tendencia para el umbral de 20°C.
    """
    r25_by_ciudad = {r["ciudad"].nombre: r for r in resultados_25}

    for r in resultados_20:
        ciudad  = r["ciudad"]
        años    = r["años"]
        noches  = np.array(r["noches"])
        r25     = r25_by_ciudad.get(ciudad.nombre)

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#0E0E0E")

        ax.bar(años, noches, color="#1D4ED8", alpha=0.6, width=0.8,
               zorder=2, label="Tmin ≥ 20°C")

        if r25 is not None:
            noches_25 = np.array(r25["noches"])
            ax.bar(años, noches_25, color="#EF4444", alpha=0.8, width=0.8,
                   zorder=3, label="Tmin ≥ 25°C")

        ax.plot(r["años_mm"], r["media_movil"],
                color="#D0D0D0", linewidth=2.5,
                label=f"Media móvil {WINDOW} años (≥20°C)", zorder=4)

        ax.plot(años, r["tendencia"],
                color="#686868", linewidth=1.8, linestyle="--",
                label=f"Tendencia: {_tendencia(r['slope'] * 10)} noches/década "
                      f"(p={r['p_value']:.3f})", zorder=4)

        estilo_ax(ax,
                  f"Noches tropicales por año\n"
                  f"{ciudad.nombre.capitalize()} ({AÑO_INICIO}–{AÑO_FIN})",
                  "Año", "Noches (días)")
        ax.legend(fontsize=10)

        idx_max = int(np.argmax(noches))
        ax.annotate(f"{int(noches[idx_max])} noches",
                    xy=(años[idx_max], noches[idx_max]),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", fontsize=9, color="#1D4ED8", fontweight="bold")

        guardar_grafico(OUTPUT_DIRS["noches_tropicales"] /
                        f"noches_{ciudad.nombre}.png")


def graficar_noches_comparativa(resultados_20: list[dict],
                                 resultados_25: list[dict]) -> None:
    """
    Dos paneles: panel superior = ≥20°C, panel inferior = ≥25°C.
    Media móvil de cada ciudad para comparar costeras vs. interior.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    fig.patch.set_facecolor("#0E0E0E")

    for resultados, ax, titulo in [
        (resultados_20, ax1, f"Noches tropicales (Tmin ≥ 20°C) · media móvil {WINDOW} años"),
        (resultados_25, ax2, f"Noches muy cálidas (Tmin ≥ 25°C) · media móvil {WINDOW} años"),
    ]:
        ax.set_facecolor("#0E0E0E")
        for r in resultados:
            ciudad = r["ciudad"]
            ax.plot(r["años"], r["noches"],
                    color=ciudad.color, linewidth=1, alpha=0.2)
            ax.plot(r["años_mm"], r["media_movil"],
                    color=ciudad.color, linewidth=2.2,
                    label=f"{ciudad.nombre.capitalize()} "
                          f"({_tendencia(r['slope'] * 10)} n/déc.)")

        ax.set_title(titulo, fontsize=12, fontweight="bold", color="#D0D0D0", pad=8)
        ax.set_ylabel("Noches por año", fontsize=11, color="#D0D0D0")
        ax.tick_params(colors="#686868")
        ax.grid(axis="y", color="#303030", linestyle="--", alpha=0.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(title="Ciudades (tendencia/déc.)", fontsize=9, ncol=2)

    ax2.set_xlabel("Año", fontsize=11, color="#D0D0D0")
    fig.suptitle(
        f"Evolución de las noches cálidas · Euskal Herria ({AÑO_INICIO}–{AÑO_FIN})",
        fontsize=14, fontweight="bold", color="#D0D0D0",
    )

    guardar_grafico(OUTPUT_DIRS["noches_tropicales"] / "noches_comparativa.png")


def graficar_noches_tropicales_comparativa(resultados_20: list[dict]) -> None:
    """
    Versión de un solo panel de graficar_noches_comparativa: solo ≥20°C.
    Media móvil de cada ciudad para comparar costeras vs. interior.
    """
    fig, ax = plt.subplots(figsize=(15, 6))
    fig.patch.set_facecolor("#0E0E0E")
    ax.set_facecolor("#0E0E0E")

    for r in resultados_20:
        ciudad = r["ciudad"]
        ax.plot(r["años"], r["noches"],
                color=ciudad.color, linewidth=1, alpha=0.2)
        ax.plot(r["años_mm"], r["media_movil"],
                color=ciudad.color, linewidth=2.2,
                label=f"{ciudad.nombre.capitalize()} "
                      f"({_tendencia(r['slope'] * 10)} n/déc.)")

    ax.set_title(f"Noches tropicales (Tmin ≥ 20°C) · media móvil {WINDOW} años",
                 fontsize=12, fontweight="bold", color="#D0D0D0", pad=8)
    ax.set_xlabel("Año", fontsize=11, color="#D0D0D0")
    ax.set_ylabel("Noches por año", fontsize=11, color="#D0D0D0")
    ax.tick_params(colors="#686868")
    ax.grid(axis="y", color="#303030", linestyle="--", alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Ciudades (tendencia/déc.)", fontsize=9, ncol=2)

    fig.suptitle(
        f"Evolución de las noches tropicales · Euskal Herria ({AÑO_INICIO}–{AÑO_FIN})",
        fontsize=14, fontweight="bold", color="#D0D0D0",
    )

    guardar_grafico(OUTPUT_DIRS["noches_tropicales"] / "noches_tropicales_comparativa.png")


def graficar_calendario_noches(resultados: list[dict],
                                sufijo: str = "tropicales") -> None:
    """
    Heatmap ciudad × año coloreado por número de noches.
    Permite ver de un vistazo los años más cálidos y si el patrón es sincrónico.
    """
    rows = []
    for r in resultados:
        for año, n in zip(r["años"], r["noches"]):
            rows.append({
                "ciudad": r["ciudad"].nombre.capitalize(),
                "año":    año,
                "noches": n,
            })

    data  = pd.DataFrame(rows)
    pivot = data.pivot(index="ciudad", columns="año", values="noches").fillna(0)
    pivot = pivot.loc[:, pivot.columns >= 1960]

    fig, ax = plt.subplots(figsize=(18, 4))
    fig.patch.set_facecolor("#0E0E0E")

    umbral_val = resultados[0]["umbral"]
    sns.heatmap(
        pivot, ax=ax,
        cmap="YlOrRd",
        linewidths=0.3,
        linecolor="#0E0E0E",
        cbar_kws={"label": f"Noches con Tmin ≥ {umbral_val:.0f}°C", "shrink": 0.7},
        yticklabels=True,
        xticklabels=5,
    )

    ax.set_title(
        f"Noches con Tmin ≥ {umbral_val:.0f}°C por ciudad y año\n"
        f"({pivot.columns.min()}–{pivot.columns.max()})",
        fontsize=13, fontweight="bold", color="#D0D0D0", pad=12,
    )
    ax.set_xlabel("Año", fontsize=11, color="#D0D0D0")
    ax.set_ylabel("", fontsize=11)
    ax.tick_params(colors="#686868", axis="x", rotation=45)
    ax.tick_params(colors="#686868", axis="y", rotation=0)

    guardar_grafico(OUTPUT_DIRS["noches_tropicales"] /
                    f"calendario_noches_{sufijo}.png")
