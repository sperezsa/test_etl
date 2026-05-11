from pathlib import Path
import logging
import pandas as pd
from datetime import datetime
import os
import plotly.express as px

logger = logging.getLogger(__name__)


def encontrar_ficheros_por_fecha(ruta_salida, fecha_str):
    """
    Busca los archivos de clientes y transacciones para una fecha YYYYMMDD.
    Ejemplo: 20260508_clientes.csv
    """
    
    # Buscamos archivos que empiecen por la fecha y contengan la palabra clave
    fichero_clientes = list(Path(ruta_salida).glob(f"{fecha_str}_*clientes*.csv"))
    fichero_transacciones = list(Path(ruta_salida).glob(f"{fecha_str}_*transacciones*.csv"))

    # Validamos que hayamos encontrado exactamente uno de cada
    if not fichero_clientes or not fichero_transacciones:
        logger.error(f"No se encontraron ambos ficheros para la fecha {fecha_str}")
        return None, None
    
    logger.info(f"Ficheros identificados: {fichero_clientes[0].name} y {fichero_transacciones[0].name}")
    
    # Devolvemos el string de la ruta
    return str(fichero_clientes[0]), str(fichero_transacciones[0])


def ejecutar_proceso_unificacion(ruta, fecha_a_procesar=None):
    # Si no le pasamos fecha, usamos la de hoy por defecto
    if not fecha_a_procesar:
        fecha_a_procesar = datetime.now().strftime("%Y%m%d")

    # 1. Identificar
    path_cli, path_tra = encontrar_ficheros_por_fecha(ruta, fecha_a_procesar)

    if path_cli and path_tra:
        # 2. Leer
        df_cli = pd.read_csv(path_cli, encoding='utf-8-sig')
        df_tra = pd.read_csv(path_tra, encoding='utf-8-sig')
       
        # 3. Limpieza de nombres por si acaso
        df_cli.columns = df_cli.columns.str.strip()
        df_tra.columns = df_tra.columns.str.strip()

        # 4. EL CRUCE CLAVE: how='right' para recuperar todas las transacciones 
        df_tablon = pd.merge(
            df_cli, 
            df_tra, 
            left_on='id', 
            right_on='cliente_id', 
            how='right' 
        )
        # Convertir la columna al tipo entero con soporte para nulos (Int64 con I mayúscula)
        df_tablon['cliente_id'] = df_tablon['cliente_id'].astype('Int64')

        # 5. Guardar resultado
        nombre_salida = f"{fecha_a_procesar}_TABLON_COMBINADO.csv"
        dir_salida = os.path.join(ruta, nombre_salida)
        df_tablon.to_csv(dir_salida, index=False, sep=';', encoding='utf-8-sig')
        logger.info(f"Éxito: Generado {nombre_salida} con {len(df_tablon)} registros.")
        logger.info(f"Se muestra gráfico de dispersión de fechas vs Monto indetificando clientes por nivel de riesgo y línea de límite 1000.")

        # Gráfico de burbujas: Fecha vs Monto, color por nivel de riesgo
        fig = px.scatter(df_tablon, x="fecha", y="monto", 
                 color="nivel_riesgo", #size="saldo", 
                 hover_name="nombre", title="Análisis de Operaciones")

        # Añadimos la línea de corte en 1000
        fig.add_hline(y=1000, line_dash="dot", 
              annotation_text="Límite 1000€", 
              annotation_font=dict(color="red", size=12),
              line_color="red")
        
        fig.show()


    else:
        logger.info("Proceso abortado por falta de ficheros.")

