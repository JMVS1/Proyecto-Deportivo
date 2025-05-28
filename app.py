import streamlit as st
import csv
import os
import pandas as pd

# -------------------------
# Configuracion de la pagina
# -------------------------
st.set_page_config(page_title="Análisis y Apuestas", layout="centered")

# -------------------------
# Estilo personalizado
# -------------------------
st.markdown("""
    <style>
        .main { background-color: #f9f9f9; }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1em;
        }
        .stTextInput > div > div > input {
            font-weight: bold;
            color: #333333;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# TITULO PRINCIPAL
# -------------------------
st.title("📊 Análisis del Local y Registro de Apuestas")

# -------------------------
# TABS
# -------------------------
analisis_tab, registro_tab = st.tabs(["🔍 Análisis del Equipo Local", "📝 Registro de Apuestas"])

# -------------------------
# TAB 1: ANÁLISIS LOCAL
# -------------------------
with analisis_tab:
    st.header("Análisis del Equipo Local")

    equipo_local = st.text_input("Nombre del equipo local:", "Equipo Local")
    st.markdown(f"### 📌 Análisis para: **{equipo_local}**")

    def calcular_ponderado(ganados, empatados, total_partidos, peso):
        perdidos = total_partidos - ganados - empatados
        pct_g = (ganados / total_partidos) * peso
        pct_e = (empatados / total_partidos) * peso
        pct_p = (perdidos / total_partidos) * peso
        return pct_g, pct_e, pct_p

    st.subheader("1. Enfrentamientos Directos (40%)")
    ganados_h2h = st.number_input("Ganados (H2H)", 0, 6, step=1)
    empatados_h2h = st.number_input("Empatados (H2H)", 0, 6, step=1)
    pct_g_h2h, pct_e_h2h, pct_p_h2h = calcular_ponderado(ganados_h2h, empatados_h2h, 6, 0.40)

    st.subheader("2. Rendimiento como Local (30%)")
    ganados_local = st.number_input("Ganados (Local)", 0, 6, step=1)
    empatados_local = st.number_input("Empatados (Local)", 0, 6, step=1)
    pct_g_local, pct_e_local, pct_p_local = calcular_ponderado(ganados_local, empatados_local, 6, 0.30)

    st.subheader("3. Resultados Generales (30%)")
    ganados_general = st.number_input("Ganados (General)", 0, 6, step=1)
    empatados_general = st.number_input("Empatados (General)", 0, 6, step=1)
    pct_g_general, pct_e_general, pct_p_general = calcular_ponderado(ganados_general, empatados_general, 6, 0.30)

    total_g = pct_g_h2h + pct_g_local + pct_g_general
    total_e = pct_e_h2h + pct_e_local + pct_e_general
    total_p = pct_p_h2h + pct_p_local + pct_p_general

    st.markdown("---")
    st.subheader("📈 Resultado Ponderado Final")
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Gana", f"{total_g*100:.1f}%")
    col2.metric("🤝 Empata", f"{total_e*100:.1f}%")
    col3.metric("❌ Pierde", f"{total_p*100:.1f}%")

    resultado = {
        "Gana": total_g,
        "Empata": total_e,
        "Pierde": total_p
    }
    top2 = sorted(resultado.items(), key=lambda x: x[1], reverse=True)[:2]
    doble_opcion = ""
    if {"Gana", "Empata"}.issubset(dict(top2)):
        doble_opcion = "1X (Gana o Empata)"
    elif {"Empata", "Pierde"}.issubset(dict(top2)):
        doble_opcion = "X2 (Empata o Pierde)"
    else:
        doble_opcion = "12 (Gana o Pierde)"

    st.markdown(f"### 🧠 Mejor Doble Oportunidad: **{doble_opcion}**")

# -------------------------
# TAB 2: REGISTRO DE APUESTAS
# -------------------------
with registro_tab:
    archivo_csv = "historial_apuestas.csv"

    if not os.path.isfile(archivo_csv):
        with open(archivo_csv, mode='w', newline='', encoding='latin-1') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Jornada",
                "Cuota A1", "Resultado A1", "Apuesta A1", "Ganancia A1",
                "Cuota A2", "Resultado A2", "Apuesta A2", "Ganancia A2",
                "Utilidad", "Banca Total"
            ])

    if "monto_a1" not in st.session_state:
        st.session_state.monto_a1 = 1000
        st.session_state.monto_a2 = 2000
        st.session_state.banca = 0
        st.session_state.jornada = 1
        st.session_state.registrar = False

    st.subheader(f"🎯 Jornada {st.session_state.jornada}")
    st.write(f"💸 Apuesta 1: ${st.session_state.monto_a1}")
    st.write(f"💸 Apuesta 2: ${st.session_state.monto_a2}")

    cuota1 = st.number_input("Cuota Apuesta 1", min_value=2.0, step=0.1, key="cuota1")
    cuota2 = st.number_input("Cuota Apuesta 2", min_value=2.0, step=0.1, key="cuota2")
    gano_a1 = st.radio("¿Ganó la Apuesta 1?", ["Sí", "No"], key="gano1") == "Sí"
    gano_a2 = st.radio("¿Ganó la Apuesta 2?", ["Sí", "No"], key="gano2") == "Sí"

    if st.button("Registrar jornada"):
        st.session_state.registrar = True

    if st.session_state.get("registrar", False):
        st.session_state.registrar = False

        ganancia_a1 = st.session_state.monto_a1 * cuota1 if gano_a1 else 0
        ganancia_a2 = st.session_state.monto_a2 * cuota2 if gano_a2 else 0

        total_apostado = st.session_state.monto_a1 + st.session_state.monto_a2
        utilidad = (ganancia_a1 + ganancia_a2) - total_apostado
        st.session_state.banca += utilidad

        with open(archivo_csv, mode='a', newline='', encoding='latin-1') as file:
            writer = csv.writer(file)
            writer.writerow([
                st.session_state.jornada,
                round(cuota1, 2), "GANÓ" if gano_a1 else "PERDIÓ", st.session_state.monto_a1, round(ganancia_a1, 2),
                round(cuota2, 2), "GANÓ" if gano_a2 else "PERDIÓ", st.session_state.monto_a2, round(ganancia_a2, 2),
                round(utilidad, 2), round(st.session_state.banca, 2)
            ])

        st.success("✅ Jornada registrada")
        st.write(f"📈 Ganancia A1: ${ganancia_a1:,.2f}")
        st.write(f"📈 Ganancia A2: ${ganancia_a2:,.2f}")
        st.write(f"💸 Total Apostado: ${total_apostado:,.2f}")
        st.write(f"📊 Utilidad jornada: ${utilidad:,.2f}")
        st.write(f"💰 Banca total acumulada: ${st.session_state.banca:,.2f}")

        st.session_state.monto_a1 = 1000 if gano_a1 else st.session_state.monto_a1 * 2
        st.session_state.monto_a2 = 1000 if gano_a2 else st.session_state.monto_a2 * 2
        st.session_state.jornada += 1

    # Mostrar historial si existe
    if os.path.isfile(archivo_csv):
        st.markdown("### 📜 Historial de Jornadas")
        try:
            with open(archivo_csv, encoding="latin-1") as f:
                df_historial = pd.read_csv(f)
                st.dataframe(df_historial)
        except Exception as e:
            st.warning(f"No se pudo cargar el historial: {e}")

        # Botón para borrar historial
        if st.button("🗑️ Borrar historial"):
            os.remove(archivo_csv)
            st.success("Historial borrado correctamente.")
            st.rerun()
