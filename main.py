from scripts.variables import CIUDADES, crear_dirs
from scripts.funciones_variables import cargar_datos
from scripts.descargar_datos import descargar_datos

from scripts.analisis import (
    temperaturas, precipitaciones, estacionalidad, correlacion_mar,
    anomalia_termica, racha_seca, olas_calor, clustering_ciudades,
    verano_meteorologico,
)
from scripts.graficos import (
    graficos_temp, graficos_precip, graficos_estacionalidad, graficos_correlacion,
    graficos_anomalia, graficos_racha_seca, graficos_olas_calor,
    graficos_clustering, graficos_verano,
)


if __name__ == "__main__":

    # ── Setup ──────────────────────────────────────────────────────────────────
    crear_dirs()

    # ── Paso 1: Descarga (solo si no tienes los CSVs) ─────────────────────────
    # descargar_datos()

    # ── Paso 2: Carga ──────────────────────────────────────────────────────────
    cargar_datos()

    # ══════════════════════════════════════════════════════════════════════════
    # H1 — Aumento de temperaturas
    # ══════════════════════════════════════════════════════════════════════════
    datos_temp = temperaturas.calcular_todos()
    graficos_temp.graficar_dias_30(datos_temp["dias_30"])
    graficos_temp.graficar_temp_media_anual(datos_temp["temp_media"])
    graficos_temp.graficar_heatmap_temp_mensual(CIUDADES)

    # Refuerzo H1: anomalía térmica
    datos_anomalia = anomalia_termica.calcular_todos()
    graficos_anomalia.graficar_anomalia(datos_anomalia)
    graficos_anomalia.graficar_anomalia_comparativa(datos_anomalia)

    # ══════════════════════════════════════════════════════════════════════════
    # H2 — Reducción de precipitaciones
    # ══════════════════════════════════════════════════════════════════════════
    datos_precip = precipitaciones.calcular_todos()
    graficos_precip.graficar_precipitacion_anual(datos_precip["precip_anual"])
    graficos_precip.graficar_dias_intensos(datos_precip["dias_intensos"])
    graficos_precip.graficar_heatmap_precip_mensual(CIUDADES)

    # Refuerzo H2: racha seca
    datos_racha = racha_seca.calcular_todos()
    graficos_racha_seca.graficar_racha_seca(datos_racha)
    graficos_racha_seca.graficar_racha_comparativa(datos_racha)
    graficos_racha_seca.graficar_violin_rachas_decadas(CIUDADES)

    # ══════════════════════════════════════════════════════════════════════════
    # H3 — Diferencias entre ciudades
    # ══════════════════════════════════════════════════════════════════════════
    datos_estac = estacionalidad.calcular_todos()
    graficos_estacionalidad.graficar_comparativa_ciudades(datos_estac["comp_temp"])
    graficos_estacionalidad.graficar_comparativa_ciudades(datos_estac["comp_precip"])
    graficos_estacionalidad.graficar_violin_ciudades(CIUDADES)

    # Refuerzo H3: clustering
    datos_cluster = clustering_ciudades.calcular_todos()
    graficos_clustering.graficar_dendrograma(datos_cluster)
    graficos_clustering.graficar_heatmap_perfil(datos_cluster)

    # ══════════════════════════════════════════════════════════════════════════
    # H4 — Frecuencia de temperaturas extremas
    # ══════════════════════════════════════════════════════════════════════════
    graficos_temp.graficar_dias_extremos(datos_temp["dias_extremos"])
    graficos_temp.graficar_boxplot_decadas(CIUDADES)

    # Refuerzo H4: olas de calor
    datos_olas = olas_calor.calcular_todos()
    graficos_olas_calor.graficar_duracion_olas(datos_olas)
    graficos_olas_calor.graficar_calendario_olas(datos_olas)

    # ══════════════════════════════════════════════════════════════════════════
    # H5 — Estacionalidad marcada
    # ══════════════════════════════════════════════════════════════════════════
    graficos_estacionalidad.graficar_estacionalidad(datos_estac["estacionalidad"])
    graficos_estacionalidad.graficar_amplitud_termica(datos_estac["amplitud"])

    # Refuerzo H5: longitud del verano
    datos_verano = verano_meteorologico.calcular_todos()
    graficos_verano.graficar_longitud_verano(datos_verano)
    graficos_verano.graficar_verano_comparativa(datos_verano)
    graficos_verano.graficar_boxplot_verano_decadas(CIUDADES)

    # ══════════════════════════════════════════════════════════════════════════
    # Correlación distancia al mar
    # ══════════════════════════════════════════════════════════════════════════
    datos_mar = correlacion_mar.calcular_todos()
    graficos_correlacion.graficar_correlacion_paneles(datos_mar)
    graficos_correlacion.graficar_gradiente_decadas(datos_mar)
    graficos_correlacion.graficar_pairplot_variables(CIUDADES)
