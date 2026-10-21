# EDA · Meteorología en Euskal Herria (1940–2025)

Análisis exploratorio de datos meteorológicos en 7 ciudades de Euskal Herria usando datos de reanálisis ERA5.

**📊 Presentación web:** https://ngalparsoro.github.io/EDA-Weather-Change-in-Basque-Country/

## Ciudades

| Ciudad | Tipo |
|---|---|
| Bilbo, Donostia, Baiona | Costera |
| Gasteiz, Iruñea, Arrasate, Maule | Interior |

## Hipótesis

- **H1** — Las temperaturas han aumentado de forma sostenida, con aceleración de los extremos desde 2015–2020.
- **H2** — Reducción de precipitaciones en el interior y aumento de episodios intensos en todas las ciudades.
- **H3** — Las ciudades del interior presentan mayor variabilidad térmica y calentamiento más intenso.
- **H4** — Los días con Tmax >35°C han aumentado notablemente desde los 2000; los días bajo cero disminuyen.
- **H5** — Los veranos son más largos, cálidos y secos; los inviernos más suaves.
- **H6** — La distancia al mar explica parte de la variabilidad climática entre ciudades.

## Estructura

```
├── data/                       # CSVs por ciudad (ERA5 vía Open-Meteo)
├── docs/                       # Presentación web (GitHub Pages)
├── img/                        # Gráficos generados, por análisis
├── notebooks/                  # Limpieza de datos y análisis por hipótesis (H1–H6)
├── scripts/
│   ├── analisis/               # Módulos de cálculo
│   ├── graficos/               # Módulos de visualización
│   ├── variables.py
│   ├── funciones_variables.py
│   ├── validacion.py
│   └── descargar_datos.py
├── Intro.ipynb                 # Introducción
├── Memoria.ipynb               # Memoria del proyecto
├── EDA_CambioClimaticoEuskalHerria.html   # Presentación (fuente de docs/)
├── EDA_Euskal_Herria.pptx/.pdf # Presentación en diapositivas
├── main.py                     # Análisis completo
├── regenerar_graficos.py       # Regenera todos los gráficos de img/
└── exportar_presentacion.py    # Genera docs/ a partir de la presentación
```

## Uso

```bash
# Instalar dependencias
pip install -r requirements.txt

# Descargar datos
python scripts/descargar_datos.py

# Ejecutar análisis completo
python main.py

# Regenerar los gráficos y la presentación web (docs/)
python regenerar_graficos.py
python exportar_presentacion.py

# O abrir la memoria directamente
jupyter notebook Memoria.ipynb
```

## Datos

- **Fuente:** [Open-Meteo API](https://open-meteo.com) · Reanálisis ERA5 (ECMWF)
- **Período:** 1940–2025 · Granularidad diaria
- **Variables:** temperatura media, máxima y mínima diaria · precipitación · velocidad del viento

## Herramientas

Python · Pandas · Matplotlib · Seaborn · NumPy · SciPy · Scikit-learn
