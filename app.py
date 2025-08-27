import streamlit as st
from fpdf import FPDF
import datetime

# Configuración de la página
st.set_page_config(page_title="Control Exceso Vicuña", layout="centered")

st.title("📋 Formulario de Control - Proyecto Vicuña")
st.write("Complete el siguiente formulario para generar el reporte en PDF.")

# Formulario
with st.form("formulario"):
    nombre = st.text_input("👤 Nombre del responsable")
    empresa = st.text_input("🏢 Empresa")
    patente = st.text_input("🚗 Patente del vehículo")
    fecha = st.date_input("📅 Fecha", value=datetime.date.today())
    hora = st.time_input("⏰ Hora", value=datetime.datetime.now().time())
    observaciones = st.text_area("📝 Observaciones")
    foto = st.file_uploader("📷 Adjuntar registro fotográfico", type=["jpg", "png", "jpeg"])
    enviar = st.form_submit_button("✅ Generar PDF")

# Generar PDF
if enviar:
    pdf = FPDF()
    pdf.add_page()

    # Encabezado
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Reporte de Control - Proyecto Vicuña", ln=True, align="C")
    pdf.ln(10)

    # Datos
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, f"""
    Nombre responsable: {nombre}
    Empresa: {empresa}
    Patente vehículo: {patente}
    Fecha: {fecha}
    Hora: {hora}
    Observaciones: {observaciones}
    
    ANTIESTALLIDO: SI
    OXIGENO: SI
    COMBUSTIBLE: SI
    RADIO: S/N
    """)
    pdf.ln(5)

    # Guardar archivo
    pdf_file = "Reporte_Vicuña.pdf"
    pdf.output(pdf_file)

    # Mostrar link de descarga
    with open(pdf_file, "rb") as f:
        st.download_button("📥 Descargar PDF", f, file_name=pdf_file, mime="application/pdf")
