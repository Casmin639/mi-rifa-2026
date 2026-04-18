import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Rifa 2026", layout="centered")

# 2. Estilos visuales (Corrigiendo visibilidad de textos)
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
    /* Forzar color negro en las etiquetas de métricas */
    [data-testid="stMetricLabel"] { 
        color: #000000 !important; 
        font-weight: 900 !important; 
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_y_limpiar():
    # Cargar datos frescos
    df_raw = conn.read(spreadsheet=st.secrets["public_gsheets_url"], ttl="0s")
    
    # Asegurar que existan las columnas exactas de tu tabla
    for col in ['numero', 'comprador', 'telefono', 'estado']:
        if col not in df_raw.columns:
            df_raw[col] = ""
            
    # Limpieza segura de datos
    df_raw['numero'] = df_raw['numero'].astype(str).str.split('.').str[0].str.zfill(2)
    # Corregido: Limpieza de texto celda por celda para evitar el AttributeError
    df_raw['estado'] = df_raw['estado'].apply(lambda x: str(x).strip() if pd.notna(x) else "Disponible")
    
    return df_raw

try:
    df = cargar_y_limpiar()
except Exception as e:
    st.error(f"Error al leer la tabla: {e}")
    st.stop()

st.title("🏆 TABLERO DE CONTROL")

# 4. Métricas
pagados = len(df[df['estado'].str.lower() == 'pagado'])
moras = len(df[df['estado'].str.lower() == 'en mora'])

c1, c2 = st.columns(2)
c1.metric("PAGADOS", f"{pagados}", f"${pagados*20000:,} COP")
c2.metric("EN MORA", f"{moras}", f"${moras*20000:,} COP")

st.divider()

# 5. Grilla de Números
st.write("### 📲 Selecciona un número")
for r in range(10):
    cols = st.columns(10)
    for c in range(10):
        val = r * 10 + c
        n_str = f"{val:02d}"
        
        fila = df[df['numero'] == n_str]
        est = fila['estado'].values[0].lower() if not fila.empty else "disponible"
        
        # Color del botón según estado
        label = n_str
        if "pagado" in est: label = f"🔵 {n_str}"
        elif "mora" in est: label = f"🔴 {n_str}"
        
        if cols[c].button(label, key=f"btn_{n_str}"):
            st.session_state.editando = n_str

# 6. Formulario para guardar
if 'editando' in st.session_state:
    num = st.session_state.editando
    st.markdown("---")
    st.subheader(f"📝 Gestionar Número {num}")
    
    actual = df[df['numero'] == num]
    
    with st.form("editor_form"):
        # Extraer valores de la tabla
        nombre_v = str(actual['comprador'].values[0]) if not actual.empty and pd.notna(actual['comprador'].values[0]) else ""
        tel_v = str(actual['telefono'].values[0]) if not actual.empty and pd.notna(actual['telefono'].values[0]) else ""
        estado_v = str(actual['estado'].values[0]).capitalize() if not actual.empty else "Disponible"
        
        nuevo_nom = st.text_input("Nombre", value=nombre_v)
        nuevo_tel = st.text_input("Teléfono", value=tel_v)
        
        opciones = ["Disponible", "Pagado", "En Mora"]
        idx = opciones.index(estado_v) if estado_v in opciones else 0
        nuevo_est = st.selectbox("Estado", opciones, index=idx)
        
        if st.form_submit_button("💾 ACTUALIZAR EN GOOGLE SHEETS"):
            # Crear nueva fila y actualizar el tablero
            df_nuevo = df[df['numero'] != num].copy()
            fila_nueva = pd.DataFrame([{
                'numero': num, 
                'comprador': nuevo_nom, 
                'telefono': nuevo_tel, 
                'estado': nuevo_est
            }])
            df_final = pd.concat([df_nuevo, fila_nueva]).sort_values('numero')
            
            # Guardar en la nube
            conn.update(spreadsheet=st.secrets["public_gsheets_url"], data=df_final)
            
            st.success(f"¡Número {num} actualizado con éxito!")
            del st.session_state.editando
            st.rerun()
