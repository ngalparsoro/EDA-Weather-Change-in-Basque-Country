import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from utils.variables import csv_list, dfs
from utils.funciones_variables import cargar_datos

cargar_datos(csv_list)

def precipitaciones():
    for csv_name in dfs:
        df = dfs[csv_name]

        # ───────────────────────────────────────────────
        # PRECIPITACIÓN TOTAL ANUAL
        # ───────────────────────────────────────────────
        df_precip = df.groupby('año')['precipitation_sum'].sum()

        años = df_precip.index.tolist()
        precip = df_precip.values

        # ───────────────────────────────────────────────
        # MEDIA MÓVIL (10 años)
        # ───────────────────────────────────────────────
        window = 10
        media_movil = np.convolve(precip, np.ones(window)/window, mode='valid')
        años_mm = años[window-1:]

        # ───────────────────────────────────────────────
        # FIGURA
        # ───────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor('#F8F9FA')
        ax.set_facecolor('#F8F9FA')

        # Colores según nivel de precipitación
        colors = ['#60A5FA' if p >= 1400 else '#93C5FD' if p >= 1000 else '#FCA5A5' for p in precip]

        ax.bar(años, precip, color=colors, alpha=0.75, width=0.8, zorder=2)

        # Media móvil
        ax.plot(años_mm, media_movil, color='#1E3A8A', linewidth=2.5,
                label=f'Media móvil {window} años', zorder=3)

        # ───────────────────────────────────────────────
        # ESTILO
        # ───────────────────────────────────────────────
        ax.set_title(f'Precipitación total anual\n{csv_name.capitalize()} (1941–2024)',
                    fontsize=14, fontweight='bold', color='#021B2E', pad=15)
        ax.set_xlabel('Año', fontsize=11, color='#021B2E')
        ax.set_ylabel('Precipitación anual (mm)', fontsize=11, color='#021B2E')
        ax.tick_params(colors='#475569')
        ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.grid(axis='y', color='#CBD5E1', linestyle='--', alpha=0.6, zorder=1)
        ax.spines[['top', 'right']].set_visible(False)
        ax.legend(fontsize=10)

        # Anotar años muy secos (< 800 mm)
        for año, p in zip(años, precip):
            if p < 800:
                ax.annotate(f'{int(p)}', xy=(año, p), xytext=(0, 5),
                            textcoords='offset points', ha='center',
                            fontsize=9, color='#B91C1C', fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'img/precipitacion/grafico_precipitacion_{csv_name}.png', dpi=180, bbox_inches='tight')
        plt.show()

def precipitaciones_extremas():
    for csv_name in dfs:
        df = dfs[csv_name]
        
        # ───────────────────────────────────────────────
        # PRECIPITACIÓN TOTAL ANUAL
        # ───────────────────────────────────────────────
        df_precip = df.groupby('año')['precipitation_sum'].sum()

        años = df_precip.index.tolist()
        precip = df_precip.values

        # ───────────────────────────────────────────────
        # MEDIA MÓVIL (10 años)
        # ───────────────────────────────────────────────
        window = 10
        media_movil = np.convolve(precip, np.ones(window)/window, mode='valid')
        años_mm = años[window-1:]
        
        # ───────────────────────────────────────────────
        # DÍAS CON MÁS DE 30 MM (por año)
        # ───────────────────────────────────────────────
        # Agrupar por año y contar días con precipitación > 30 mm
        df_dias_intensos = df[df['precipitation_sum'] > 30].groupby('año').size()
        
        # Asegurar que todos los años estén presentes (rellenar con 0)
        todos_años = range(min(años), max(años)+1)
        dias_intensos = df_dias_intensos.reindex(todos_años, fill_value=0)
        
        años_completos = dias_intensos.index.tolist()
        dias_values = dias_intensos.values

        # ───────────────────────────────────────────────
        # FIGURA 2: DÍAS CON MÁS DE 30 MM
        # ───────────────────────────────────────────────

        años_completos = dias_intensos.index.tolist()
        dias_values = dias_intensos.values
        
        fig2, ax2 = plt.subplots(figsize=(14, 6))
        fig2.patch.set_facecolor('#F8F9FA')
        ax2.set_facecolor('#F8F9FA')

        # Colores según número de días intensos
        colors_dias = ['#DC2626' if d >= 10 else '#F59E0B' if d >= 5 else '#10B981' if d >= 1 else '#94A3B8' 
                    for d in dias_values]

        ax2.bar(años_completos, dias_values, color=colors_dias, alpha=0.75, width=0.8, zorder=2)

        # Media móvil para días intensos
        if len(dias_values) >= window:
            media_movil_dias = np.convolve(dias_values, np.ones(window)/window, mode='valid')
            años_mm_dias = años_completos[window-1:]
            ax2.plot(años_mm_dias, media_movil_dias, color='#1E3A8A', linewidth=2.5,
                    label=f'Media móvil {window} años', zorder=3)

        # Estilo
        ax2.set_title(f'Días con precipitación > 30 mm por año\n{csv_name.capitalize()} (1941–2024)',
                    fontsize=14, fontweight='bold', color='#021B2E', pad=15)
        ax2.set_xlabel('Año', fontsize=11, color='#021B2E')
        ax2.set_ylabel('Número de días', fontsize=11, color='#021B2E')
        ax2.tick_params(colors='#475569')
        ax2.xaxis.set_major_locator(ticker.MultipleLocator(10))
        ax2.grid(axis='y', color='#CBD5E1', linestyle='--', alpha=0.6, zorder=1)
        ax2.spines[['top', 'right']].set_visible(False)
        ax2.legend(fontsize=10)

        # Anotar años con muchos días intensos (> 10 días)
        for año, d in zip(años_completos, dias_values):
            if d > 10:
                ax2.annotate(f'{int(d)}', xy=(año, d), xytext=(0, 5),
                            textcoords='offset points', ha='center',
                            fontsize=9, color='#991B1B', fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'img/precipitacion/grafico_dias_intensos_{csv_name}.png', dpi=180, bbox_inches='tight')
        plt.show()
