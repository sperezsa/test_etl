from pathlib import Path
import os
from extractors.sqlite_extractor import SQLiteExtractor
from extractors import extractor
from utils.etl_engine import ETLEngine
from models.cliente_schema import ClienteSchema
from models.transaccion_schema import TransaccionSchema
import logging
import logging.handlers
import warnings
from typing import List, Dict, Any
import configparser
import csv
import pandas as pd
from datetime import datetime

from extractors.rdf_extractor import *
from analytic.join import *

#---------------------------------------------------------
# --- Configuración y Logging con rotación de ficheros ---
#---------------------------------------------------------

DIRECTORIO_SALIDA = "data/output" 
LOG_FILE = "data/output/log_script.log" 
MAX_BYTES = 10 * 1024 * 1024   # 10 MB
BACKUP_COUNT = 3               # Mantener 3 ficheros de log antiguos

# Obtener el nivel de log de una variable de entorno.
# $env:APP_LOG_LEVEL="INFO"

# Si la variable no existe, se usa 'WARNING' por defecto. Por ahora lo dejo en INFO para pruebas en desarrollo
# LOG_LEVEL = os.getenv('APP_LOG_LEVEL', 'WARNING').upper()
LOG_LEVEL = os.getenv('APP_LOG_LEVEL', 'INFO').upper()

# Crear un 'handler' que gestiona la rotación
# Rotará el fichero cuando supere los 10 MB y guardará 3 copias de seguridad (.1, .2, .3)
rotating_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=MAX_BYTES,
    backupCount=BACKUP_COUNT,
    encoding='utf-8'
)

# Configuración del formato de los mensajes
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
rotating_handler.setFormatter(formatter)

# Configuración del logging principal
logging.basicConfig(
    level=LOG_LEVEL, 
    handlers=[
        rotating_handler  
        # logging.StreamHandler() # Para que siga mostrando los logs en la consola
    ]
)

logging.captureWarnings(True)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


#---------------------------------------------------------
# --- Inicialización del entorno 
#---------------------------------------------------------

def inicializar_entorno():
    # Definimos las rutas
    carpetas = ['data/input', 'data/output']
    
    for carpeta in carpetas:
        # parents=True crea carpetas intermedias si no existen
        # exist_ok=True evita que el código explote si la carpeta ya está ahí
        Path(carpeta).mkdir(parents=True, exist_ok=True)


#--------------------------------------------------
# --- Funcion para recuperar datos de configuración
#--------------------------------------------------

def leer_configuracion(project) -> Dict[str, Any]:
    """
    Recupera la configuracion establecida en el fichero .conf y la almacena en un diccionario
    """
    CONFIG_FILE = os.path.join(project, 'config', '.conf')

    if not os.path.exists(CONFIG_FILE):
        logging.info(f"Error: No se encontró el archivo de configuración en {CONFIG_FILE}")
	
	#Leer la configuración ---
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
	
    # Retorna un diccionario con los valores, en este caso hay solo valores de la bd
    return {
		'DRIVER'   : config['database']['DRIVER'],
		'SERVER'   : config['database']['DB_SERVER'],
		'DATABASE' : config['database']['DB_DATABASE'],
		'UID'      : config['database']['DB_UID'],
		'PWD'      : config['database']['DB_PWD'],
		'ENCRYPT'  : config['database']['ENCRYPT'],
		'TRUST_SERVER_CERTIFICATE' : config['database']['TRUST_SERVER_CERTIFICATE']
	}


#--------------------------------------------------
# proceso ppal 
#--------------------------------------------------

def run_pipeline():
    try:
        # Se crean las carpetas input y output
        inicializar_entorno()

        logging.info(f"--- INICIO EJECUCIÓN ---") 
        
        # 1. CONFIGURACIÓN DE RUTAS
        # Para esta prueba utilizamos el fichero empresa2.db como base de datos relacional gestionada por el motor SQLite.
        ORIGEN = "empresa2.db"
        db_path = os.path.join(PROJECT_ROOT, ORIGEN)

        # 2. LECTURA FICHERO CONFIGURACIÓN
        # se registran los datos de conexion a bbdd SQL server
        dic_config = leer_configuracion(PROJECT_ROOT)
        logging.info(f"--- Recuperar fichero de CONFIGURACION {dic_config} ---") 

        # 3. FASE E: EXTRACCIÓN Y TRANSFORMACIÓN
        logging.info(f"--- Iniciando fase de EXTRACCIÓN Y TRANSFORMACIÓN ---")  
        
        salida = extractor.procesar_extraccion(db_path)

        logging.info(f"Resumen estado EXTRACCIÓN. Numero de tablas procesadas: {len(salida)}")
        for tabla, listas in salida.items():
            logging.info(f"{tabla} | OK: {len(listas['ok'])} | KO: {len(listas['ko'])}")

 
        # 6. FASE L: LOAD (Carga a otra BBDD, CSV, etc, en este caso a CSV)
        logging.info(f"--- Iniciando fase de CARGA generando ficheros CSV por tabla ---") 

        fecha_hoy = datetime.now().strftime("%Y%m%d")

        for tabla, listas in salida.items():
            # para generar fichero CSV SOLO de tablas que contengan registros
            if listas['ok']:
                logging.info(f"{tabla} | OK: {len(listas['ok'])} | KO: {len(listas['ko'])}")
                nombre_fich = f"{fecha_hoy}_{ORIGEN.split('.')[0]}_{tabla}.csv"
                dir_salida = os.path.join(PROJECT_ROOT, 'data', 'output', nombre_fich)
                pd.DataFrame(listas['ok']).to_csv(dir_salida, index=False)
                logging.info(f"Generado fichero salida en: {dir_salida}")

        # 7. FASE ANÁLISIS DE DATOS y GRÁFICO DE DISPERSIÓN
        logging.info(f"--- Iniciando fase de ANÁLISIS DE DATOS ---") 
        ejecutar_proceso_unificacion(os.path.join(PROJECT_ROOT, 'data', 'output'))


    except Exception as e:
        logging.critical(f"Ha ocurrido un error inesperado en el script: {e}")
    finally:
        if True:
            #cnxn:
            #cnxn.close()
            logging.info(f"--- FIN EJECUCIÓN ---") 


#----------------------------------------------------------
# proceso para extraer metadatos de datos.gob.es con SPARQL
#----------------------------------------------------------

def proceso_auditoria_metadatos():
    logging.info("Iniciando extracción de metadatos desde datos.gob.es con SPARQL")
    
    # 1. Extraer
    datos = extraer_mdat_por_dataset_cnig()
    
    if not datos:
        logging.info("No se recuperaron metadatos.")
        return

    # 2. Convertir a DataFrame
    df = pd.DataFrame(datos)
    
    # 3. Generar nombre
    fecha_hoy = datetime.now().strftime("%Y%m%d")
    nombre_fich = f"{fecha_hoy}_CNIG_DCAT_AP_ES.csv"
    dir_salida = os.path.join(PROJECT_ROOT, 'data', 'output', nombre_fich)

    # 4. Exportar
    df.to_csv(dir_salida, index=False, sep=';', encoding='utf-8-sig')
    logging.info(f"Reporte generado exitosamente: {dir_salida}")


#--------------------------------------------------------
# proceso para extraer metadatos de datos.gob.es por API
#--------------------------------------------------------

def proceso_api():
    logging.info("Iniciando extracción de metadatos desde datos.gob.es llamando a la API por nombre de dataset")

    fecha_hoy = datetime.now().strftime("%Y%m%d")

    # Lista de datasets que quieres consultar
    datasets_a_revisar = [
    "Información Geográfica de Referencia de Poblaciones" #,    "Red de Transporte"
    ]

    for nombre in datasets_a_revisar:
        data_json = obtener_metadatos_por_titulo(nombre)
        
        if data_json:
            df = procesar_json_api(data_json)
            
            # Guardar cada uno con su nombre y fecha
            nombre_fich = f"{fecha_hoy}_{nombre.replace(' ', '_')}.csv"
            dir_salida = os.path.join(PROJECT_ROOT, 'data', 'output', nombre_fich)

            df.to_csv(dir_salida, sep=';', index=False, encoding='utf-8-sig')
            logging.info(f"CSV generado con éxito: {dir_salida}")
    
if __name__ == "__main__":
    run_pipeline()
    #proceso_auditoria_metadatos()
    #proceso_api()