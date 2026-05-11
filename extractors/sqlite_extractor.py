import sqlite3
import logging

logger = logging.getLogger(__name__)

class SQLiteExtractor:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_data(self, query: str) -> list:
        """Extrae datos y los devuelve como una lista de diccionarios"""
        try:
            # Conectamos usando un context manager para asegurar el cierre
            with sqlite3.connect(self.db_path) as conn:
                # Configuramos el row_factory para obtener diccionarios en vez de tuplas
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                
                # Convertimos cada fila de SQLite.Row a un dict de Python
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Error al extraer datos de SQLite: {e}")
            return []