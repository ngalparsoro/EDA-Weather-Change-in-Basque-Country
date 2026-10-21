"""
Gráficos de longitud del verano meteorológico — refuerzo H5
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scripts.variables import OUTPUT_DIRS, AÑO_INICIO, AÑO_FIN, CIUDADES, WINDOW
from scripts.funciones_variables import estilo_ax, media_movil, guardar_grafico
from scripts.analisis.verano_meteorologico import _longitud_verano_anual


def graficar_longitud_verano(resultados: list[dict]) -> None:
    """Longitud del verano por año con tendencia. Una figura por ciudad."""
    for r in resultados:
        ciudad = r["ciudad"]
        años   = r["años"]
        dias   = np.array(r["dias"])

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#0E0E0E")

        colors = ["#0D9488" if d <= 30 else "#F59E0B" if d <= 60 else "#EF4444"
                  for d in dias]
        ax.bar(años, dias, color=colors, alpha=0.75, width=0.8, zorder=2)

        ax.plot(r["años_mm"], r["media_movil"],
                color="#D0D0D0", linewidth=2.5,
                label=f"Media móvil {WINDOW} años", zorder=3)

        ax.plot(años, r["tendencia"],
                color="#686868", linewidth=1.8, linestyle="--",
                label=f"Tendencia ({r['slope'] * 10:+.1f} días/década)", zorder=3)

        estilo_ax(ax,
                  f"Longitud del verano meteorológico\n{ciudad.nombre.capitalize()} "
                  f"(días consecutivos con Tmedia > {r['umbral']:.0f}°C, {AÑO_INICIO}–{AÑO_FIN})",
                  "Año", "Días de verano meteorológico")
        ax.legend(fontsize=10)

        idx_max = np.argmax(dias)
        ax.annotate(f"{int(dias[idx_max])} días",
                    xy=(años[idx_max], dias[idx_max]),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", fontsize=9, color="#EF4444", fontweight="bold")

        guardar_grafico(OUTPUT_DIRS["estacionalidad"] / f"verano_{ciudad.nombre}.png")


def graficar_verano_comparativa(resultados: list[dict]) -> None:
    """
    Media móvil de la longitud del verano para todas las ciudades.
    Permite ver si el verano se alarga más en el interior que en la costa.
    """
    fig, ax = plt.subplots(figsize=(15, 7))
    fig.patch.set_facecolor("#0E0E0E")
    ax.set_facecolor("#0E0E0E")

    for r in resultados:
        ciudad = r["ciudad"]
        ax.plot(r["años"], r["dias"],
                color=ciudad.color, linewidth=1, alpha=0.25)
        ax.plot(r["años_mm"], r["media_movil"],
                color=ciudad.color, linewidth=2.2,
                label=f"{ciudad.nombre.capitalize()} ({r['slope'] * 10:+.1f} d/déc.)")

    estilo_ax(ax,
              f"Longitud del verano meteorológico por ciudad\n"
              f"(media móvil {WINDOW} años, Tmedia > {resultados[0]['umbral']:.0f}°C, {AÑO_INICIO}–{AÑO_FIN})",
              "Año", "Días de verano meteorológico")
    ax.legend(title="Ciudades (tendencia/década)", fontsize=10)

    guardar_grafico(OUTPUT_DIRS["estacionalidad"] / "verano_comparativa.png")


def graficar_boxplot_verano_decadas(ciudades: list = None) -> None:
    """
    Distribución de la longitud del verano por décadas y ciudad.
    Seaborn: boxplot para ver cómo cambia la mediana y dispersión.
    """
    ciudades = ciudades or [c for c in CIUDADES if c.df is not None]
    frames   = []
    for ciudad in ciudades:
        serie = _longitud_verano_anual(ciudad.df)
        tmp   = serie.reset_index()
        tmp.columns = ["año", "dias"]
        tmp["ciudad"] = ciudad.nombre.capitalize()
        tmp["decada"] = (tmp["año"] // 10 * 10).astype(str) + "s"
        frames.append(tmp)

    data   = pd.concat(frames, ignore_index=True)
    paleta = {c.nombre.capitalize(): c.color for c in ciudades}

    fig, ax = plt.subplots(figsize=(16, 7))
    fig.patch.set_facecolor("#0E0E0E")
    ax.set_facecolor("#0E0E0E")

    sns.boxplot(
        data=data, x="decada", y="dias", hue="ciudad",
        palette=paleta, notch=False,
        linewidth=1.0, flierprops={"marker": ".", "alpha": 0.3},
        ax=ax,
    )
    ax.set_facecolor("#0E0E0E")

    ax.set_title(
        f"Distribución de la longitud del verano meteorológico por décadas\n({AÑO_INICIO}–{AÑO_FIN})",
        fontsize=14, fontweight="bold", color="#D0D0D0", pad=15,
    )
    ax.set_xlabel("Década", fontsize=11, color="#D0D0D0")
    ax.set_ylabel("Días de verano meteorológico", fontsize=11, color="#D0D0D0")
    ax.tick_params(colors="#686868")
    ax.grid(axis="y", color="#303030", linestyle="--", alpha=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Ciudad", fontsize=9, ncol=2)

    guardar_grafico(OUTPUT_DIRS["estacionalidad"] / "boxplot_verano_decadas.png")


def graficar_inicio_fin_verano(resultados: list[dict]) -> None:
    """
    Evolución temporal del día de inicio y fin del verano meteorológico.
    Inicio descendente = el verano empieza antes.
    Fin ascendente     = el verano termina más tarde.
    """
    MESES_DOY = {1: "Ene", 32: "Feb", 60: "Mar", 91: "Abr", 121: "May",
                 152: "Jun", 182: "Jul", 213: "Ago", 244: "Sep",
                 274: "Oct", 305: "Nov", 335: "Dic"}

    for r in resultados:
        if r.get("vacio"):
            continue

        ciudad  = r["ciudad"]
        años    = r["años"]
        inicios = np.array(r["inicios"])
        fines   = np.array(r["fines"])

        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#0E0E0E")

        ax.plot(años, inicios, color="#0EA5E9", linewidth=1.8, alpha=0.7,
                label="Inicio del verano", marker="o", markersize=3)
        ax.plot(años, fines, color="#EF4444", linewidth=1.8, alpha=0.7,
                label="Fin del verano", marker="o", markersize=3)

        años_arr = np.array(años)
        for valores, color, slope, p, etiqueta in [
            (inicios, "#0369A1", r["slope_inicio"], r["p_inicio"], "inicio"),
            (fines,   "#B91C1C", r["slope_fin"],    r["p_fin"],    "fin"),
        ]:
            z     = np.polyfit(años_arr, valores, 1)
            trend = np.poly1d(z)(años_arr)
            p_str = f"p={p:.3f}"
            sig   = " ✓" if p < 0.05 else " ~"
            ax.plot(años_arr, trend, color=color, linewidth=2, linestyle="--",
                    label=f"Tendencia {etiqueta}: {slope:+.1f} d/déc. ({p_str}{sig})",
                    zorder=3)

        ticks_doy = sorted(MESES_DOY.keys())
        visible   = [t for t in ticks_doy if inicios.min() - 20 <= t <= fines.max() + 20]
        ax.set_yticks(visible)
        ax.set_yticklabels([MESES_DOY[t] for t in visible])

        estilo_ax(ax,
                  f"Inicio y fin del verano meteorológico\n"
                  f"{ciudad.nombre.capitalize()} (Tmedia > {r['umbral']:.0f}°C, {AÑO_INICIO}–{AÑO_FIN})",
                  "Año", "Mes del año", x_multiple=10)
        ax.legend(fontsize=9)

        guardar_grafico(OUTPUT_DIRS["estacionalidad"] / f"inicio_fin_verano_{ciudad.nombre}.png")


def graficar_inicio_fin_comparativa(resultados: list[dict]) -> None:
    """
    Tendencia del inicio y fin del verano para todas las ciudades.
    Panel superior = inicio. Panel inferior = fin.
    """
    MESES_DOY = {121: "May", 152: "Jun", 182: "Jul",
                 213: "Ago", 244: "Sep", 274: "Oct"}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    fig.patch.set_facecolor("#0E0E0E")

    paleta = {c.nombre: c.color for c in CIUDADES}

    for r in resultados:
        if r.get("vacio"):
            continue
        ciudad  = r["ciudad"]
        años    = np.array(r["años"])
        inicios = np.array(r["inicios"])
        fines   = np.array(r["fines"])
        color   = paleta.get(ciudad.nombre, "#94A3B8")

        if len(inicios) >= WINDOW:
            mm_ini  = media_movil(inicios)
            mm_fin  = media_movil(fines)
            años_mm = años[WINDOW - 1:]
            ax1.plot(años_mm, mm_ini, color=color, linewidth=2.2,
                     label=f"{ciudad.nombre.capitalize()} ({r['slope_inicio']:+.1f} d/déc.)")
            ax2.plot(años_mm, mm_fin, color=color, linewidth=2.2,
                     label=f"{ciudad.nombre.capitalize()} ({r['slope_fin']:+.1f} d/déc.)")

    for ax, titulo, yticks in [
        (ax1, "Inicio del verano (media móvil 10 años)", [152, 182, 213]),
        (ax2, "Fin del verano (media móvil 10 años)",    [213, 244, 274]),
    ]:
        ax.set_title(titulo, fontsize=12, fontweight="bold", color="#D0D0D0")
        ax.set_yticks(yticks)
        ax.set_yticklabels([MESES_DOY.get(t, str(t)) for t in yticks])
        ax.tick_params(colors="#686868")
        ax.grid(axis="y", color="#303030", linestyle="--", alpha=0.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(title="Ciudades (tendencia/déc.)", fontsize=9, ncol=2)

    ax2.set_xlabel("Año", fontsize=11, color="#D0D0D0")
    fig.suptitle(
        f"Evolución del inicio y fin del verano meteorológico\n"
        f"({AÑO_INICIO}–{AÑO_FIN}, Tmedia > 20°C)",
        fontsize=14, fontweight="bold", color="#D0D0D0",
    )

    guardar_grafico(OUTPUT_DIRS["estacionalidad"] / "inicio_fin_verano_comparativa.png")
