import streamlit as st
from fpdf import FPDF
from datetime import datetime
import base64
from PIL import Image
import os
import urllib.parse

# ---- CONFIGURACIÓN DE PÁGINA ----
st.set_page_config(page_title="Proyecto Vicuña - Registro de Excesos", layout="wide", page_icon="🚨")

# ---- ESTILO CSS FONDO OSCURO ----
st.markdown("""
<style>
/* Fondo oscuro de la página */
.stApp {
    background-color: #1a1a2e;
    font-family: 'Arial', sans-serif;
}

/* Caja del formulario clara para resaltar */
.card {
    background-color: #f4f6f9;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.4);
}

/* Encabezados claros */
h1, h2, h3 {
    color: #e0e0e0;
}

/* Texto general */
.stMarkdown, .stText {
    color: #ffffff;
}

/* Estilo campos del formulario */
[data-baseweb="input"] input {
    border: 2px solid #1a3d7c !important;
    border-radius: 6px !important;
    color: #000000 !important;
    background-color: #ffffff !important;
}

/* Botones estilo corporativo claros */
a.download-btn, a.wa-btn {
    background-color: #1a3d7c;
    color: white !important;
    padding: 10px 22px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    transition: background-color 0.3s;
}
a.download-btn:hover, a.wa-btn:hover {
    background-color: #163261;
}

/* Footer */
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---- HEADER CON LOGO ----
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Warning_icon.svg/240px-Warning_icon.svg.png", width=70)
with col_title:
    st.markdown("<h1>Registro de Exceso de Velocidad</h1>", unsafe_allow_html=True)
    st.markdown("**Proyecto Vicuña - Seguridad Patrimonial**", unsafe_allow_html=True)

st.markdown("")  # espacio

# ---- FORMULARIO ----
with st.form("exceso_form"):
    with st.container():
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
        foto = st.file_uploader("📷 Registro fotográfico (opcional)", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("✅ Generar Informe PDF")

# ---- LÓGICA DEL PDF PROFESIONAL ----
if submit:
    if not chofer or not dni or not empresa or not dominio:
        st.error("⚠️ Complete los campos obligatorios: nombre del chofer, DNI, empresa y dominio.")
    else:
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # ---- ENCABEZADO LOGO + TÍTULO ----
        logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Warning_icon.svg/240px-Warning_icon.svg.png"
        logo_path = "logo_temp.png"
        if foto:
            # solo para usar el mismo directorio
            pass
        import requests
        r = requests.get(logo_url)
        with open(logo_path, "wb") as f:
            f.write(r.content)
        pdf.image(logo_path, x=10, y=8, w=25)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Informe de Exceso de Velocidad", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 6, "Proyecto Vicuña - Seguridad Patrimonial", ln=True, align="C")
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        # ---- TABLA DE DATOS ----
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 6, "Campo", 1, 0, "C")
        pdf.cell(0, 6, "Detalle", 1, 1, "C")

        pdf.set_font("Arial", "", 12)
        data = [
            ("Hora del incidente", hora.strftime('%H:%M')),
            ("Chofer", chofer),
            ("DNI", dni),
            ("Empresa", empresa),
            ("Sector", sector),
            ("Zona límite (km/h)", str(limite)),
            ("Velocidad registrada (km/h)", str(velocidad)),
            ("Dominio vehículo", dominio)
        ]
        for field, value in data:
            pdf.cell(50, 6, field, 1, 0)
            pdf.cell(0, 6, value, 1, 1)

        pdf.ln(5)
        pdf.multi_cell(0, 6, "Se adjunta registro fotográfico.", 0, 1)
        pdf.ln(2)

        # ---- FOTO CENTRADA ----
        temp_path = None
        try:
            if foto:
                temp_path = "temp_exceso.jpg"
                with open(temp_path, "wb") as f:
                    f.write(foto.getbuffer())

                img = Image.open(temp_path)
                max_pixel_width = 1600
                if img.width > max_pixel_width:
                    ratio = max_pixel_width / img.width
                    new_h = int(img.height * ratio)
                    img = img.resize((max_pixel_width, new_h), Image.LANCZOS)
                    img.save(temp_path)

                # Centrar imagen horizontalmente
                pdf_w = 210
                img_w_mm = 180
                pdf.image(temp_path, x=(pdf_w - img_w_mm)/2, w=img_w_mm)
                pdf.ln(5)

            # ---- PIE DE PÁGINA ----
            pdf.set_y(-25)
            pdf.set_font("Arial", "I", 10)
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            pdf.cell(0, 5, f"Proyecto Vicuña | Seguridad Patrimonial | Generado: {fecha}", 0, 1, "C")

            # ---- GUARDAR PDF ----
            file_name = f"Exceso_{dominio.replace(' ', '_')}.pdf"
            pdf.output(file_name)

            with open(file_name, "rb") as f:
                pdf_bytes = f.read()
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a class="download-btn" href="data:application/octet-stream;base64,{b64}" download="{file_name}">📥 Descargar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

            mensaje = f"Exceso de velocidad:\nChofer: {chofer} ({dni})\nEmpresa: {empresa}\nSector: {sector}\nVelocidad: {velocidad} km/h (Zona {limite})\nDominio: {dominio}"
            wa_url = f"https://wa.me/?text={urllib.parse.quote(mensaje)}"
            st.markdown(f'<a class="wa-btn" href="{wa_url}">📲 Enviar por WhatsApp</a>', unsafe_allow_html=True)
            st.success("✅ Informe generado con éxito.")

        finally:
            try:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(logo_path):
                    os.remove(logo_path)
            except Exception:
                pass

# ---- FOOTER ----
st.markdown("---")
st.markdown("<center>📌 Proyecto Vicuña | Seguridad Patrimonial © 2025</center>", unsafe_allow_html=True)
