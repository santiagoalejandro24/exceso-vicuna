import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile
import os

# ---- Configuración página ----
st.set_page_config(page_title="Reporte Exceso Vicuña", layout="centered")

# ---- Estilos CSS ----
st.markdown("""
<style>  
body { background-color: #0E1117; color: #FAFAFA; font-family: Arial, sans-serif; }
h1 { text-align: center; color: #F5C518; }
.stButton>button { background-color: #F5C518; color: black; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---- Título ----
st.title("📑 Reporte Exceso Vicuña")

# ---- Formulario ----
with st.form("reporte_form"):
    fecha = st.date_input("📅 Fecha del reporte")
    hora = st.time_input("⏰ Hora del reporte")
    lugar = st.text_input("📍 Lugar del evento")
    descripcion = st.text_area("📝 Descripción del evento")
    uploaded_images = st.file_uploader("📷 Subir imágenes", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    submitted = st.form_submit_button("📌 Generar Reporte")

if submitted:
    # ---- Crear PDF ----
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Reporte de Exceso - Proyecto Vicuña", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"📅 Fecha: {fecha}", ln=True)
    pdf.cell(0, 10, f"⏰ Hora: {hora}", ln=True)
    pdf.cell(0, 10, f"📍 Lugar: {lugar}", ln=True)
    pdf.multi_cell(0, 10, f"📝 Descripción:\n{descripcion}")
    pdf.ln(10)

    # ---- Insertar imágenes en el PDF ----
    if uploaded_images:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "📷 Imágenes adjuntas:", ln=True)

        i = 0
        while i < len(uploaded_images):
            img = uploaded_images[i]
            image = Image.open(img)
            w, h = image.size

            # Detectar si hay dos imágenes verticales seguidas
            if i + 1 < len(uploaded_images):
                next_img = Image.open(uploaded_images[i+1])
                w2, h2 = next_img.size

                if h > w and h2 > w2:  # ambas son verticales
                    # Guardar temporalmente ambas
                    img_path1 = tempfile.mktemp(suffix=".png")
                    image.save(img_path1)
                    img_path2 = tempfile.mktemp(suffix=".png")
                    next_img.save(img_path2)

                    # Ajustar a mitad de la página cada una
                    max_width = (pdf.w - 40) / 2
                    new_h = int(h * (max_width / w))
                    new_h2 = int(h2 * (max_width / w2))

                    y_before = pdf.get_y()
                    pdf.image(img_path1, x=10, y=y_before, w=max_width)
                    pdf.image(img_path2, x=pdf.w/2 + 5, y=y_before, w=max_width)

                    pdf.ln(max(new_h, new_h2) + 10)
                    i += 2
                    continue

            # Si no hay par, insertar normal
            img_path = tempfile.mktemp(suffix=".png")
            image.save(img_path)

            max_width = pdf.w - 40
            if w > h:  # horizontal
                new_h = int(h * (max_width / w))
                pdf.image(img_path, x=10, y=pdf.get_y(), w=max_width)
                pdf.ln(new_h + 10)
            else:  # vertical sola
                max_height = 120
                new_w = int(w * (max_height / h))
                pdf.image(img_path, x=(pdf.w - new_w) / 2, y=pdf.get_y(), h=max_height)
                pdf.ln(max_height + 10)

            i += 1

    # ---- Guardar PDF ----
    temp_pdf = tempfile.mktemp(suffix=".pdf")
    pdf.output(temp_pdf)

    with open(temp_pdf, "rb") as file:
        st.download_button("⬇️ Descargar Reporte PDF", file, file_name="Reporte_Exceso_Vicuña.pdf")
