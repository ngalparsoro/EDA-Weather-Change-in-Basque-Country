"""
Heatmap de concentración estacional de extremos — ¿en qué mes caen los días >35°C?
"""
import matplotlib.pyplot as plt
import seaborn as sns
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN
from scripts.funciones_variables import guardar_grafico


def graficar_concentracion_mensual(resultados: list[dict]) -> None:
    """
    Heatmap quinquenio × mes para cada ciudad.
    Permite ver si los días extremos se concentran cada vez más en julio
    o se extienden a junio y agosto en las décadas recientes.
    """
    for r in resultados:
        ciudad = r["ciudad"]
        pivot  = r["pivot"]
        umbral = r["umbral"]

        if pivot.empty:
            continue

        fig, ax = plt.subplots(figsize=(12, max(4, len(pivot) * 0.45)))
        fig.patch.set_facecolor("#0E0E0E")

        sns.heatmap(
            pivot, ax=ax,
            cmap="YlOrRd",
            linewidths=0.4,
            linecolor="#0E0E0E",
            annot=True, fmt=".0f", annot_kws={"size": 8},
            cbar_kws={"label": f"Días con Tmax > {umbral:.0f}°C", "shrink": 0.7},
        )

        ax.set_title(
            f"Concentración mensual de días extremos (Tmax > {umbral:.0f}°C)\n"
            f"{ciudad.nombre.capitalize()} · por quinquenio ({AÑO_INICIO}–{AÑO_FIN})",
            fontsize=13, fontweight="bold", color="#D0D0D0", pad=12,
        )
        ax.set_xlabel("Mes", fontsize=11, color="#D0D0D0")
        ax.set_ylabel("Quinquenio", fontsize=11, color="#D0D0D0")
        ax.tick_params(colors="#686868", axis="x", rotation=0)
        ax.tick_params(colors="#686868", axis="y", rotation=0)

        guardar_grafico(
            OUTPUT_DIRS["extremos_35"] / f"concentracion_mensual_{ciudad.nombre}.png"
        )
