import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Rifa 2026", layout="centered")

# 2. Estilos visuales optimizados para Móvil
st.markdown("""
    <style>
    .stApp { background-color: #FDF5E6; }
    
    /* Botones más grandes para dedos en móvil */
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 55px; font-weight: 800; 
        background-color: #1E1E1E !important; color: white !important;
        border: 2px solid #4B3621 !important;
        font-size: 14px !important;
    }
    
    /* Tarjetas de métricas */
    div.stMetric { 
        background-color: #FFFFFF !important; 
        padding: 15px !important; 
        border-radius: 15px !important; 
        border: 2px solid #4B3621 !important;
    }
    
    [data-testid="stMetricLabel"] { color: #1E1E1E !important; font-weight: 900 !important; }
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: 900 !important; }

    /* Ajuste de títulos */
    h1 { font-size: 24px !important; text-align: center; color: #4B3621 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Conexión y Carga
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_y_limpiar():
    df_raw = conn.read(spreadsheet=st.secrets["public_gsheets_url"], ttl="0s")
    for col in ['numero', 'comprador', 'telefono', 'estado']:
        if col not in df_raw.columns:
            df_raw[col] = ""
    df_raw['numero'] = df_raw['numero'].astype(str).str.split('.').str[0].str.zfill(2)
    df_raw['estado'] = df_raw['estado'].apply(lambda x: str(x).strip() if pd.notna(x) else "Disponible")
    return df_raw

df = cargar_y_limpiar()

# --- INTERFAZ ---
st.title("🏆 CONTROL DE RIFA")

# Métricas
pagados = len(df[df['estado'].str.lower() == 'pagado'])
moras = len(df[df['estado'].str.lower() == 'en mora'])

c1, c2 = st.columns(2)
c1.metric("PAGADOS", f"{pagados}", f"${pagados*20000:,} COP")
c2.metric("EN MORA", f"{moras}", f"${moras*20000:,} COP")

st.divider()

# 4. VENTANA EMERGENTE (MODAL)
@st.dialog("📝 Gestionar Número")
def editar_numero(num_seleccionado):
    actual = df[df['numero'] == num_seleccionado]
    
    # Valores actuales
    nombre_v = str(actual['comprador'].values[0]) if not actual.empty and pd.notna(actual['comprador'].values[0]) else ""
    tel_v = str(actual['telefono'].values[0]) if not actual.empty and pd.notna(actual['telefono'].values[0]) else ""
    estado_v = str(actual['estado'].values[0]).capitalize() if not actual.empty else "Disponible"

    st.write(f"Estás editando el número: **{num_seleccionado}**")
    
    nuevo_nom = st.text_input("Nombre del Comprador", value=nombre_v)
    nuevo_tel = st.text_input("Teléfono", value=tel_v)
    
    opciones = ["Disponible", "Pagado", "En Mora"]
    idx = opciones.index(estado_v) if estado_v in opciones else 0
    nuevo_est = st.selectbox("Estado del pago", opciones, index=idx)
    
    st.write("---")
    if st.button("💾 GUARDAR CAMBIOS", use_container_width=True):
        # Procesar datos
        df_nuevo = df[df['numero'] != num_seleccionado].copy()
        fila_nueva = pd.DataFrame([{
            'numero': num_seleccionado, 
            'comprador': nuevo_nom, 
            'telefono': nuevo_tel, 
            'estado': nuevo_est
        }])
        df_final = pd.concat([df_nuevo, fila_nueva]).sort_values('numero')
        
        # Subir a la nube
        conn.update(spreadsheet=st.secrets["public_gsheets_url"], data=df_final)
        st.success("¡Guardado!")
        st.rerun()

# 5. GRILLA DE NÚMEROS
# Usamos columnas pequeñas para que quepan bien en móvil
for r in range(20): # 20 filas de 5 columnas para que se vea mejor en vertical
    cols = st.columns(5)
    for c in range(5):
        val = r * 5 + c
        if val < 100:
            n_str = f"{val:02d}"
            
            fila = df[df['numero'] == n_str]
            est = fila['estado'].values[0].lower() if not fila.empty else "disponible"
            
            label = n_str
            if "pagado" in est: label = f"🔵 {n_str}"
            elif "mora" in est: label = f"🔴 {n_str}"
            
            if cols[c].button(label, key=f"btn_{n_str}"):
                editar_numero(n_str)
