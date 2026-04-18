import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Rifa 2026", layout="centered")

# 2. Estilos visuales de alta visibilidad para móvil
st.markdown("""
    <style>
    .stApp { background-color: #FDF5E6; }
    
    /* Botones de números: más grandes para facilitar el toque */
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 60px; font-weight: 800; 
        background-color: #1E1E1E !important; color: white !important;
        border: 2px solid #4B3621 !important;
        font-size: 16px !important;
    }
    
    /* Tarjetas de métricas (Resumen superior) */
    div.stMetric { 
        background-color: #FFFFFF !important; 
        padding: 15px !important; 
        border-radius: 15px !important; 
        border: 2px solid #4B3621 !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05) !important;
    }
    
    /* Color de texto en métricas para que no se vea blanco */
    [data-testid="stMetricLabel"] { color: #1E1E1E !important; font-weight: 900 !important; }
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: 900 !important; }

    /* Títulos */
    h1 { font-size: 26px !important; text-align: center; color: #4B3621 !important; font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Conexión y Carga de Datos
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # Leer datos sin caché para ver cambios inmediatos
    df_raw = conn.read(spreadsheet=st.secrets["public_gsheets_url"], ttl="0s")
    
    # Asegurar columnas necesarias
    for col in ['numero', 'comprador', 'telefono', 'estado']:
        if col not in df_raw.columns:
            df_raw[col] = ""
            
    # Limpiar números (ej: 1.0 -> 01) y estados vacíos
    df_raw['numero'] = df_raw['numero'].astype(str).str.split('.').str[0].str.zfill(2)
    df_raw['estado'] = df_raw['estado'].apply(lambda x: str(x).strip() if pd.notna(x) else "Disponible")
    return df_raw

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.title("🏆 TABLERO DE CONTROL")

# Resumen de ventas
pagados = len(df[df['estado'].str.lower() == 'pagado'])
moras = len(df[df['estado'].str.lower() == 'en mora'])

c1, c2 = st.columns(2)
c1.metric("PAGADOS", f"{pagados}", f"${pagados*20000:,} COP")
c2.metric("EN MORA", f"{moras}", f"${moras*20000:,} COP")

st.divider()

# 4. VENTANA EMERGENTE (MODAL) PARA EDICIÓN
@st.dialog("📝 Gestionar Número")
def editar_numero(num_id):
    # Buscar datos del número seleccionado
    fila = df[df['numero'] == num_id]
    
    # Extraer valores actuales
    v_nombre = str(fila['comprador'].values[0]) if not fila.empty and pd.notna(fila['comprador'].values[0]) else ""
    v_tel = str(fila['telefono'].values[0]) if not fila.empty and pd.notna(fila['telefono'].values[0]) else ""
    v_estado = str(fila['estado'].values[0]).capitalize() if not fila.empty else "Disponible"

    st.write(f"Editando el número: **{num_id}**")
    
    nuevo_nom = st.text_input("Nombre del Comprador", value=v_nombre)
    nuevo_tel = st.text_input("Teléfono", value=v_tel)
    
    opciones = ["Disponible", "Pagado", "En Mora"]
    # Ajustar índice si el estado actual no está en la lista
    idx = opciones.index(v_estado) if v_estado in opciones else 0
    nuevo_est = st.selectbox("Estado del Pago", opciones, index=idx)
    
    st.write("---")
    if st.button("💾 GUARDAR CAMBIOS", use_container_width=True):
        # 1. Crear copia y actualizar la fila
        df_temp = df[df['numero'] != num_id].copy()
        nueva_fila = pd.DataFrame([{
            'numero': num_id, 
            'comprador': nuevo_nom, 
            'telefono': nuevo_tel, 
            'estado': nuevo_est
        }])
        df_final = pd.concat([df_temp, nueva_fila]).sort_values('numero')
        
        # 2. Intentar subir a Google Sheets (Asegúrate de que sea EDITOR)
        try:
            conn.update(
                spreadsheet=st.secrets["public_gsheets_url"], 
                data=df_final
            )
            st.success("¡Datos actualizados!")
            st.rerun() # Recarga la app para mostrar los círculos nuevos
        except Exception as err:
            st.error(f"No se pudo guardar: {err}")
            st.info("Revisa que el archivo de Google Sheets esté compartido como 'EDITOR'.")

# 5. GRILLA DE NÚMEROS (5 columnas para móvil)
st.write("### 📲 Toca un número")
for r in range(20): # 20 filas x 5 columnas = 100 números
    cols = st.columns(5)
    for c in range(5):
        index = r * 5 + c
        if index < 100:
            n_str = f"{index:02d}"
            
            # Obtener estado para el icono
            info = df[df['numero'] == n_str]
            estado_actual = info['estado'].values[0].lower() if not info.empty else "disponible"
            
            # Etiqueta con icono según estado
            label = n_str
            if "pagado" in estado_actual: label = f"🔵 {n_str}"
            elif "mora" in estado_actual: label = f"🔴 {n_str}"
            
            # Al hacer clic, abre el diálogo
            if cols[c].button(label, key=f"n_{n_str}"):
                editar_numero(n_str)
