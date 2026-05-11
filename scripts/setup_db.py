import sqlite3
from pathlib import Path

# Esto apunta a la raíz desde la carpeta 'scripts/'
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "empresa2.db"



def setup_database(schema_queries, data_configs=None):
    """
    Crea tablas e inserta datos de forma dinámica.
    :param schema_queries: Lista de strings con comandos CREATE TABLE
    :param data_configs: Lista de tuplas (query_insert, lista_de_datos)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Ejecutar la creación de tablas
        for query in schema_queries:
            cursor.execute(query)
        
        # 2. Insertar datos si se proporcionan
        if data_configs:
            for query, data in data_configs:
                cursor.executemany(query, data)
        
        conn.commit()
        print(f"Base de datos actualizada con éxito.")
        
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # --- CONFIGURACIÓN ---

    # Definición de tablas
    tablas = [
        '''CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            email TEXT,
            saldo REAL,
            nivel_riesgo TEXT,
            documento TEXT,
            pais TEXT,
            comentarios TEXT,
            fecha_alta TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            monto REAL,
            tipo TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )'''
    ]

    # Configuración de datos iniciales
    datos_iniciales = [
        # Clientes
        ('INSERT OR REPLACE INTO clientes VALUES (?,?,?,?,?,?,?,?,?)', [
            (1, 'Juan Pérez', 'juan@ejemplo.com', 1500.50, 'Bajo', '05309480E', 'ESP', ' lo que sea ', '2025-01-01'),
            (2, 'María García', 'maria@ejemplo.com', 45000.00, 'Medio', '12342878C', 'ITA', 'otra cadena de caracteres esdrújula ', '2023-01-01'),
            (3, 'Carlos Ruiz', 'carlos@ejemplo.com', -250.00, 'Alto', '71466987F', 'FRA', 'all you need is attention', '2022-01-01'),
            (4, 'Carlos Varios', 'carlosvarios@ejemplo.com', 1250.00, 'Alto', '13172516W', 'FRA', '', '2025-01-01' )
        ]),
        # Transacciones de ejemplo
        ('INSERT INTO transacciones (cliente_id, monto, tipo) VALUES (?,?,?)', [
            (1, 100.0, 'DEPOSITO'),
            (1, -20.0, 'RETIRO'),
            (2, 5000.0, 'TRANSFERENCIA'),
            (2, -4000.0, 'RETIRO'),
            (1, -30.0, 'RETIRO')
        ])
    ]

    # Ejecución
    setup_database(tablas, datos_iniciales)