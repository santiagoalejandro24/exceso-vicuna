import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile
import os

st.set_page_config(page_title="Reporte Exceso Vicuña", layout="centered")
st.title("Control de Exceso de Velocidad - Proyecto Vicuña")

# ---- Contenedor del formulario ----
with st.container():
    with st.form("formulario_reporte"):
        st.markdown("### Complete los datos del registro")
        hora = st.text_input("Hora del registro (ej: 09:52)")
        chofer = st.text_input("Chofer (Nombre y Apellido)")
        dni = st.text_input("DNI del chofer")
        empresa = st.text_input("Empresa")
        sector = st.text_input("Sector (ej: Km 170, La Majadita, etc.)")
        zona = st.number_input("Zona de velocidad permitida (km/h)", min_value=0, max_value=200)
        exceso = st.number_input("Exceso de velocidad registrado (km/h)", min_value=0, max_value=300)
        patente = st.text_input("Dominio del vehículo")
        observaciones = st.text_area("Observaciones adicionales (opcional)")

        st.markdown("### Firma del guardia (subir imagen .png o .jpg)")
        firma = st.file_uploader("Subir imagen de firma", type=["png", "jpg", "jpeg"])

        fotos = st.file_uploader(
            "Adjunte archivo(s) fotográfico(s) (máx. 30 MB cada uno)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )

        enviar = st.form_submit_button("Generar PDF")

# ---- Vista previa de fotos y firma ----
if fotos:
    st.markdown("### Fotos subidas")
    for foto in fotos:
        st.image(foto, width=200)

if firma:
    st.markdown("### Firma subida")
    st.image(firma, width=200)

# ---- Generar PDF con indicador visual ----
if enviar:
    campos_obligatorios = [hora, chofer, dni, empresa, sector, patente]
    if any(campo.strip() == "" for campo in campos_obligatorios):
        st.warning("Por favor, complete todos los campos obligatorios.")
    else:
        with st.spinner("Generando PDF, por favor espere..."):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            # --- Encabezado corporativo ---
            pdf.set_font("Arial", "B", 28)
            pdf.set_text_color(0, 128, 0)
            pdf.cell(0, 12, "HUARPE SEGURIDAD", ln=True, align="C")
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "SEGURIDAD INTEGRAL", ln=True, align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 8, "Patrulla Huarpe", ln=True, align="C")
            pdf.ln(10)

            # --- Informe ---
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 6, "Señores", ln=True)
            pdf.cell(0, 6, "Seguridad Patrimonial", ln=True)
            pdf.cell(0, 6, "Proyecto Vicuña", ln=True)
            pdf.cell(0, 6, "S_/_D", ln=True)
            pdf.ln(5)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, f"""Para informar, exceso de velocidad:
Hora del registro {hora}Hs
Chofer {chofer} (DNI: {dni})
Empresa {empresa}
Sector {sector}
Zona de velocidad {zona} km/h
Exceso de velocidad {exceso} km/h
Dominio del vehículo {patente}

Se remite a Staff de Seguridad Patrimonial.
Se adjunta registro fotográfico.""")

            pdf.ln(5)

            # --- Fotos en 2 columnas ---
            if fotos:
                col_width = (pdf.w - 30) / 2
                max_height_in_row = 0
                for i, foto in enumerate(fotos):
                    image = Image.open(foto)
                    dpi = 96
                    width_mm = min(image.width * 25.4 / dpi, col_width)
                    height_mm = width_mm * image.height / image.width
                    max_height_in_row = max(max_height_in_row, height_mm)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        image.save(tmp.name, format="PNG")
                        x_pos = 15 if i % 2 == 0 else 15 + col_width
                        y_pos = pdf.get_y()
                        pdf.image(tmp.name, x=x_pos, y=y_pos, w=width_mm, h=height_mm)
                        os.unlink(tmp.name)

                        if i % 2 == 1:
                            pdf.ln(max_height_in_row + 5)
                            max_height_in_row = 0

                if len(fotos) % 2 == 1:
                    pdf.ln(max_height_in_row + 5)

            # --- Firma al final derecha ---
            if firma:
                pdf.ln(10)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 6, "Firma del guardia:", ln=True)
                img = Image.open(firma)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_sig:
                    img.save(tmp_sig.name, format="PNG")
                    x_start = pdf.w - 15 - 60
                    y_start = pdf.get_y()
                    pdf.rect(x_start - 2, y_start - 2, 60 + 4, 30 + 4)
                    pdf.image(tmp_sig.name, x=x_start, y=y_start, w=60, h=30)
                    pdf.ln(40)
                    os.unlink(tmp_sig.name)

            # --- Descargar PDF ---
            pdf_file = "Reporte_Exceso-Vicuna_Firma.pdf"
            pdf.output(pdf_file)
            with open(pdf_file, "rb") as f:
                st.download_button("Descargar Reporte PDF", f, file_name=pdf_file, mime="application/pdf")

        st.success("Reporte generado correctamente")
