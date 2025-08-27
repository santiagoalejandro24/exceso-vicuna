# app.py (VERSIÓN CORREGIDA)
import streamlit as st
from fpdf import FPDF
from datetime import datetime
import base64
from PIL import Image
import os
import urllib.parse

st.set_page_config(page_title="Proyecto Vicuña - Registro de Excesos", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    .card { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
    </style>
""", unsafe_allow_html=True)

st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Warning_icon.svg/240px-Warning_icon.svg.png", width=70)
st.title("🚨 Registro de Exceso de Velocidad")
st.markdown("**Proyecto Vicuña - Seguridad Patrimonial**")
st.markdown("")  # espacio

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
    foto = st.file_uploader("📷 Registro fotográfico (opcional)", type=["jpg", "jpeg", "png"])
    submit = st.form_submit_button("✅ Generar Informe PDF")

if submit:
    # Validación básica
    if not chofer or not dni or not empresa or not dominio:
        st.error("⚠️ Complete los campos obligatorios: nombre del chofer, DNI, empresa y dominio.")
    else:
        # Configurar PDF
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Informe de Exceso de Velocidad - Proyecto Vicuña", ln=True, align="C")
        pdf.ln(6)
        pdf.set_font("Arial", size=12)

        # Encabezado y texto
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

        # Frase antes de la foto
        pdf.multi_cell(0, 7, "Se adjunta registro fotográfico.")
        pdf.ln(3)

        # Manejo de la foto: colocarla *después* del texto y evitar solapamientos
        temp_path = None
        try:
            if foto:
                # Guardar imagen temporal
                temp_path = "temp_exceso.jpg"
                with open(temp_path, "wb") as f:
                    f.write(foto.getbuffer())

                # (Opcional) reducir tamaño muy grande para evitar PDFs enormes
                img = Image.open(temp_path)
                max_pixel_width = 2000
                if img.width > max_pixel_width:
                    ratio = max_pixel_width / img.width
                    new_h = int(img.height * ratio)
                    img = img.resize((max_pixel_width, new_h), Image.LANCZOS)
                    img.save(temp_path)

                # Comprobación simple de salto de página:
                y_pos = pdf.get_y()  # posición actual en mm
                page_height = 297     # A4 en mm
                bottom_margin = 15    # margen inferior en mm
                safety_image_height_estimate = 80  # estimación mm para decidir salto de página
                if y_pos + safety_image_height_estimate > (page_height - bottom_margin):
                    pdf.add_page()

                # Dejar pequeño espacio y agregar imagen usando ancho máximo de página
                pdf.ln(2)
                left_margin = 10
                usable_width = 210 - 2 * left_margin  # 210mm ancho A4
                pdf.image(temp_path, x=left_margin, w=usable_width)
                pdf.ln(5)

            # Guardar PDF y ofrecer descarga
            file_name = f"Exceso_{dominio.replace(' ', '_')}.pdf"
            pdf.output(file_name)

            with open(file_name, "rb") as f:
                pdf_bytes = f.read()
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a style="background:#1a3d7c;color:white;padding:10px 18px;border-radius:8px;text-decoration:none;" href="data:application/octet-stream;base64,{b64}" download="{file_name}">📥 Descargar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

            # Enlace WhatsApp (mensaje codificado)
            mensaje = f"Exceso de velocidad:%0AChofer: {chofer} ({dni})%0AEmpresa: {empresa}%0ASector: {sector}%0AVelocidad: {velocidad} km/h (Zona {limite})%0ADominio: {dominio}"
            wa_url = f"https://wa.me/?text={urllib.parse.quote(mensaje)}"
            st.markdown(f"[📲 Enviar por WhatsApp]({wa_url})")
            st.success("✅ Informe generado con éxito.")
        finally:
            # Limpieza: eliminar temporales
            try:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass
