"""
Gráficos de anomalía térmica anual — refuerzo H1
"""
import numpy as np
import matplotlib.pyplot as plt
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN
from scripts.funciones_variables import estilo_ax, guardar_grafico


def graficar_anomalia(resultados: list[dict]) -> None:
    """
    Barras azul/rojo clásicas de anomalía térmica respecto al período base OMM.
    Una figura por ciudad.
    """
    for r in resultados:
        ciudad   = r["ciudad"]
        años     = r["años"]
        anomalia = np.array(r["anomalia"])
        p_ini, p_fin = r["periodo_base"]

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#0E0E0E")

        colors = ["#EF4444" if a >= 0 else "#3B82F6" for a in anomalia]
        ax.bar(años, anomalia, color=colors, alpha=0.8, width=0.8, zorder=2)

        ax.plot(r["años_mm"], r["media_movil"],
                color="#D0D0D0", linewidth=2.5,
                label="Media móvil 10 años", zorder=3)

        ax.axhline(0, color="#94A3B8", linewidth=1, zorder=1)
        ax.axvspan(p_ini, p_fin, alpha=0.06, color="#D0D0D0",
                   label=f"Período base ({p_ini}–{p_fin})")

        estilo_ax(ax,
                  f"Anomalía de temperatura media anual\n{ciudad.nombre.capitalize()} "
                  f"(respecto a media {p_ini}–{p_fin})",
                  "Año", "Anomalía (°C)")
        ax.legend(fontsize=10)

        idx_max = np.argmax(anomalia)
        ax.annotate(f"+{anomalia[idx_max]:.2f}°C",
                    xy=(años[idx_max], anomalia[idx_max]),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", fontsize=9, color="#EF4444", fontweight="bold")

        guardar_grafico(OUTPUT_DIRS["temp_media"] / f"anomalia_{ciudad.nombre}.png")


def graficar_anomalia_comparativa(resultados: list[dict]) -> None:
    """
    Todas las ciudades en un mismo gráfico de líneas de anomalía.
    Permite ver si el calentamiento es sincrónico entre ciudades.
    """
    fig, ax = plt.subplots(figsize=(15, 7))
    fig.patch.set_facecolor("#0E0E0E")
    ax.set_facecolor("#0E0E0E")

    for r in resultados:
        ciudad = r["ciudad"]
        ax.plot(r["años"], r["anomalia"],
                color=ciudad.color, linewidth=1.2, alpha=0.35)
        ax.plot(r["años_mm"], r["media_movil"],
                color=ciudad.color, linewidth=2.2,
                label=ciudad.nombre.capitalize())

    ax.axhline(0, color="#94A3B8", linewidth=1.2, linestyle="--")

    p_ini, p_fin = resultados[0]["periodo_base"]
    ax.axvspan(p_ini, p_fin, alpha=0.05, color="#D0D0D0",
               label=f"Período base ({p_ini}–{p_fin})")

    estilo_ax(ax,
              f"Anomalía de temperatura media anual por ciudad\n"
              f"(respecto a media {p_ini}–{p_fin}, media móvil 10 años)",
              "Año", "Anomalía (°C)")
    ax.legend(title="Ciudades", fontsize=10)

    guardar_grafico(OUTPUT_DIRS["temp_media"] / "anomalia_comparativa.png")
