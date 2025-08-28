import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile
import os

st.set_page_config(page_title="Reporte Exceso Vicuña", layout="centered")
st.title("Reporte de Exceso de Velocidad - Proyecto Vicuña")

# ---- Formulario ----
with st.form("formulario_reporte"):
    st.subheader("Datos del Suceso")
    hora = st.text_input("Hora del registro (ej: 12:30)")
    chofer = st.text_input("Chofer (Nombre y Apellido)")
    dni = st.text_input("DNI del chofer")
    empresa = st.text_input("Empresa")
    sector = st.text_input("Sector donde se hizo el suceso")
    zona_vel = st.number_input("Zona de velocidad permitida (km/h)", min_value=0, max_value=200)
    exceso_vel = st.number_input("Exceso de velocidad registrado (km/h)", min_value=0, max_value=300)
    dominio = st.text_input("Dominio del vehículo")

    st.subheader("Evidencia fotográfica")
    fotos = st.file_uploader(
        "Subir imágenes (png, jpg, jpeg) - max 2 por fila",
        type=["png","jpg","jpeg"],
        accept_multiple_files=True
    )

    st.subheader("Firma del Guardia")
    firma_guardia = st.file_uploader(
        "Subir imagen de la firma del guardia (png, jpg, jpeg)",
        type=["png","jpg","jpeg"]
    )
    nombre_guardia = st.text_input("Nombre del Guardia")
    dni_guardia = st.text_input("DNI del Guardia")

    enviar = st.form_submit_button("Generar PDF")

# ---- Generar PDF ----
if enviar:
    pdf = FPDF()
    pdf.add_page()

    # --- Encabezado corporativo ---
    pdf.set_font("Arial", "B", 28)
    pdf.set_text_color(0, 128, 0)   # Verde
    pdf.cell(0, 12, "HUARPE SEGURIDAD", ln=True, align="C")

    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "SEGURIDAD INTEGRAL", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, "Patrulla Huarpe", ln=True, align="C")
    pdf.ln(10)

    # --- Sección oficial de texto ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Señores", ln=True)
    pdf.cell(0, 10, "Seguridad Patrimonial", ln=True)
    pdf.cell(0, 10, "Proyecto Vicuña", ln=True)
    pdf.cell(0, 10, "S_/_D", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, f"""Para informar, exceso de velocidad:
Hora del registro {hora}Hs
Chofer {chofer} (DNI: {dni})
Empresa {empresa}
Sector {sector}
Zona de velocidad {zona_vel} km/h
Exceso de velocidad {exceso_vel} km/h
Dominio del vehículo {dominio}

Se remite a Staff de Seguridad Patrimonial.
Se adjunta registro fotográfico.""")
    pdf.ln(5)

    # --- Fotos ---
    if fotos:
        max_width = 90
        max_height = 100
        x_left = 10
        x_right = 10 + max_width + 10
        y_position = pdf.get_y() + 5
        img_count = 0

        for foto in fotos:
            image = Image.open(foto)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                image.save(tmpfile.name, format="PNG")
                tmpfile_path = tmpfile.name

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

    # --- Firma al final derecha ---
    if firma_guardia:
        pdf.set_y(-60)
        x_pos = pdf.w - 70
        y_pos = pdf.get_y()

        pdf.set_draw_color(100,100,100)
        pdf.set_line_width(0.6)
        pdf.rect(x=x_pos, y=y_pos, w=60, h=40)

        image = Image.open(firma_guardia)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            image.save(tmpfile.name, format="PNG")
            tmpfile_path = tmpfile.name

        pdf.image(tmpfile_path, x=x_pos + 2, y=y_pos + 2, w=56)
        os.unlink(tmpfile_path)

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
