import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Reporte Exceso Vicuña", layout="centered")

# ---- Estilos CSS (modo oscuro) ----
st.markdown("""
    <style>
        body { background-color: #0E1117; color: #FAFAFA; }
        h1, label, p { color: #FAFAFA !important; }
        .stTextInput, .stTextArea, .stNumberInput { background-color: #1E1E1E !important; color: white !important; }
        .stButton>button { background-color: #6200EE; color: white; border-radius: 8px; padding: 0.6em 1.2em; }
        .stButton>button:hover { background-color: #3700B3; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Control de Exceso de Velocidad - Proyecto Vicuña")

# ---- Formulario ----
with st.form("formulario"):
    hora = st.text_input("⏰ Hora del registro (ej: 09:52)")
    chofer = st.text_input("👤 Chofer (Nombre y Apellido)")
    dni = st.text_input("🪪 DNI del chofer")
    empresa = st.text_input("🏢 Empresa")
    sector = st.text_input("📍 Sector (ej: Km 170)")
    zona = st.number_input("🚧 Zona permitida (km/h)", min_value=0, max_value=200)
    velocidad = st.number_input("💨 Velocidad registrada (km/h)", min_value=0, max_value=300)
    patente = st.text_input("🚗 Dominio del vehículo")
    observaciones = st.text_area("📝 Observaciones adicionales (opcional)")
    enviar = st.form_submit_button("✅ Generar PDF")

# ---- Generar PDF profesional ----
if enviar:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    # Encabezado fijo
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Señores", ln=True)
    pdf.cell(0, 10, "Seguridad Patrimonial", ln=True)
    pdf.cell(0, 10, "Proyecto Vicuña", ln=True)
    pdf.cell(0, 10, "S_/_D", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Para informar, exceso de velocidad:", ln=True)
    pdf.ln(5)

    # ---- Cuadro tipo tabla ----
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 12)
    def add_row(label, value):
        pdf.set_font("Arial", "B", 11)
        pdf.cell(60, 10, label, border=1, fill=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, str(value), border=1, ln=True)

    add_row("Hora del registro", f"{hora}Hs")
    add_row("Chofer", f"{chofer} (DNI: {dni})")
    add_row("Empresa", empresa)
    add_row("Sector", sector)
    add_row("Zona permitida", f"{zona} km/h")
    add_row("Velocidad registrada", f"{velocidad} km/h")
    add_row("Dominio del vehículo", patente)

    if observaciones.strip() != "":
        add_row("Observaciones adicionales", observaciones)

    pdf.ln(5)
    # Se remite y registro fotográfico
    pdf.multi_cell(0, 10, "Se remite a Staff de Seguridad Patrimonial.\nSe adjunta registro fotográfico.")

    # Guardar PDF
    pdf_file = "Reporte_Exceso_Vicuña.pdf"
    pdf.output(pdf_file)

    with open(pdf_file, "rb") as f:
        st.download_button("📥 Descargar Reporte PDF", f, file_name=pdf_file, mime="application/pdf")

    st.success("✅ Reporte generado correctamente")
