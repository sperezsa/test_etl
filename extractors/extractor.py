import yaml
from typing import Dict, Type
from pydantic import BaseModel
import logging
from .sqlite_extractor import SQLiteExtractor
from pydantic import ValidationError

# Importamos tus esquemas
from models.cliente_schema import ClienteSchema
from models.transaccion_schema import TransaccionSchema


logger = logging.getLogger(__name__)


# Diccionario mapeador: vincula el texto del YAML con la clase de Pydantic
MAPEO_ESQUEMAS: Dict[str, Type[BaseModel]] = {
    "cliente": ClienteSchema,
    "transaccion": TransaccionSchema
}

def procesar_extraccion(db_path):

    reporte_procesamiento = {}

    # 1. Leer configuración
    logger.info(f"--- Leyendo fichero yaml con la info de las tablas a procesar ---")
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    for item in config['extract_process']:
        tabla = item['table_name']
        tipo_esquema = item['schema_type']
        consulta = item['query']
        
        logger.info(f"--- Procesando tabla: {tabla} ---")
        
        reporte_procesamiento[tabla] = {"ok": [], "ko": []}

        # 2. Obtener los datos
        extractor = SQLiteExtractor(db_path)
        datos_crudos = extractor.get_data(consulta)
        
        if not datos_crudos: 
            logger.info(f"No se extrajeron datos. Abortando proceso.") 
            reporte_procesamiento[tabla] = {"ok": [0], "ko": [0]}
            return

        logger.info(f"Extracción completada tabla {tabla}. {len(datos_crudos)} registros obtenidos.")


        # 3. Validar cada registro con el esquema correspondiente
        esquema_validador = MAPEO_ESQUEMAS.get(tipo_esquema)
        
        if not esquema_validador:
            logger.error(f"Error: No hay un esquema definido para {tipo_esquema}")
            continue

        for registro in datos_crudos:
            try:
                # Validación dinámica y Transformación con Pydantic
                obj_validado = esquema_validador(**registro)
                
                reporte_procesamiento[tabla]["ok"].append(obj_validado.model_dump())

            except ValidationError as e:
                logger.error(f"❌ Error de validación en {tabla}: {e}")
                # .json() devuelve un string detallado con cada campo fallido
                registro['detalle_error'] = e.json()
                reporte_procesamiento[tabla]["ko"].append(registro)
            except ValueError as e:
                logger.error(f"❌ Error de valor en {tabla}: {e}")
                registro['detalle_error'] = str(e)
                reporte_procesamiento[tabla]["ko"].append(registro)


    return reporte_procesamiento