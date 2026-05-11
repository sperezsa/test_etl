from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px



# Configuración de la página
st.set_page_config(page_title="Dashboard de Transacciones", layout="wide")

st.title("📊 Monitor de Transacciones de pruebas")

# 1. Cargar datos
@st.cache_data # Esto hace que la app sea ultra rápida al recargar
def load_data():
    # 1. Obtenemos la carpeta donde está este script actual
    base_path = Path(__file__).parent
    
    # 2. Construimos la ruta relativa hacia la carpeta de salida
    ruta = base_path / "data" / "output" / "EJEMPLO_TABLON_COMBINADO.csv"
    
    # 3. Verificamos si el archivo existe antes de leerlo para evitar errores
    if not ruta.exists():
        st.error(f"No se encuentra el archivo en: {ruta}")
        return pd.DataFrame() # Devolvemos un dataframe vacío para que no explote la app

    df = pd.read_csv(ruta, sep=';')
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

df = load_data()

# 2. Barra lateral para filtros
st.sidebar.header("Filtros")
limite = st.sidebar.slider("Definir límite de alerta", 0, 6000, 1000)
paises = st.sidebar.multiselect("Seleccionar Países", df['pais'].unique(), default=df['pais'].unique())

# Filtrar dataframe según los controles
df_filtrado = df[df['pais'].isin(paises)]

# 3. Crear el gráfico de Plotly
fig = px.scatter(df_filtrado, x="fecha", y="monto", 
                 color="nivel_riesgo", hover_data=['nombre'],
                 title=f"Transacciones (Límite: {limite}€)")

fig.add_hline(y=limite, line_dash="dot", line_color="red",
              annotation_text=f"Alerta {limite}€", 
              annotation_font=dict(color="red"))

# 4. Mostrar en Streamlit
col1, col2 = st.columns([3, 1])

with col1:
    #st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig, width='stretch')

with col2:
    st.metric("Total Transacciones", len(df_filtrado))
    st.metric("Máximo Importe", f"{df_filtrado['monto'].max()} €")

st.write("### Datos Brutos", df_filtrado)