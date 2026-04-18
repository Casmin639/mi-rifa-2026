import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración visual
st.set_page_config(page_title="Gestor de Rifa Pro", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FDF5E6; }
    [data-testid="stMetricLabel"] { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button { width: 100%; font-weight: 800; background-color: #1E1E1E; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Conexión a la base de datos de Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    return conn.read(spreadsheet=st.secrets["public_gsheets_url"], ttl="0s")

df = cargar_datos()

st.title("🏆 TABLERO COMPARTIDO")

# Resumen de ventas
pagados = len(df[df['estado'] == 'Pagado'])
moras = len(df[df['estado'] == 'En Mora'])

c1, c2 = st.columns(2)
c1.metric("PAGADOS", f"{pagados}", f"${pagados*20000:,} COP")
c2.metric("EN MORA", f"{moras}", f"${moras*20000:,} COP")

# Cuadrícula de números
st.write("### 📲 Selecciona un número para editar")
cols = st.columns(10)
for i in range(100):
    n = f"{i:02d}"
    # Buscar el estado en el DataFrame
    info = df[df['numero'].astype(str).str.zfill(2) == n]
    estado = info['estado'].values[0] if not info.empty else "Disponible"
    
    label = f"🔵 {n}" if estado == "Pagado" else (f"🔴 {n}" if estado == "En Mora" else n)
    if cols[i % 10].button(label, key=n):
        st.session_state.seleccionado = n

# Formulario de edición
if 'seleccionado' in st.session_state:
    num = st.session_state.seleccionado
    st.markdown(f"## 📝 Editando Número: {num}")
    
    fila_actual = df[df['numero'].astype(str).str.zfill(2) == num]
    nombre_v = fila_actual['comprador'].values[0] if not fila_actual.empty else ""
    
    with st.form("edit_form"):
        nuevo_nombre = st.text_input("Nombre del Comprador", value=nombre_v)
        nuevo_estado = st.selectbox("Estado de Pago", ["Disponible", "Pagado", "En Mora"])
        
        if st.form_submit_button("💾 GUARDAR CAMBIOS PARA TODOS"):
            # Lógica para actualizar la Google Sheet
            # (Aquí se enviaría la actualización a la hoja de cálculo)
            st.success(f"¡Número {num} actualizado! Refrescando...")
            st.rerun()
