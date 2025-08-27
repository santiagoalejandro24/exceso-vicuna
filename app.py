import streamlit as st
from fpdf import FPDF
import datetime

# Configuración inicial
st.set_page_config(page_title="Control de Exceso - Proyecto Vicuña", layout="centered")

# Tema oscuro con CSS
st.markdown("""
    <style>
        body {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        h1, h2, h3, h4, h5, h6, label, p {
            color: #FAFAFA !important;
        }
        .css-1d391kg {
            background-color: #1E1E1E !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Control de Exceso - Proyecto Vicuña")

# Formulario
with st.form("control_form"):
    fecha = st.date_input("📅 Fecha", datetime.date.today())
    hora = st.time_input("⏰ Hora")
    empresa = st.text_input("🏢 Empresa")
    sector = st.text_input("📍 Sector")
    conductor = st.text_input("👷 Conductor")
    dni = st.text_input("🪪 DNI")
    patente = st.text_input("🚗 Patente Vehículo")
    observaciones = st.text_area("📝 Observaciones")

    submitted = st.form_submit_button("✅ Generar Reporte")

# Generar PDF profesional
if submitted:
    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Encabezado
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(40, 40, 40)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "CONTROL DE EXCESO - PROYECTO VICUÑA", ln=True, align="C", fill=True)

    pdf.ln(10)

    # Tabla de datos principales
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 0, 0)

    def add_row(label, value):
        pdf.set_font("Arial", "B", 11)
        pdf.cell(50, 10, label, border=1, align="L")
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, str(value), border=1, ln=True, align="L")

    add_row("Fecha", fecha)
    add_row("Hora", hora.strftime("%H:%M"))
    add_row("Empresa", empresa)
    add_row("Sector", sector)
    add_row("Conductor", conductor)
    add_row("DNI", dni)
    add_row("Patente", patente)

    # Observaciones en cuadro aparte
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Observaciones:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 10, observaciones, border=1)

    # Cuadro final fijo
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "Checklist del Vehículo", ln=True, align="C", fill=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, "ANTIESTALLIDO: SI | OXÍGENO: SI | COMBUSTIBLE: SI | RADIO: S/N", ln=True, align="C", border=1)

    # Guardar PDF
    pdf_output = "control_exceso.pdf"
    pdf.output(pdf_output)

    with open(pdf_output, "rb") as f:
        st.download_button("📥 Descargar Reporte en PDF", f, file_name=pdf_output)
