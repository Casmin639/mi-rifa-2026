import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Rifa 2026", layout="centered")

# Reemplaza esta URL con la de tu archivo de Google Sheets
URL_DE_MI_HOJA = "TU_URL_DE_GOOGLE_SHEETS_AQUI"

# Estilos visuales
st.markdown("""
    <style>
    .stApp { background-color: #FDF5E6; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 60px; font-weight: 800; 
        background-color: #1E1E1E !important; color: white !important;
        border: 2px solid #4B3621 !important;
    }
    div.stMetric { 
        background-color: #FFFFFF !important; padding: 15px !important; 
        border-radius: 15px !important; border: 2px solid #4B3621 !important;
    }
    [data-testid="stMetricLabel"] { color: #1E1E1E !important; font-weight: 900 !important; }
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# Conexión profesional usando la configuración de Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # Se añade la URL directamente aquí para evitar el ValueError
    df_raw = conn.read(spreadsheet=URL_DE_MI_HOJA, ttl="0s")
    df_raw.columns = df_raw.columns.str.lower()
    for col in ['numero', 'comprador', 'telefono', 'estado']:
        if col not in df_raw.columns: df_raw[col] = ""
    df_raw['numero'] = df_raw['numero'].astype(str).str.split('.').str[0].str.zfill(2)
    df_raw['estado'] = df_raw['estado'].fillna("Disponible").str.strip()
    return df_raw

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.stop()

st.title("🏆 TABLERO DE CONTROL")

# Métricas
pagados = len(df[df['estado'].str.lower() == 'pagado'])
moras = len(df[df['estado'].str.lower() == 'en mora'])
c1, c2 = st.columns(2)
c1.metric("PAGADOS", f"{pagados}", f"${pagados*20000:,} COP")
c2.metric("EN MORA", f"{moras}", f"${moras*20000:,} COP")

st.divider()

@st.dialog("📝 Gestionar Número")
def editar_numero(num_id):
    fila = df[df['numero'] == num_id]
    v_nombre = str(fila['comprador'].values[0]) if not fila.empty else ""
    v_tel = str(fila['telefono'].values[0]) if not fila.empty else ""
    v_estado = str(fila['estado'].values[0]).capitalize() if not fila.empty else "Disponible"

    nuevo_nom = st.text_input("Nombre", value=v_nombre)
    nuevo_tel = st.text_input("Teléfono", value=v_tel)
    opciones = ["Disponible", "Pagado", "En Mora"]
    nuevo_est = st.selectbox("Estado", opciones, index=opciones.index(v_estado) if v_estado in opciones else 0)
    
    if st.button("💾 GUARDAR CAMBIOS", use_container_width=True):
        df_temp = df[df['numero'] != num_id].copy()
        nueva_fila = pd.DataFrame([{'numero': num_id, 'comprador': nuevo_nom, 'telefono': nuevo_tel, 'estado': nuevo_est}])
        df_final = pd.concat([df_temp, nueva_fila]).sort_values('numero')
        
        try:
            # Se especifica la hoja para la actualización exitosa
            conn.update(spreadsheet=URL_DE_MI_HOJA, data=df_final)
            st.success("¡Registro actualizado exitosamente!")
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo guardar: {e}")

# Grilla de números
for r in range(20):
    cols = st.columns(5)
    for c in range(5):
        index = r * 5 + c
        if index < 100:
            n_str = f"{index:02d}"
            est_serie = df[df['numero'] == n_str]['estado']
            est = est_serie.values[0].lower() if not est_serie.empty else "disponible"
            label = n_str
            if "pagado" in est: label = f"🔵 {n_str}"
            elif "mora" in est: label = f"🔴 {n_str}"
            
            if cols[c].button(label, key=f"n_{n_str}"):
                editar_numero(n_str)
