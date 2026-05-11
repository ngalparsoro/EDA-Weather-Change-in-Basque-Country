import pandas as pd
from utils.variables import dfs

def cargar_datos(csv_list):
    for csv in csv_list:
        nombre = csv.split('_')[1].replace('.csv', '')
        dfs[nombre] = pd.read_csv(csv)
    return dfs
