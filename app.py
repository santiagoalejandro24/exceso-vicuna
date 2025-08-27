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

# ---- LÓGICA DEL PDF ----
if submit:
    if not chofer or not dni or not empresa or not dominio:
        st.error("⚠️ Complete los campos obligatorios: nombre del chofer, DNI, empresa y dominio.")
    else:
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Informe de Exceso de Velocidad - Proyecto Vicuña", ln=True, align="C")
        pdf.ln(6)
        pdf.set_font("Arial", size=12)

        pdf.multi_cell(0, 7, "Señores\nSeguridad Patrimonial\nProyecto Vicuña\nS_/_D\n")
        pdf.ln(2)

        texto = f"""Para informar, exceso de velocidad:

* Siendo las {hora.strftime('%H:%M')}Hs
- Chofer Sr. {chofer} (DNI: {dni}).
- Empresa {empresa} para Proyecto Vicuña.
- Sector {sector}.
- Zona de {limite} km/h.
- Exceso de velocidad de {velocidad} km/h.
- Camioneta dominio: {dominio}.

Se remite a Staff de Seguridad Patrimonial.
"""
        pdf.multi_cell(0, 7, texto)
        pdf.ln(3)
        pdf.multi_cell(0, 7, "Se adjunta registro fotográfico.")
        pdf.ln(3)

        temp_path = None
        try:
            if foto:
                temp_path = "temp_exceso.jpg"
                with open(temp_path, "wb") as f:
                    f.write(foto.getbuffer())

                img = Image.open(temp_path)
                max_pixel_width = 2000
                if img.width > max_pixel_width:
                    ratio = max_pixel_width / img.width
                    new_h = int(img.height * ratio)
                    img = img.resize((max_pixel_width, new_h), Image.LANCZOS)
                    img.save(temp_path)

                y_pos = pdf.get_y()
                page_height = 297
                bottom_margin = 15
                safety_image_height_estimate = 60
                if y_pos + safety_image_height_estimate > (page_height - bottom_margin):
                    pdf.add_page()

                pdf.ln(2)
                left_margin = 10
                usable_width = 210 - 2 * left_margin
                pdf.image(temp_path, x=left_margin, w=usable_width)
                pdf.ln(5)

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
            except Exception:
                pass

# ---- FOOTER ----
st.markdown("---")
st.markdown("<center>📌 Proyecto Vicuña | Seguridad Patrimonial © 2025</center>", unsafe_allow_html=True)
