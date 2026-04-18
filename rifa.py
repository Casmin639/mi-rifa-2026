import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS DE ALTO CONTRASTE
st.set_page_config(page_title="Gestor de Rifa Pro", layout="centered")

st.markdown("""
    <style>
    /* Fondo crema suave para la vista */
    .stApp { background-color: #FDF5E6; }
    
    /* Botones principales: Fondo oscuro y letras blancas para legibilidad total */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 50px; 
        font-weight: bold; 
        font-size: 16px; 
        background-color: #262730; 
        color: white;
        border: none;
    }
    
    /* Títulos en color café oscuro para que resalten sobre el crema */
    h1, h2, h3, .stMarkdown { 
        color: #4B3621 !important; 
    }

    /* Tarjetas de resumen con bordes definidos */
    div.stMetric { 
        background-color: white; 
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        border: 1px solid #E0C9A6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
if 'datos' not in st.session_state:
    # Cargamos tus datos de Excel conocidos
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
        # Asignamos estados: Azul para Pagados, Rojo para Mora
        estado = "Pagado" if n in ["21", "24", "27", "39", "42", "47", "53", "57", "67", "82", "91"] else ("En Mora" if nombre else "Disponible")
        st.session_state.datos[n] = {"nombre": nombre, "estado": estado}

# --- INTERFAZ ---
st.title("🏆 TABLERO DE CONTROL")

# Resumen de ventas con colores vivos
pagados = sum(1 for d in st.session_state.datos.values() if d["estado"] == "Pagado")
moras = sum(1 for d in st.session_state.datos.values() if d["estado"] == "En Mora")

c1, c2 = st.columns(2)
c1.metric("PAGADOS (Total)", f"{pagados}", f"${pagados*20000:,} COP")
c2.metric("EN MORA (Pendiente)", f"{moras}", f"${moras*20000:,} COP", delta_color="inverse")

st.write("---")
st.write("### 📲 Toca un número para gestionar")

# Grilla de 10x10 con iconos de alta visibilidad
for fila in range(10):
    cols = st.columns(10)
    for col in range(10):
        indice = fila * 10 + col
        n = f"{indice:02d}"
        est = st.session_state.datos[n]["estado"]
        
        # Usamos círculos de color grandes para que se vean a simple vista
        if est == "Pagado":
            label = f"🔵\n{n}"
        elif est == "En Mora":
            label = f"🔴\n{n}"
        else:
            label = f"\n{n}"

        if cols[col].button(label, key=n):
            st.session_state.seleccionado = n

# Formulario de edición táctil
if 'seleccionado' in st.session_state:
    num = st.session_state.seleccionado
    st.markdown(f"## 📝 Editando Número: {num}")
    
    with st.expander("Abrir detalles del cliente", expanded=True):
        nuevo_nombre = st.text_input("Nombre del Comprador", value=st.session_state.datos[num]["nombre"])
        nuevo_estado = st.selectbox("Estado de Pago", ["Disponible", "Pagado", "En Mora"], 
                                     index=["Disponible", "Pagado", "En Mora"].index(st.session_state.datos[num]["estado"]))
        
        col_save, col_cancel = st.columns(2)
        if col_save.button("✅ GUARDAR"):
            st.session_state.datos[num] = {"nombre": nuevo_nombre, "estado": nuevo_estado}
            del st.session_state.seleccionado
            st.rerun()
        if col_cancel.button("✖️ CANCELAR"):
            del st.session_state.seleccionado
            st.rerun()
