# EDA-Weather-Change-in-Basque-Country (1940-2025)
Análisis Exploratorio de Datos de los registros meteorológicos históricos del País Vasco.


## 📋 Descripción General

Este proyecto realiza un **Análisis Exploratorio de Datos (EDA)** comprensivo sobre los registros meteorológicos históricos del País Vasco (Euskal Herria) durante el período 1940-2025. El objetivo principal es investigar y cuantificar los cambios climáticos ocurridos en cinco ciudades principales.

El análisis se centra en validar hipótesis sobre el cambio climático local, incluyendo el aumento de temperaturas, reducción de precipitaciones, variabilidad territorial y cambios en la estacionalidad.

---

## 🎯 Objetivos del Proyecto

1. **Analizar tendencias climáticas** en el País Vasco durante 86 años (1940-2025)
2. **Comparar patrones meteorológicos** entre ciudades costeras e interiores
3. **Identificar cambios en extremos climáticos** (temperaturas máximas y mínimas)
4. **Evaluar cambios en la estacionalidad** y amplitud térmica anual
5. **Proporcionar evidencia cuantitativa** del cambio climático en Euskal Herria

---

## 🔬 Hipótesis de Investigación

### H1 - Aumento Sostenido de Temperaturas
Las temperaturas medias, mínimas y máximas han experimentado un incremento estadísticamente significativo en las cinco ciudades a lo largo del período 1940-2025.

### H2 - Reducción de Precipitaciones
La precipitación acumulada anual muestra una tendencia decreciente, especialmente en los meses de verano, como consecuencia del desplazamiento hacia el norte de los sistemas de baja presión atlántica.

### H3 - Diferencias Climáticas entre Ciudades
Las ciudades del interior (Vitoria-Gasteiz, Pamplona) presentan mayor variabilidad térmica anual que las costeras (Bilbao, San Sebastián, Bayona), y han experimentado un calentamiento más marcado.

### H4 - Mayor Frecuencia de Temperaturas Extremas
El número de días con temperaturas máximas superiores a 35°C ha aumentado notablemente desde los años 2000, mientras que los días con temperaturas mínimas bajo cero han disminuido.

### H5 - Estacionalidad Más Marcada
Los veranos se han vuelto más cálidos y secos, mientras que los inviernos son progresivamente más suaves, implicando una mayor amplitud de condiciones entre estaciones.

---

## 📊 Datos Utilizados

### Fuente de Datos
- **Proveedor:** API pública [Open-Meteo](https://open-meteo.com/)
- **Dataset:** Reanálisis climático **ERA5** (European Center for Medium-Range Weather Forecasts - ECMWF)
- **Cobertura Temporal:** 1940 - 2025 (86 años de datos históricos)
- **Resolución Temporal:** Datos diarios

### Ciudades Analizadas

| Ciudad | Tipo | Provincia | Coordenadas |
|--------|------|-----------|-------------|
| 🌊 **Bilbao** | Costera | Vizcaya | 43.26°N, 2.92°W |
| 🌊 **San Sebastián/Donostia** | Costera | Guipúzcoa | 43.32°N, 1.98°W |
| 🌊 **Bayona/Baiona** | Costera | Lapurdi (Francia) | 43.49°N, 1.48°W |
| 🏔️ **Vitoria-Gasteiz** | Interior | Álava | 42.85°N, 2.67°W |
| 🏔️ **Pamplona/Iruñea** | Interior | Navarra | 42.81°N, 1.64°W |

### Variables Analizadas
- `temperature_2m_mean`: Temperatura media diaria (°C)
- `temperature_2m_min`: Temperatura mínima diaria (°C)
- `temperature_2m_max`: Temperatura máxima diaria (°C)
- `precipitation_sum`: Precipitación acumulada diaria (mm)
- `año`: Año de registro
- `mes`: Mes de registro (1-12)

**Nota:** ERA5 es un producto de reanálisis climático que combina modelos numéricos atmosféricos con observaciones históricas, proporcionando series temporales consistentes y de alta resolución.

---

## 📂 Estructura del Proyecto

```
EDA-Weather-Change-in-Basque-Country/
├── README.md                                    # Este archivo
├── Intro.ipynb                                  # Notebook introductorio con descripción del proyecto
├── H2_Reduccion_precipitaciones.ipynb          # Análisis detallado de la hipótesis H2
├── H5_Estacionalidad_marcada.py                # Script de análisis de estacionalidad (H5)
├── main.py                                      # Script principal de ejecución
│
├── data/                                        # Directorio de datos (descargados)
│   ├── clima_bilbao.csv
│   ├── clima_donostia.csv
│   ├── clima_baiona.csv
│   ├── clima_irunea.csv
│   └── clima_vitoria.csv
│
├── utils/                                       # Funciones auxiliares
│   ├── descargar_datos.py                       # Descarga datos de la API Open-Meteo
│   ├── variables.py                             # Configuración y variables
│   ├── funciones_variables.py                   # Funciones comunes de carga y procesamiento
│   ├── H1_Aumento_temperaturas.py              # Análisis de H1
│   ├── H2_Reduccion_precipitaciones.py         # Análisis de H2
│   ├── H3_Diferencias_ciudades.py              # Análisis de H3
│   └── H4_Frecuencia_temp_extremas.py          # Análisis de H4
│
├── img/                                         # Imágenes y visualizaciones
│   └── [Gráficos generados del análisis]
│
├── estacionalidad_quinquenios_*.png            # Visualizaciones de estacionalidad
└── EDA-Weather-Change-in-Basque-Country.code-workspace  # Configuración VSCode
```

---

## 🚀 Cómo Ejecutar el Proyecto

### Requisitos Previos
- Python 3.8 o superior
- pip o conda para gestión de dependencias

### Instalación de Dependencias

```bash
pip install pandas numpy matplotlib seaborn scipy requests
```

### Descarga de Datos (Opcional)

Si deseas descargar datos actualizados desde la API Open-Meteo:

```bash
python main.py
```

### Ejecución del Análisis

```bash
python main.py
```

Esto ejecutará todos los análisis y generará visualizaciones en la carpeta `img/`.

### Exploración en Jupyter

Para explorar interactivamente los análisis:

```bash
jupyter notebook Intro.ipynb
jupyter notebook H2_Reduccion_precipitaciones.ipynb
```

---

## 📈 Resultados Principales

### Hallazgos Clave

✅ **Confirmado: Aumento de Temperaturas**
- Tendencia positiva clara en temperaturas medias, mínimas y máximas
- Calentamiento más pronunciado en ciudades interiores

✅ **Confirmado: Reducción de Precipitaciones**
- Descenso significativo en precipitación anual
- Cambios estacionales más marcados en verano

✅ **Confirmado: Diferencias Territoriales**
- Ciudades interiores: mayor amplitud térmica y calentamiento más acelerado
- Ciudades costeras: variabilidad moderada, amortiguadas por influencia oceánica

✅ **Confirmado: Extremos Climáticos**
- Aumento en días con temperaturas máximas > 35°C desde los años 2000
- Disminución en días con heladas (T_min < 0°C)

✅ **Confirmado: Estacionalidad Marcada**
- Veranos más secos y cálidos
- Inviernos más suaves
- Mayor amplitud anual en la variación de temperaturas

---

## 🔗 Visualizaciones Generadas

El proyecto genera múltiples gráficos analíticos:

- **Tendencias de Temperaturas:** Series temporales con líneas de tendencia
- **Análisis de Precipitaciones:** Distribuciones estacionales y anuales
- **Estacionalidad por Quinquenios:** Comparativas de períodos de 5 años
- **Mapas de Calor:** Variabilidad temporal por mes y año
- **Diagramas de Caja:** Distribuciones por ciudad

---

## 📚 Referencias Científicas

Este análisis se basa en:
- **ECMWF ERA5:** [Copernicus Climate Change Service](https://cds.climate.copernicus.eu/)
- **Open-Meteo API:** [open-meteo.com](https://open-meteo.com/)
- Literatura científica sobre cambio climático en el Sur de Europa

---

## 👤 Autor

**ngalparsoro**

- GitHub: [@ngalparsoro](https://github.com/ngalparsoro)
- Proyecto: EDA-Weather-Change-in-Basque-Country

---

🔄
