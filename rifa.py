import streamlit as st
import pandas as pd

# Configuración visual
st.set_page_config(page_title="Gestor de Rifa Pro", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FDF5E6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 45px; font-weight: bold; font-size: 14px; }
    div.stMetric { background-color: white; padding: 10px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS TEMPORAL ---
# Nota: En la web, si se reinicia la página se pierden los datos.
# Para ventas reales, luego conectaremos Google Sheets.
if 'datos' not in st.session_state:
    # Datos iniciales basados en tu lista de Excel
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

# --- INTERFAZ ---
st.title("🏆 TABLERO DE CONTROL")

# Resumen
pagados = sum(1 for d in st.session_state.datos.values() if d["estado"] == "Pagado")
moras = sum(1 for d in st.session_state.datos.values() if d["estado"] == "En Mora")

c1, c2 = st.columns(2)
c1.metric("Pagados", f"{pagados}", f"${pagados*20000:,} COP")
c2.metric("En Mora", f"{moras}", f"${moras*20000:,} COP", delta_color="inverse")

# Grilla de 10x10
st.write("### Selecciona un número")
for fila in range(10):
    cols = st.columns(10)
    for col in range(10):
        indice = fila * 10 + col
        n = f"{indice:02d}"
        est = st.session_state.datos[n]["estado"]
        
        # Colores solicitados
        color_btn = "secondary" # Blanco por defecto
        if est == "Pagado":
            label = f"🔵 {n}" # Representación visual del azul claro
        elif est == "En Mora":
            label = f"🔴 {n}" # Representación visual del rojo
        else:
            label = n

        if cols[col].button(label, key=n):
            st.session_state.seleccionado = n

# Formulario de edición (al hacer clic)
if 'seleccionado' in st.session_state:
    num = st.session_state.seleccionado
    st.divider()
    st.subheader(f"📝 Editar Número {num}")
    
    with st.container():
        nuevo_nombre = st.text_input("Nombre del Comprador", value=st.session_state.datos[num]["nombre"])
        nuevo_estado = st.selectbox("Estado de Pago", ["Disponible", "Pagado", "En Mora"], 
                                     index=["Disponible", "Pagado", "En Mora"].index(st.session_state.datos[num]["estado"]))
        
        if st.button("✅ Guardar Cambios"):
            st.session_state.datos[num] = {"nombre": nuevo_nombre, "estado": nuevo_estado}
            del st.session_state.seleccionado
            st.rerun()
