import streamlit as st
from fpdf import FPDF
from datetime import datetime
import base64

st.set_page_config(page_title="Registro Excesos - Proyecto Vicuña", layout="centered")

st.title("🚨 Registro de Exceso de Velocidad - Proyecto Vicuña")

with st.form("exceso_form"):
    hora = st.time_input("Hora del incidente", value=datetime.now().time())
    chofer = st.text_input("Nombre del chofer")
    dni = st.text_input("DNI")
    empresa = st.text_input("Empresa")
    sector = st.text_input("Sector")
    limite = st.number_input("Límite de velocidad (km/h)", min_value=0)
    velocidad = st.number_input("Velocidad registrada (km/h)", min_value=0)
    dominio = st.text_input("Dominio del vehículo")
    foto = st.file_uploader("Registro fotográfico", type=["jpg", "jpeg", "png"])
    
    submit = st.form_submit_button("Generar PDF")

if submit:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Encabezado
    pdf.multi_cell(0, 10, "Señores\nSeguridad Patrimonial\nProyecto Vicuña\nS_/_D")

    # Texto principal
    texto = f"""
Para informar, exceso de velocidad:

* Siendo las {hora.strftime('%H:%M')}Hs
- Chofer Sr. {chofer} (DNI: {dni}).
- Empresa {empresa} para Proyecto Vicuña.
- Sector {sector}.
- Zona de {limite} km/h.
- Exceso de velocidad de {velocidad} km/h.
- Camioneta dominio: {dominio}.

Se remite a Staff de Seguridad Patrimonial.
"""
    pdf.multi_cell(0, 10, texto)

    # Agregar foto si existe
    if foto:
        with open("temp.jpg", "wb") as f:
            f.write(foto.getbuffer())
        pdf.image("temp.jpg", x=10, y=120, w=100)

    # Guardar PDF en memoria
    file_name = f"Exceso_{dominio}.pdf"
    pdf.output(file_name)

    # Descargar PDF
    with open(file_name, "rb") as f:
        pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">📥 Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

    # Link WhatsApp
    mensaje = f"""Exceso de velocidad:
Chofer: {chofer} ({dni})
Empresa: {empresa}
Sector: {sector}
Velocidad: {velocidad} km/h (Zona {limite})
Dominio: {dominio}
"""
    url = f"https://wa.me/?text={mensaje.replace(' ', '%20')}"
    st.markdown(f"[📲 Enviar por WhatsApp]({url})")
