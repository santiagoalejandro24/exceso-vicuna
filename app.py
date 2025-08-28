import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile
import os
import datetime

# --- Configuración de página ---
st.set_page_config(page_title="Reporte Exceso Vicuña", layout="centered")

# --- Estilos ---
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: #FAFAFA;
    font-family: Arial, sans-serif;
}
</style>
""", unsafe_allow_html=True)

# --- Título ---
st.title("📋 Reporte Exceso Vicuña")

# --- Formulario ---
with st.form("reporte_form"):
    fecha = st.date_input("Fecha", value=datetime.date.today())
    hora = st.time_input("Hora", value=datetime.datetime.now().time())
    lugar = st.text_input("Lugar del suceso")
    descripcion = st.text_area("Descripción del suceso")
    responsable = st.text_input("Responsable")
    firma = st.file_uploader("Firma digital (imagen)", type=["png", "jpg", "jpeg"])
    uploaded_images = st.file_uploader("Subir imágenes de evidencia", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    submitted = st.form_submit_button("Generar PDF")

# --- Generar PDF ---
if submitted:
    pdf = FPDF()
    pdf.add_page()

    # Encabezado
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte de Exceso - Proyecto Vicuña", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"📅 Fecha: {fecha}", ln=True)
    pdf.cell(0, 10, f"⏰ Hora: {hora}", ln=True)
    pdf.cell(0, 10, f"📍 Lugar: {lugar}", ln=True)
    pdf.cell(0, 10, f"👤 Responsable: {responsable}", ln=True)

    pdf.ln(5)
    pdf.multi_cell(0, 10, f"📝 Descripción: {descripcion}")

    # --- Imágenes de evidencia ---
    if uploaded_images:
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Evidencias fotográficas:", ln=True)

        max_width = 90   # ancho máximo por imagen
        max_height = 100 # alto máximo
        margin_x = 10
        x_left = margin_x
        x_right = margin_x + max_width + 10
        y_position = pdf.get_y() + 10

        img_count = 0

        for img in uploaded_images:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                tmpfile.write(img.read())
                tmpfile_path = tmpfile.name

            pil_img = Image.open(tmpfile_path)
            width, height = pil_img.size

            # Escalado proporcional
            ratio = min(max_width / width, max_height / height)
            w = int(width * ratio)
            h = int(height * ratio)

            # Columna izquierda o derecha
            x = x_left if img_count % 2 == 0 else x_right

            pdf.image(tmpfile_path, x=x, y=y_position, w=w, h=h)

            # Si es segunda de la fila → bajar
            if img_count % 2 == 1:
                y_position += max_height + 10

            img_count += 1
            os.unlink(tmpfile_path)

        # Si quedó una sola en fila
        if img_count % 2 == 1:
            y_position += max_height + 10

        pdf.ln(10)

    # --- Firma digital ---
    if firma:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            tmpfile.write(firma.read())
            firma_path = tmpfile.name

        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Firma del Responsable:", ln=True)

        pdf.image(firma_path, x=10, y=pdf.get_y()+5, w=50)
        os.unlink(firma_path)

    # Guardar PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
        pdf_path = tmpfile.name

    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ Descargar PDF", f, file_name="Reporte_Exceso_Vicuña.pdf")
