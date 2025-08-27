import streamlit as st
from fpdf import FPDF
from datetime import datetime
from PIL import Image
import os
import tempfile
import base64
import urllib.parse

# ---- CONFIGURACIÓN DE PÁGINA ----
st.set_page_config(page_title="Proyecto Vicuña - Registro de Excesos", layout="wide", page_icon="🚨")

# ---- ESTILO CSS FONDO OSCURO ----
st.markdown("""
<style>
.stApp { background-color: #1a1a2e; font-family: 'Arial', sans-serif; }
.card { background-color: #f4f6f9; padding: 30px; border-radius: 15px; box-shadow: 0 6px 18px rgba(0,0,0,0.4); }
h1, h2, h3 { color: #e0e0e0; }
.stMarkdown, .stText { color: #ffffff; }
[data-baseweb="input"] input { border: 2px solid #1a3d7c !important; border-radius: 6px !important; color: #000000 !important; background-color: #ffffff !important; }
a.download-btn, a.wa-btn { background-color: #1a3d7c; color: white !important; padding: 10px 22px; border-radius: 8px; text-decoration: none; font-weight: bold; transition: background-color 0.3s; }
a.download-btn:hover, a.wa-btn:hover { background-color: #163261; }
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("<h1>Registro de Exceso de Velocidad</h1>", unsafe_allow_html=True)
st.markdown("**Proyecto Vicuña - Seguridad Patrimonial**", unsafe_allow_html=True)
st.markdown("")

# ---- FORMULARIO ----
with st.form("exceso_form"):
    col1, col2 = st.columns(2)
    with col1:
        hora = st.time_input("Hora del incidente", value=datetime.now().time())
        chofer = st.text_input("Nombre del chofer")
        dni = st.text_input("DNI")
        empresa = st.text_input("Empresa")
    with col2:
        sector = st.text_input("Sector")
        limite = st.number_input("Límite velocidad (km/h)", min_value=0)
        velocidad = st.number_input("Velocidad registrada (km/h)", min_value=0)
        dominio = st.text_input("Dominio del vehículo")
    foto = st.file_uploader("📷 Registro fotográfico (opcional)", type=["jpg","jpeg","png"])
    submit = st.form_submit_button("✅ Generar Informe PDF")

# ---- PDF PROFESIONAL ----
if submit:
    if not chofer or not dni or not empresa or not dominio:
        st.error("⚠️ Complete los campos obligatorios: nombre del chofer, DNI, empresa y dominio.")
    else:
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Título centrado
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Informe de Exceso de Velocidad", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 6, "Proyecto Vicuña - Seguridad Patrimonial", ln=True, align="C")
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        # Tabla de datos
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50,6,"Campo",1,0,"C")
        pdf.cell(0,6,"Detalle",1,1,"C")
        pdf.set_font("Arial","",12)
        datos = [
            ("Hora del incidente", hora.strftime("%H:%M")),
            ("Chofer", chofer),
            ("DNI", dni),
            ("Empresa", empresa),
            ("Sector", sector),
            ("Zona límite (km/h)", str(limite)),
            ("Velocidad registrada (km/h)", str(velocidad)),
            ("Dominio vehículo", dominio)
        ]
        for campo, valor in datos:
            pdf.cell(50,6,campo,1,0)
            pdf.cell(0,6,valor,1,1)

        pdf.ln(5)
        pdf.multi_cell(0,6,"Se adjunta registro fotográfico.",0,1)
        pdf.ln(2)

        # Foto centrada
        temp_path = None
        try:
            if foto:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(foto.getbuffer())
                    temp_path = tmp.name
                img = Image.open(temp_path)
                max_width = 1600
                if img.width > max_width:
                    ratio = max_width / img.width
                    img = img.resize((max_width, int(img.height*ratio)), Image.LANCZOS)
                    img.save(temp_path)
                pdf.image(temp_path, x=(210-180)/2, w=180)
                pdf.ln(5)

            # Pie de página
            pdf.set_y(-25)
            pdf.set_font("Arial", "I", 10)
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            pdf.cell(0,5,f"Proyecto Vicuña | Seguridad Patrimonial | Generado: {fecha}",0,1,"C")

            # Guardar PDF en temp
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                pdf.output(tmp_pdf.name)
                tmp_pdf_path = tmp_pdf.name

            with open(tmp_pdf_path, "rb") as f:
                pdf_bytes = f.read()
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a class="download-btn" href="data:application/octet-stream;base64,{b64}" download="Exceso_{dominio.replace(" ","_")}.pdf">📥 Descargar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

            mensaje = f"Exceso de velocidad:\nChofer: {chofer} ({dni})\nEmpresa: {empresa}\nSector: {sector}\nVelocidad: {velocidad} km/h (Zona {limite})\nDominio: {dominio}"
            wa_url = f"https://wa.me/?text={urllib.parse.quote(mensaje)}"
            st.markdown(f'<a class="wa-btn" href="{wa_url}">📲 Enviar por WhatsApp</a>', unsafe_allow_html=True)

            st.success("✅ Informe generado con éxito.")

        finally:
            try:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                if tmp_pdf_path and os.path.exists(tmp_pdf_path):
                    os.remove(tmp_pdf_path)
            except:
                pass

# ---- FOOTER ----
st.markdown("---")
st.markdown("<center>📌 Proyecto Vicuña | Seguridad Patrimonial © 2025</center>", unsafe_allow_html=True)
