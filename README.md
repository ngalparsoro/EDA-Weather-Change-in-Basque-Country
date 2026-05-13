# EDA · Meteorología en Euskal Herria (1940–2025)

Análisis exploratorio de datos meteorológicos en 7 ciudades de Euskal Herria usando datos de reanálisis ERA5.

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
├── data/               # CSVs por ciudad (ERA5 vía Open-Meteo)
├── img/                # Gráficos generados
├── notebooks/          # Análisis por hipótesis + Memoria
├── scripts/
│   ├── analisis/       # Módulos de cálculo
│   ├── graficos/       # Módulos de visualización
│   ├── variables.py
│   ├── funciones_variables.py
│   └── descargar_datos.py
└── main.py
```

## Uso

```bash
# Instalar dependencias
pip install -r requirements.txt

# Descargar datos
python scripts/descargar_datos.py

# Ejecutar análisis completo
python main.py

# O abrir la memoria directamente
jupyter notebook notebooks/Memoria.ipynb
```

## Datos

- **Fuente:** [Open-Meteo API](https://open-meteo.com) · Reanálisis ERA5 (ECMWF)
- **Período:** 1940–2025 · Granularidad diaria
- **Variables:** temperatura media, máxima y mínima diaria · precipitación · velocidad del viento

## Herramientas

Python · Pandas · Matplotlib · Seaborn · NumPy · SciPy · Scikit-learn
