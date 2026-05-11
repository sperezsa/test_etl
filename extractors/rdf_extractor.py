import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def extraer_mdat_lista_datasets_cnig():
    endpoint_url = "https://datos.gob.es/virtuoso/sparql"
    
    # Consulta SPARQL para filtrar por CNIG y obtener la lista de conjuntos de datos
    query = """
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    SELECT ?dataset ?titulo ?fecha_emision ?licencia ?frecuencia
    WHERE {
      ?dataset a dcat:Dataset .
      ?dataset dct:title ?titulo .
      ?dataset dct:publisher ?publicador .
      ?publicador foaf:name ?nombre_pub .
      
      # Filtramos por CNIG
      FILTER(CONTAINS(LCASE(?nombre_pub), "centro nacional de información geográfica"))
      
      OPTIONAL { ?dataset dct:issued ?fecha_emision }
      OPTIONAL { ?dataset dct:license ?licencia }
      OPTIONAL { ?dataset dct:accrualPeriodicity ?frecuencia }
    }
    LIMIT 100
    """
    
    params = {
        "query": query,
        "format": "application/sparql-results+json"
    }

    try:
        response = requests.get(endpoint_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Aplanamos el JSON de SPARQL a una lista de diccionarios
        resultados = []
        for row in data["results"]["bindings"]:
            resultados.append({
                "uri": row["dataset"]["value"],
                "titulo": row["titulo"]["value"],
                "fecha": row.get("fecha_emision", {}).get("value", "N/A"),
                "licencia": row.get("licencia", {}).get("value", "N/A")
            })
        
        return resultados

    except Exception as e:
        logger.error(f"Error consultando la API de datos.gob.es: {e}")
        return []
    

def extraer_mdat_dataset_cnig():
    endpoint_url = "https://datos.gob.es/virtuoso/sparql"
    
    # Consulta SPARQL para filtrar por CNIG y obtener propiedades DCAT-AP-ES
    query = """    
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>

    SELECT DISTINCT ?propiedad ?valor
    WHERE {
    ?s a dcat:Dataset ;
        dct:title ?titulo .
    
    # Filtro por el nombre exacto que buscas
    FILTER(STR(?titulo) = "Información Geográfica de Referencia de Poblaciones")
    
    # Traemos todas las propiedades asociadas
    ?s ?propiedad ?valor .
    }
    ORDER BY ?propiedad
    """
    
    params = {
        "query": query,
        "format": "application/sparql-results+json"
    }

    try:
        response = requests.get(endpoint_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        resultados = []
        for row in data["results"]["bindings"]:
            # IMPORTANTE: Aquí cambiamos row["dataset"] por row["propiedad"]
            resultados.append({
                "Propiedad": row["propiedad"]["value"],
                "Valor": row["valor"]["value"]
            })
        
        return resultados

    except KeyError as e:
        logger.error(f"Error: La consulta no devolvió la columna esperada: {e}")
        return []
    except Exception as e:
        logger.error(f"Error consultando la API: {e}")
        return []

def extraer_mdat_por_dataset_cnig():
    endpoint_url = "https://datos.gob.es/virtuoso/sparql"
    
    # Consulta SPARQL para filtrar por CNIG y obtener propiedades DCAT-AP-ES
    query = """    
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?nivel ?id_recurso ?propiedad ?valor
    WHERE {
    # --- BLOQUE 1: PROPIEDADES DEL DATASET ---
    {
        ?dataset a dcat:Dataset ;
                dct:title ?titulo .
        FILTER(STR(?titulo) = "Información Geográfica de Referencia de Poblaciones")
        ?dataset ?propiedad ?valor .
        BIND("DATASET" AS ?nivel)
        BIND(?dataset AS ?id_recurso)
    }
    UNION
    # --- BLOQUE 2: PROPIEDADES DE SUS DISTRIBUCIONES ---
    {
        ?dataset a dcat:Dataset ;
                dct:title ?titulo ;
                dcat:distribution ?dist .
        FILTER(STR(?titulo) = "Información Geográfica de Referencia de Poblaciones")
        ?dist ?propiedad ?valor .
        BIND("DISTRIBUCION" AS ?nivel)
        BIND(?dist AS ?id_recurso)
    }
    UNION
    # --- BLOQUE 3: PROPIEDADES DE SERVICIOS (Data Services) ---
    {
        ?dataset a dcat:Dataset ;
                dct:title ?titulo ;
                dcat:distribution ?dist .
        ?dist dcat:accessService ?service .
        FILTER(STR(?titulo) = "Información Geográfica de Referencia de Poblaciones")
        ?service ?propiedad ?valor .
        BIND("SERVICIO" AS ?nivel)
        BIND(?service AS ?id_recurso)
    }
    }
    ORDER BY ?nivel ?id_recurso ?propiedad
    """
    
    params = {
        "query": query,
        "format": "application/sparql-results+json"
    }

    try:
        response = requests.get(endpoint_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        resultados = []
        for row in data["results"]["bindings"]:
            resultados.append({
                "Nivel": row["nivel"]["value"],
                "ID Recurso": row["id_recurso"]["value"],
                # Usamos la función de limpiar_uri que comentamos antes si quieres nombres cortos
                "Propiedad": row["propiedad"]["value"],
                "Valor": row["valor"]["value"]
            })
        
        return resultados
    except Exception as e:
        logger.error(f"Error en la extracción multinivel: {e}")
        return []


def obtener_metadatos_por_titulo(titulo):
    # La base de la API de datos.gob.es (Linked Data API)
    url_base = "http://datos.gob.es/apidata/catalog/dataset/title/"
    
    # Construimos la URL completa. 
    # Requests se encargará de convertir "Información" en "Informaci%C3%B3n" automáticamente.
    url_completa = f"{url_base}{titulo}.json"
    
    # Parámetros adicionales de la API de datos.gob.es
    params = {
        "_sort": "title",
        "_pageSize": 10,
        "_page": 0
    }

    try:
        logger.info(f"Consultando API para: {titulo}")
        response = requests.get(url_completa, params=params, timeout=20)
        response.raise_for_status() # Lanza error si la URL está mal o el dataset no existe
                    
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"No se encontró el dataset o error en la URL: {e}")
        return None

def procesar_json_api(api_response):
    items = api_response.get("result", {}).get("items", [])
    filas_csv = []

    for item in items:
        # 1. Extraer campos simples
        dataset_id = item.get("_about")
        fecha_creacion = item.get("issued")
        fecha_modificacion = item.get("modified")
        
        # 2. Extraer títulos y descripciones (Filtramos por idioma 'es')
        titulo_es = next((t["_value"] for t in item.get("title", []) if t.get("_lang") == "es"), "N/A")
        desc_es = next((d["_value"] for d in item.get("description", []) if d.get("_lang") == "es"), "N/A")
        
        # 3. Palabras clave (las unimos por comas)
        keywords = ", ".join([k["_value"] for k in item.get("keyword", []) if k.get("_lang") == "es"])
        
        # Estos suelen venir como una URI directa o un string
        cobertura_espacial = item.get("spatial", "N/A")
        tema_dataset = item.get("theme", "N/A")

        # 4. Información de la Distribución
        dist = item.get("distribution", {})
        dist_url = dist.get("accessURL", "N/A")
        dist_formato = dist.get("format", {}).get("value", "N/A")
        dist_titulo = next((t["_value"] for t in dist.get("title", []) if t.get("_lang") == "es"), "N/A")

        # Crear la fila aplanada
        filas_csv.append({
            "Nivel": "DATASET",
            "Dataset_ID": dataset_id,
            "Titulo": titulo_es,
            "Descripcion": desc_es,
            "Cobertura_Espacial": cobertura_espacial,
            "Tema_Principal": tema_dataset,
            "Fecha_Publicacion": fecha_creacion,
            "Ultima_Modificacion": fecha_modificacion,
            "Keywords": keywords,
            "Publicador": item.get("publisher"),
            "Frecuencia_Meses": item.get("accrualPeriodicity", {}).get("value", {}).get("months"),
            "Dist_Titulo": dist_titulo,
            "Dist_Formato": dist_formato,
            "Dist_URL": dist_url
        })

    return pd.DataFrame(filas_csv)

