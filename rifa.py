import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración visual
st.set_page_config(page_title="Rifa 2026", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FDF5E6; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 60px; font-weight: 800; 
        background-color: #1E1E1E !important; color: white !important;
        border: 2px solid #4B3621 !important;
    }
    div.stMetric { 
        background-color: white; padding: 15px; border-radius: 12px; 
        border: 2px solid #4B3621;
    }
    [data-testid="stMetricLabel"] { color: #000000 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_y_limpiar():
    # Lee la tabla
    df_raw = conn.read(spreadsheet=st.secrets["public_gsheets_url"], ttl="0s")
    
    # Asegura que existan las columnas si la hoja es nueva
    for col in ['numero', 'comprador', 'telefono', 'estado']:
        if col not in df_raw.columns:
            df_raw[col] = ""
            
    # Limpia los datos: rellena vacíos y pone ceros a la izquierda en los números
    df_raw['numero'] = df_raw['numero'].astype(str).str.split('.').str[0].str.zfill(2)
    df_raw['estado'] = df_raw['estado'].fillna("Disponible").strip()
    return df_raw

df = cargar_y_limpiar()

st.title("🏆 TABLERO DE CONTROL")

# Métricas (Ignora si es mayúscula o minúscula en el Excel)
pagados = len(df[df['estado'].str.lower() == 'pagado'])
moras = len(df[df['estado'].str.lower() == 'en mora'])

c1, c2 = st.columns(2)
c1.metric("PAGADOS", f"{pagados}", f"${pagados*20000:,} COP")
c2.metric("EN MORA", f"{moras}", f"${moras*20000:,} COP")

# Grilla de números
st.write("### 📲 Selecciona para editar")
rows = 10
cols_count = 10
for r in range(rows):
    cols = st.columns(cols_count)
    for c in range(cols_count):
        val = r * 10 + c
        n_str = f"{val:02d}"
        
        # Buscar estado
        info = df[df['numero'] == n_str]
        est = info['estado'].values[0].lower() if not info.empty else "disponible"
        
        label = n_str
        if "pagado" in est: label = f"🔵 {n_str}"
        elif "mora" in est: label = f"🔴 {n_str}"
        
        if cols[c].button(label, key=n_str):
            st.session_state.editando = n_str

# Formulario de guardado
if 'editando' in st.session_state:
    num = st.session_state.editando
    st.divider()
    st.subheader(f"📝 Editar Número {num}")
    
    actual = df[df['numero'] == num]
    with st.form("editor"):
        nom = st.text_input("Comprador", value=str(actual['comprador'].values[0]) if not actual.empty else "")
        tel = st.text_input("Teléfono", value=str(actual['telefono'].values[0]) if not actual.empty else "")
        est_opciones = ["Disponible", "Pagado", "En Mora"]
        # Intenta marcar la opción actual
        idx = 0
        if not actual.empty:
            curr_est = str(actual['estado'].values[0]).capitalize()
            if curr_est in est_opciones: idx = est_opciones.index(curr_est)

        nuevo_est = st.selectbox("Estado", est_opciones, index=idx)
        
        if st.form_submit_button("💾 GUARDAR CAMBIOS"):
            # Actualizar DataFrame
            df = df[df['numero'] != num] # Borra el viejo
            nueva_fila = pd.DataFrame([{'numero': num, 'comprador': nom, 'telefono': tel, 'estado': nuevo_est}])
            df = pd.concat([df, nueva_fila]).sort_values('numero')
            
            # Subir a Google Sheets
            conn.update(spreadsheet=st.secrets["public_gsheets_url"], data=df)
            st.success(f"¡Número {num} actualizado!")
            del st.session_state.editando
            st.rerun()
