from utils.descargar_datos import descargar_datos
from utils.variables import csv_list
from utils.funciones_variables import cargar_datos
from utils.H1_Aumento_temperaturas import aumento_temperaturas
from utils.H2_Reduccion_precipitaciones import precipitaciones, precipitaciones_extremas
from utils.H3_Diferencias_ciudades import diferencias_ciudades
from utils.H4_Frecuencia_temp_extremas import temperaturas_extremas

if __name__ == "__main__":

    # Paso 1 : Descargar datos
    #descargar_datos(csv_list)

    # Paso 2 : Cargar datos
    cargar_datos(csv_list)

    # Paso 2 : Visualizar aumento de temperaturas
    #aumento_temperaturas()

    # Paso 3 : Visualizar precipitaciones
    #precipitaciones()

    # Paso 4 : Visualizar precipitaciones extremas
    #precipitaciones_extremas()

    # Paso 5 : Diferencias ciudades
    #diferencias_ciudades()

    # Paso 6 : Frecuencia temperaturas extremas
    temperaturas_extremas()

    # Paso 7 : Estacionalidad marcada
    