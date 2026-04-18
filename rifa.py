import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Rifa 2026", layout="centered")

# 2. Estilos visuales de ALTA VISIBILIDAD
st.markdown("""
    <style>
    .stApp { background-color: #FDF5E6; }
    
    /* Diseño de los botones de números */
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 60px; font-weight: 800; 
        background-color: #1E1E1E !important; color: white !important;
        border: 2px solid #4B3621 !important;
    }
    
    /* Tarjetas de métricas (Resumen superior) */
    div.stMetric { 
        background-color: #FFFFFF !important; 
        padding: 20px !important; 
        border-radius: 15px !important; 
        border: 3px solid #4B3621 !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1) !important;
    }
    
    /* FORZAR COLOR NEGRO EN TEXTOS DE MÉTRICAS */
    [data-testid="stMetricLabel"] { 
        color: #1E1E1E !important; 
        font-weight: 900 !important; 
        font-size: 18px !important;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] { 
        color: #000000 !important; 
        font-weight: 900 !important;
        font-size: 40px !important;
    }
    [data-testid="stMetricDelta"] { 
        font-weight: 700 !important;
    }

    /* Títulos generales */
    h1, h2, h3 { color: #4B3621 !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Conexión y Carga de Datos
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_y_limpiar():
    df_raw = conn.read(spreadsheet=st.secrets["public_gsheets_url"], ttl="0s")
    for col in ['numero', 'comprador', 'telefono', 'estado']:
        if col not in df_raw.columns:
            df_raw[col] = ""
    df_raw['numero'] = df_raw['numero'].astype(str).str.split('.').str[0].str.zfill(2)
    df_raw['estado'] = df_raw['estado'].apply(lambda x: str(x).strip() if pd.notna(x) else "Disponible")
    return df_raw

try:
    df = cargar_y_limpiar()
except Exception as e:
    st.error(f"Error al leer la tabla: {e}")
    st.stop()

st.title("🏆 TABLERO DE CONTROL")

# 4. Resumen de Ventas
pagados = len(df[df['estado'].str.lower() == 'pagado'])
moras = len(df[df['estado'].str.lower() == 'en mora'])

c1, c2 = st.columns(2)
# Mostramos el conteo y el valor total recaudado/pendiente
c1.metric("PAGADOS (Total)", f"{pagados}", f"+ ${pagados*20000:,} COP", delta_color="normal")
c2.metric("EN MORA (Pendiente)", f"{moras}", f"- ${moras*20000:,} COP", delta_color="inverse")

st.divider()

# 5. Grilla de Números
st.write("### 📲 Selecciona un número para gestionar")
for r in range(10):
    cols = st.columns(10)
    for c in range(10):
        val = r * 10 + c
        n_str = f"{val:02d}"
        
        fila = df[df['numero'] == n_str]
        est = fila['estado'].values[0].lower() if not fila.empty else "disponible"
        
        label = n_str
        if "pagado" in est: label = f"🔵 {n_str}"
        elif "mora" in est: label = f"🔴 {n_str}"
        
        if cols[c].button(label, key=f"btn_{n_str}"):
            st.session_state.editando = n_str

# 6. Formulario de Edición
if 'editando' in st.session_state:
    num = st.session_state.editando
    st.markdown("---")
    st.subheader(f"📝 Gestionar Número {num}")
    
    actual = df[df['numero'] == num]
    
    with st.form("editor_form"):
        nombre_v = str(actual['comprador'].values[0]) if not actual.empty and pd.notna(actual['comprador'].values[0]) else ""
        tel_v = str(actual['telefono'].values[0]) if not actual.empty and pd.notna(actual['telefono'].values[0]) else ""
        estado_v = str(actual['estado'].values[0]).capitalize() if not actual.empty else "Disponible"
        
        nuevo_nom = st.text_input("Nombre del Comprador", value=nombre_v)
        nuevo_tel = st.text_input("Teléfono de contacto", value=tel_v)
        
        opciones = ["Disponible", "Pagado", "En Mora"]
        idx = opciones.index(estado_v) if estado_v in opciones else 0
        nuevo_est = st.selectbox("Estado del pago", opciones, index=idx)
        
        if st.form_submit_button("💾 ACTUALIZAR REGISTRO"):
            df_nuevo = df[df['numero'] != num].copy()
            fila_nueva = pd.DataFrame([{
                'numero': num, 
                'comprador': nuevo_nom, 
                'telefono': nuevo_tel, 
                'estado': nuevo_est
            }])
            df_final = pd.concat([df_nuevo, fila_nueva]).sort_values('numero')
            
            conn.update(spreadsheet=st.secrets["public_gsheets_url"], data=df_final)
            st.success(f"¡Número {num} actualizado!")
            del st.session_state.editando
            st.rerun()
