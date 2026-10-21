"""
Regenera todos los gráficos del proyecto en modo batch (sin abrir ventanas).
Ejecutar con: python regenerar_graficos.py
"""
import matplotlib
matplotlib.use("Agg")  # backend sin ventanas — ANTES de cualquier import de plt

import matplotlib.pyplot as plt
plt.show = lambda: None  # no-op adicional por si algún módulo lo llama directamente

from scripts.variables import CIUDADES, crear_dirs
from scripts.funciones_variables import cargar_datos
from scripts.validacion import validar_datos
from scripts.analisis import (
    temperaturas, precipitaciones, estacionalidad, correlacion_mar,
    anomalia_termica, racha_seca, olas_calor, clustering_ciudades,
    verano_meteorologico, noches_tropicales, viento, extremos_estacionales,
)
from scripts.graficos import (
    graficos_temp, graficos_precip, graficos_estacionalidad, graficos_correlacion,
    graficos_anomalia, graficos_racha_seca, graficos_olas_calor,
    graficos_clustering, graficos_verano, graficos_noches_tropicales,
    graficos_viento, graficos_extremos_estacionales,
)

crear_dirs()
cargar_datos()
validar_datos()

ciudades = [c for c in CIUDADES if c.df is not None]

print("── H1: Temperaturas ──")
datos_temp = temperaturas.calcular_todos()
graficos_temp.graficar_dias_p90(datos_temp["dias_p90"])
graficos_temp.graficar_temp_media_anual(datos_temp["temp_media"])
graficos_temp.graficar_heatmap_temp_mensual(ciudades)
datos_anomalia = anomalia_termica.calcular_todos()
graficos_anomalia.graficar_anomalia(datos_anomalia)
graficos_anomalia.graficar_anomalia_comparativa(datos_anomalia)
print("  ✅ H1 done")

print("── H2: Precipitaciones ──")
datos_precip = precipitaciones.calcular_todos()
graficos_precip.graficar_precipitacion_anual(datos_precip["precip_anual"])
graficos_precip.graficar_dias_intensos(datos_precip["dias_intensos"])
graficos_precip.graficar_heatmap_precip_mensual(ciudades)
datos_racha = racha_seca.calcular_todos()
graficos_racha_seca.graficar_racha_seca(datos_racha)
graficos_racha_seca.graficar_racha_comparativa(datos_racha)
graficos_racha_seca.graficar_violin_rachas_decadas(ciudades)
print("  ✅ H2 done")

print("── H3: Diferencias entre ciudades ──")
datos_estac = estacionalidad.calcular_todos()
graficos_estacionalidad.graficar_comparativa_ciudades(datos_estac["comp_temp"])
graficos_estacionalidad.graficar_comparativa_ciudades(datos_estac["comp_precip"])
graficos_estacionalidad.graficar_violin_ciudades(ciudades)
datos_cluster = clustering_ciudades.calcular_todos()
graficos_clustering.graficar_dendrograma(datos_cluster)
graficos_clustering.graficar_heatmap_perfil(datos_cluster)
graficos_clustering.graficar_pca_loadings(datos_cluster)
print("  ✅ H3 done")

print("── H4: Temperaturas extremas ──")
graficos_temp.graficar_dias_extremos(datos_temp["dias_extremos"])
graficos_temp.graficar_boxplot_decadas(ciudades)
datos_olas = olas_calor.calcular_todos()
graficos_olas_calor.graficar_duracion_olas(datos_olas)
graficos_olas_calor.graficar_calendario_olas(datos_olas)
datos_olas_p95 = olas_calor.calcular_todos_p95()
graficos_olas_calor.graficar_calendario_olas_p95(datos_olas_p95)
datos_noches = noches_tropicales.calcular_todos_umbrales()
graficos_noches_tropicales.graficar_noches_anuales(
    datos_noches["tropicales"], datos_noches["muy_calidas"])
graficos_noches_tropicales.graficar_noches_comparativa(
    datos_noches["tropicales"], datos_noches["muy_calidas"])
graficos_noches_tropicales.graficar_noches_tropicales_comparativa(
    datos_noches["tropicales"])
graficos_noches_tropicales.graficar_calendario_noches(
    datos_noches["tropicales"], sufijo="tropicales")
graficos_noches_tropicales.graficar_calendario_noches(
    datos_noches["muy_calidas"], sufijo="muy_calidas")
datos_conc = extremos_estacionales.calcular_todos()
graficos_extremos_estacionales.graficar_concentracion_mensual(datos_conc)
print("  ✅ H4 done")

print("── H5: Estacionalidad ──")
graficos_estacionalidad.graficar_estacionalidad(datos_estac["estacionalidad"])
graficos_estacionalidad.graficar_amplitud_termica(datos_estac["amplitud"])
datos_verano = verano_meteorologico.calcular_todos()
graficos_verano.graficar_longitud_verano(datos_verano)
graficos_verano.graficar_verano_comparativa(datos_verano)
graficos_verano.graficar_boxplot_verano_decadas(ciudades)
datos_inicio_fin = verano_meteorologico.calcular_todos_inicio_fin()
graficos_verano.graficar_inicio_fin_verano(datos_inicio_fin)
graficos_verano.graficar_inicio_fin_comparativa(datos_inicio_fin)
print("  ✅ H5 done")

print("── H6: Correlación distancia al mar ──")
datos_mar = correlacion_mar.calcular_todos()
graficos_correlacion.graficar_correlacion_paneles(datos_mar)
graficos_correlacion.graficar_correlacion_altitud_paneles(datos_mar)
graficos_correlacion.graficar_gradiente_decadas(datos_mar)
graficos_correlacion.graficar_pairplot_variables(ciudades)
graficos_correlacion.graficar_heatmap_correlacion(ciudades)
print("  ✅ H6 done")

print("── Viento ──")
datos_viento = viento.calcular_todos()
graficos_viento.graficar_viento_anual(datos_viento["viento_anual"])
graficos_viento.graficar_dias_viento_fuerte(datos_viento["dias_fuerte"])
graficos_viento.graficar_perfil_mensual_comparativa(datos_viento)
graficos_viento.graficar_comparativa_ciudades(datos_viento)
graficos_viento.graficar_periodos_ciudades(datos_viento)
print("  ✅ Viento done")

print("\n✅ Todos los gráficos regenerados.")
