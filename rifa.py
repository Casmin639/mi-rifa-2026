import streamlit as st

# 1. CONFIGURACIÓN Y ESTILOS DE MÁXIMA VISIBILIDAD
st.set_page_config(page_title="Gestor de Rifa Pro", layout="centered")

st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color: #FDF5E6; }
    
    /* BOTONES: Números grandes y legibles */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 60px; 
        font-weight: 800; 
        font-size: 18px; 
        background-color: #1E1E1E; 
        color: white;
        border: 2px solid #4B3621;
    }
    
    /* TARJETAS DE RESUMEN: Forzar color de etiquetas */
    div.stMetric { 
        background-color: white; 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        border: 2px solid #4B3621;
    }
    
    /* ESTO ARREGLA LOS TEXTOS INVISIBLES QUE ME MOSTRASTE */
    /* Forzamos el color negro (#000000) en las etiquetas de métricas */
    [data-testid="stMetricLabel"] {
        color: #000000 !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        opacity: 1 !important;
    }
    
    /* Color para los números grandes del resumen */
    [data-testid="stMetricValue"] {
        color: #1E1E1E !important;
    }

    h1, h2, h3 { color: #4B3621 !important; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# --- EL RESTO DEL CÓDIGO SIGUE IGUAL ---
if 'datos' not in st.session_state:
    excel_data = {
        "00": "Jose Rivera", "02": "Tia Adriana", "04": "Diana castrillon", "21": "Amanda",
        "24": "Johana prima", "27": "Carolina Fiserv", "39": "Alejo (tia)", "42": "Johana prima",
        "47": "Alejo (tia)", "53": "Prima Luisa", "57": "Tia menchis", "67": "Claudia Prima",
        "82": "Prima Luisa", "91": "Saris (Fiserv)"
    }
    st.session_state.datos = {}
    for i in range(100):
        n = f"{i:02d}"
        nombre = excel_data.get(n, "")
        estado = "Pagado" if n in ["21", "24", "27", "39", "42", "47", "53", "57", "67", "82", "91"] else ("En Mora" if nombre else "Disponible")
        st.session_state.datos[n] = {"nombre": nombre, "estado": estado}

st.title("🏆 TABLERO DE CONTROL")

pagados = sum(1 for d in st.session_state.datos.values() if d["estado"] == "Pagado")
moras = sum(1 for d in st.session_state.datos.values() if d["estado"] == "En Mora")

c1, c2 = st.columns(2)
c1.metric("PAGADOS", f"{pagados}", f"${pagados*20000:,} COP")
c2.metric("EN MORA", f"{moras}", f"${moras*20000:,} COP", delta_color="inverse")

st.write("### 📲 Toca un número para gestionar")

for fila in range(10):
    cols = st.columns(10)
    for col in range(10):
        indice = fila * 10 + col
        n = f"{indice:02d}"
        est = st.session_state.datos[n]["estado"]
        label = f"🔵 {n}" if est == "Pagado" else (f"🔴 {n}" if est == "En Mora" else n)
        if cols[col].button(label, key=n):
            st.session_state.seleccionado = n

if 'seleccionado' in st.session_state:
    num = st.session_state.seleccionado
    st.markdown(f"## 📝 Editando: {num}")
    with st.expander("DETALLES DEL CLIENTE", expanded=True):
        nuevo_nombre = st.text_input("Nombre", value=st.session_state.datos[num]["nombre"])
        nuevo_estado = st.selectbox("Estado", ["Disponible", "Pagado", "En Mora"], 
                                     index=["Disponible", "Pagado", "En Mora"].index(st.session_state.datos[num]["estado"]))
        if st.button("✅ GUARDAR"):
            st.session_state.datos[num] = {"nombre": nuevo_nombre, "estado": nuevo_estado}
            del st.session_state.seleccionado
            st.rerun()
