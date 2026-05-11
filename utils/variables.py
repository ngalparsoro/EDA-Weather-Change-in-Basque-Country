import pandas as pd

csv_list = ['data/clima_donostia.csv', 'data/clima_bilbo.csv', 'data/clima_baiona.csv', 
            'data/clima_iruna.csv', 'data/clima_gasteiz.csv', 'data/clima_arrasate.csv',
            'data/clima_maule.csv']

dfs = {}

CIUDADES = {
    "Bilbo":         {"lat": 43.263, "lon": -2.935},
    "Donostia":  {"lat": 43.318, "lon": -1.981},
    "Gasteiz":        {"lat": 42.846, "lon": -2.672},
    "Iruña":       {"lat": 42.812, "lon": -1.645},
    "Baiona":         {"lat": 43.493, "lon": -1.474},
    "Arrasate":       {'lat': 43.079, 'lon': -2.490},
    "Maule":          {'lat': 43.224, 'lon': -0.887}
}

