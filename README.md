# test_etl

Proyecto de ingeniería de datos para la extracción, transformación y carga (ETL) de información de transacciones y clientes, con visualización mediante un cuadro de mandos interactivo.

## 🛠️ Descripción del Sistema
El proyecto consta de dos fases principales:

1. **Proceso ETL (`main.py`)**: Ejecuta la lógica de integración de diferentes orígenes de datos, principalmente desde la base de datos `empresa2.db`, para generar un fichero consolidado denominado **TABLON** (hay un ejemplo en `data/output/EJEMPLO_TABLON_COMBINADO.csv`) con información detallada de transacciones y clientes.

2. **Visualización (`app.py`)**: Un cuadro de mandos desarrollado en **Streamlit** que consume el fichero CSV generado para mostrar métricas y análisis clave.

## 📂 Estructura del Repositorio
```text
test_etl/
├── app.py                 # Dashboard de visualización (Streamlit)
├── main.py                # Lógica central del proceso ETL
├── pyproject.toml         # Configuración de dependencias (uv)
├── uv.lock                # Bloqueo de versiones de dependencias
├── .gitignore             # Archivos y carpetas excluidos del repositorio
├── config/
│   └── config.yaml        # Parám. de config de acceso a la bd (tabla, schema y query)
├── data/
│   ├── database/          # Origen de datos (empresa2.db)
│   ├── input/             # Ficheros de entrada adicionales (en principio no se utiliza)
│   └── output/            # Destino del ETL (Fichero salida TABLON CSV)
└── scripts/               # Utilidades de mantenimiento
    ├── setup_db.py        # Inicialización de la base de datos
    └── update_db.py       # Scripts de actualización de registros
```

## 🚀 Tecnologías
- **Gestión de Entorno**: [uv](https://github.com/astral-sh/uv) (Gestor de paquetes de alto rendimiento)

- **Interfaz de Usuario**: Streamlit

- **Procesamiento de Datos**: Pandas

- **Motor de Base de Datos**: SQLite

## ⚙️ Instalación
Este proyecto utiliza `uv`. Asegúrate de tenerlo instalado antes de comenzar.

1. Clonar el repositorio:

```bash
git clone https://github.com/sperezsa/test_etl.git
cd test_etl
```

2. Sincronizar el entorno y dependencias:

```bash
uv sync
```

## 📈 Flujo de Trabajo
Para operar con el proyecto, siga este orden:

1. **Preparación** (La bbdd ya viene con datos pero se puede volver a inicializar):

```bash
python scripts/setup_db.py
```

2. **Ejecución del proceso ETL** Genere el fichero consolidado de transacciones y clientes:

```bash
python main.py
```
*Este comando leerá `empresa2.db` y generará el CSV en `data/output/`.*


3. **Lanzamiento del Dashboard**
Visualice los datos procesados en el navegador:

```bash
streamlit run app.py
```
