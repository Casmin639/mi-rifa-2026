import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Gestor de Rifa Pro", layout="centered")

# 2. Diseño Visual de Alto Contraste
st.markdown("""
    <style>
    .stApp { background-color: #FDF5E6; }
    
    /* Botones de números */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 60px; 
        font-weight: 800; 
        font-size: 16px; 
        background-color: #1E1E1E !important; 
        color: white !important;
        border: 2px solid #4B3621 !important;
        margin-bottom: 5px;
    }
    
    /* Tarjetas de resumen */
    div.stMetric { 
        background-color: white; 
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        border: 2px solid #4B3621;
    }
    
    /* Textos de métricas forzados a Negro */
    [data-testid="stMetricLabel"] {
        color: #000000 !important;
        font-size: 15px !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricValue"] {
        color: #1E1E1E !important;
    }

    /* Títulos y textos */
    h1, h2, h3, p { 
        color: #4B3621 !important; 
        font-weight: 800 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # ttl=0 para que siempre traiga lo último que se guardó
    return conn.read(spreadsheet=st.secrets["public_gsheets_url"], ttl="0s")

try:
    df = cargar_datos()
    # Limpieza de datos por seguridad
    df['numero'] = df['numero'].astype(str).str.zfill(2)
    df['estado'] = df['estado'].fillna("Disponible")
except Exception as e:
    st.error("Error al conectar con Google Sheets. Revisa la URL en Secrets.")
    st.stop()

st.title("🏆 CONTROL DE RIFA")

# 4. Resumen de Ventas
# Convertimos a minúsculas para contar sin errores de dedo (Pagado vs pagado)
pagados = len(df[df['estado'].str.lower() == 'pagado'])
moras = len(df[df['estado'].str.lower() == 'en mora'])

c1, c2 = st.columns(2)
c1.metric("TOTAL PAGADOS", f"{pagados}", f"${pagados*20000:,} COP")
c2.metric("POR COBRAR (Mora)", f"{moras}", f"${moras*20000:,} COP")

st.divider()

# 5. Grilla de Números (10 columnas)
st.write("### 📲 Toca un número para gestionar")
for fila in range(10):
    cols = st.columns(10)
    for col in range(10):
        idx = fila * 10 + col
        n_str = f"{idx:02d}"
        
        # Buscar estado actual
        dato_num = df[df['numero'] == n_str]
        estado_actual = dato_num['estado'].values[0] if not dato_num.empty else "Disponible"
        
        # Definir emoji por estado
        if estado_actual.lower() == "pagado":
            label = f"🔵\n{n_str}"
        elif estado_actual.lower() == "en mora":
            label = f"🔴\n{n_str}"
        else:
            label = f"\n{n_str}"
            
        if cols[col].button(label, key=f"btn_{n_str}"):
            st.session_state.seleccionado = n_str

# 6. Formulario de Edición (aparece al tocar un botón)
if 'seleccionado' in st.session_state:
    num = st.session_state.seleccionado
    st.markdown(f"### 📝 Editando Número: {num}")
    
    fila_actual = df[df['numero'] == num]
    # Extraer valores actuales o poner vacíos
    val_nombre = fila_actual['comprador'].values[0] if not fila_actual.empty else ""
    val_tel = fila_actual['telefono'].values[0] if not fila_actual.empty else ""
    val_est = fila_actual['estado'].values[0] if not fila_actual.empty else "Disponible"

    with st.form("form_edicion"):
        nuevo_nom = st.text_input("Nombre del Comprador", value=str(val_nombre) if pd.notna(val_nombre) else "")
        nuevo_tel = st.text_input("Teléfono", value=str(val_tel) if pd.notna(val_tel) else "")
        # Normalizamos la lista para el selector
        opciones = ["Disponible", "Pagado", "En Mora"]
        idx_opcion = opciones.index(val_est) if val_est in opciones else 0
        nuevo_est = st.selectbox("Estado", opciones, index=idx_opcion)
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.form_submit_button("✅ GUARDAR"):
            # Actualizar el DataFrame local
            # Quitamos la fila vieja y ponemos la nueva
            df = df[df['numero'] != num]
            nueva_fila = pd.DataFrame([{'numero': num, 'comprador': nuevo_nom, 'telefono': nuevo_tel, 'estado': nuevo_est}])
            df = pd.concat([df, nueva_fila]).sort_values('numero')
            
            # Subir a Google Sheets (Asegúrate que la pestaña se llame Sheet1)
            conn.update(worksheet="Sheet1", data=df)
            
            st.success(f"¡Número {num} guardado con éxito!")
            del st.session_state.seleccionado
            st.rerun()
            
        if col_btn2.form_submit_button("❌ CANCELAR"):
            del st.session_state.seleccionado
            st.rerun()
