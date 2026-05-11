import sqlite3
from pathlib import Path

# Esto apunta a la raíz desde la carpeta 'scripts/'
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "database" / "empresa2.db"


def nueva_tabla_vacia():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS cuentas ( " \
                        "id INTEGER PRIMARY KEY, " \
                        "nombre TEXT, " \
                        "fecha_alta TEXT);")
        conn.commit()
        print("✅ Tabla creada correctamente.")
    except sqlite3.OperationalError:
        print("⚠️ KO alta tabla.")
    
    conn.close()

def actualizar_cuentas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO cuentas (nombre, fecha_alta) VALUES ('Ana García', '2024-03-15'), " \
                       "('Luis Martínez', '2024-06-01')," \
                       "('Sara López', '2014-01-10');")
        
        conn.commit()
        print("✅ Datos insertados correctamente.")
    except sqlite3.OperationalError:
        print("⚠️ KO alta usuarios.")
    
    conn.close()

def updt_fx_trans():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE transacciones SET fecha = '2026-05-04 11:11:23' WHERE id = 1") 
        cursor.execute("UPDATE transacciones SET fecha = '2026-05-04 11:12:00' WHERE id = 2") 
        cursor.execute("UPDATE transacciones SET fecha = '2026-05-05 10:00:00' WHERE id = 3") 
        cursor.execute("UPDATE transacciones SET fecha = '2026-05-06 11:00:00' WHERE id = 4") 
        cursor.execute("UPDATE transacciones SET fecha = '2026-05-06 12:00:00' WHERE id = 5") 
        
        conn.commit()
        print("✅ Tabla actualizada correctamente.")
    except sqlite3.OperationalError:
        print("⚠️ Error en el update.")
    
    conn.close()

#nueva_tabla_vacia()
#actualizar_cuentas()
updt_fx_trans()

