import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Gestión de Rifa 2026", page_icon="🎟️")

st.title("🎟️ Sistema de Gestión de Rifa")

# 1. Establecer conexión con Google Sheets
# Nota: Usa los secretos definidos en el Dashboard de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Lee la hoja de cálculo (usa ttl=0 para evitar caché y ver cambios inmediatos)
        return conn.read(ttl="0")
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

df = cargar_datos()

if df is not None:
    # --- TABLERO DE CONTROL ---
    st.subheader("🏆 TABLERO DE CONTROL")
    
    # Cálculos rápidos
    total_pagados = len(df[df['estado'].str.contains('Pagado', case=False, na=False)])
    # Asumiendo que el valor de cada número es $20,000 COP (ajustar según sea necesario)
    recaudado = total_pagados * 20000 
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("PAGADOS", total_pagados, f"${recaudado:,} COP")
    with col2:
        en_mora = len(df) - total_pagados
        st.metric("PENDIENTES / DISPONIBLES", en_mora)

    st.divider()

    # --- GESTIÓN DE NÚMEROS ---
    st.subheader("📝 Gestionar Números")
    
    # Selector de número basado en el índice o columna 'Número'
    # Si tu Excel no tiene columna 'Número', usamos el índice del DataFrame
    numero_seleccionado = st.selectbox("Selecciona un número para editar:", df.index)

    # Formulario para editar el registro seleccionado
    with st.form("form_edicion"):
        st.write(f"### Editando Número: {numero_seleccionado}")
        
        # Precargar datos actuales
        nombre_actual = df.loc[numero_seleccionado, 'nombre'] if 'nombre' in df.columns else ""
        telefono_actual = df.loc[numero_seleccionado, 'telefono'] if 'telefono' in df.columns else ""
        estado_actual = df.loc[numero_seleccionado, 'estado'] if 'estado' in df.columns else "Disponible"

        nuevo_nombre = st.text_input("Nombre del Comprador", value=nombre_actual)
        nuevo_telefono = st.text_input("Teléfono de contacto", value=telefono_actual)
        nuevo_estado = st.selectbox("Estado del pago", 
                                  options=["Disponible", "Pagado", "Apartado"], 
                                  index=["Disponible", "Pagado", "Apartado"].index(estado_actual) if estado_actual in ["Disponible", "Pagado", "Apartado"] else 0)

        boton_guardar = st.form_submit_button("💾 GUARDAR CAMBIOS")

        if boton_guardar:
            try:
                # Actualizar el DataFrame localmente
                df.loc[numero_seleccionado, 'nombre'] = nuevo_nombre
                df.loc[numero_seleccionado, 'telefono'] = nuevo_telefono
                df.loc[numero_seleccionado, 'estado'] = nuevo_estado
                
                # Subir los cambios a Google Sheets
                conn.update(data=df)
                st.success(f"✅ ¡Registro {numero_seleccionado} actualizado con éxito!")
                st.balloons()
                
            except Exception as e:
                st.error("No se pudo guardar: Verifica que el archivo de Google Sheets esté compartido como 'EDITOR' con el correo de la cuenta de servicio.")
                st.info("Error técnico: " + str(e))

    # --- VISTA GENERAL ---
    with st.expander("Ver lista completa de números"):
        st.dataframe(df, use_container_width=True)

else:
    st.warning("Configura los 'Secrets' en Streamlit Cloud para conectar con tu Google Sheet.")
