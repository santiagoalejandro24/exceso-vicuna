import streamlit as st
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import tempfile
import os
import datetime

st.set_page_config(page_title="Reporte Exceso Vicuña", layout="centered")
st.title("Reporte de Exceso de Velocidad - Proyecto Vicuña")

# ---- Formulario limpio estilo oficial ----
with st.form("formulario_reporte"):
    st.subheader("Datos del registro")

    nombre = st.text_input("Nombre de la persona")
    dni = st.text_input("DNI")
    empresa = st.text_input("Empresa")
    sector = st.text_input("Sector donde se hizo el suceso")
    limite_vel = st.number_input("Límite de velocidad (km/h)", min_value=0, step=1)
    exceso_vel = st.number_input("Exceso de velocidad (km/h)", min_value=0, step=1)
    dominio = st.text_input("Dominio del vehículo")

    st.subheader("Evidencia fotográfica")
    fotos = st.file_uploader(
        "Subir imágenes (png, jpg, jpeg) - max 2 por fila",
        type=["png","jpg","jpeg"],
        accept_multiple_files=True
    )

    st.subheader("Firma del Guardia")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=400,
        drawing_mode="freedraw",
        key="canvas"
    )

    nombre_guardia = st.text_input("Nombre del Guardia")
    dni_guardia = st.text_input("DNI del Guardia")

    enviar = st.form_submit_button("Generar PDF")

# ---- Generar PDF ----
if enviar:
    pdf = FPDF()
    pdf.add_page()

    # --- Encabezado corporativo ---
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(0, 50, 0)
    pdf.cell(0, 15, "HUARPE SEGURIDAD", ln=True, align="C")
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0,0,0)
    pdf.cell(0, 10, "Reporte de Exceso de Velocidad - Proyecto Vicuña", ln=True, align="C")
    pdf.ln(5)

    # --- Datos en cuadros estilo oficial ---
    def add_field(label, value, fill_color=(245,245,245)):
        pdf.set_fill_color(*fill_color)
        pdf.set_draw_color(100,100,100)
        pdf.set_line_width(0.5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(60, 10, label, border=1, fill=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, str(value), border=1, fill=True, ln=True)

    add_field("Nombre de la persona", nombre, fill_color=(240,240,240))
    add_field("DNI", dni)
    add_field("Empresa", empresa, fill_color=(240,240,240))
    add_field("Sector donde se hizo el suceso", sector)
    add_field("Límite de velocidad", f"{limite_vel} km/h", fill_color=(240,240,240))
    add_field("Exceso de velocidad", f"{exceso_vel} km/h")
    add_field("Dominio del vehículo", dominio, fill_color=(240,240,240))
    pdf.ln(5)

    # --- Fotos de evidencia ---
    if fotos:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Evidencias fotográficas:", ln=True)

        max_width = 90
        max_height = 100
        x_left = 10
        x_right = 10 + max_width + 10
        y_position = pdf.get_y() + 5
        img_count = 0

        for foto in fotos:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                tmpfile.write(foto.read())
                tmpfile_path = tmpfile.name

            image = Image.open(tmpfile_path)
            width, height = image.size
            ratio = min(max_width / width, max_height / height)
            w = int(width * ratio)
            h = int(height * ratio)

            x = x_left if img_count % 2 == 0 else x_right
            pdf.image(tmpfile_path, x=x, y=y_position, w=w, h=h)

            if img_count % 2 == 1:
                y_position += max_height + 10

            img_count += 1
            os.unlink(tmpfile_path)

        if img_count % 2 == 1:
            y_position += max_height + 10

        pdf.ln(10)

    # --- Firma digital a la derecha ---
    if canvas_result.image_data is not None:
        pdf.set_y(-60)
        x_pos = pdf.w - 70
        y_pos = pdf.get_y()

        pdf.set_draw_color(50,50,50)
        pdf.set_line_width(0.6)
        pdf.rect(x=x_pos, y=y_pos, w=60, h=40)

        img = Image.fromarray((canvas_result.image_data).astype("uint8"))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        pdf.image(buf, x=x_pos + 2, y=y_pos + 2, w=56)

        pdf.set_xy(x_pos, y_pos + 42)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(60, 5, f"{nombre_guardia}\nDNI: {dni_guardia}", align="C")

    # --- Descargar PDF ---
    pdf_output = pdf.output(dest="S").encode("latin-1")
    st.download_button(
        "📄 Descargar PDF",
        data=pdf_output,
        file_name="Reporte_Exceso-Vicuña.pdf",
        mime="application/pdf"
    )
