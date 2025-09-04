import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile
import os
import datetime

# ---- Configuración página ----
st.set_page_config(page_title="Reporte Exceso Vicuña", layout="centered")

# ---- Función para generar PDF ----
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Reporte de Exceso de Velocidad - Proyecto Vicuña", ln=True, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generar_pdf(datos, fotos, firma):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    # ---- Datos del reporte ----
    for campo, valor in datos.items():
        pdf.cell(0, 10, f"{campo.capitalize()}: {valor}", ln=True)

    pdf.ln(5)

    # ---- Fotos ----
    if fotos:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Registro Fotográfico:", ln=True)
        for foto in fotos:
            img = Image.open(foto)
            max_ancho = 66  # 10% más grande que antes
            max_alto = 88
            img.thumbnail((max_ancho, max_alto))
            temp_path = tempfile.mktemp(suffix=".png")
            img.save(temp_path)
            pdf.image(temp_path, w=max_ancho, h=max_alto)
            os.remove(temp_path)
            pdf.ln(5)

    # ---- Firma ----
    if firma:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Firma del Responsable:", ln=True)
        img = Image.open(firma)
        img.thumbnail((80, 40))
        temp_path = tempfile.mktemp(suffix=".png")
        img.save(temp_path)
        pdf.image(temp_path, w=80, h=40)
        os.remove(temp_path)

    return pdf

# ---- Validación de datos ----
def validar_datos(hora, dni, zona, exceso, patente):
    if not hora or not dni or not zona or not exceso or not patente:
        return False, "⚠️ Todos los campos obligatorios deben estar completos."
    return True, ""

# ---- Formulario ----
with st.form("form_reporte"):
    st.subheader("Formulario de Reporte de Exceso de Velocidad")

    hora = st.text_input("Hora del incidente *")
    chofer = st.text_input("Nombre del Chofer")
    dni = st.text_input("DNI del Chofer *")
    empresa = st.text_input("Empresa")
    sector = st.text_input("Sector")
    zona = st.text_input("Zona *")
    exceso = st.text_input("Exceso de Velocidad *")
    patente = st.text_input("Patente *")
    guardia = st.text_input("Nombre del Guardia que registró el exceso *")
    observaciones = st.text_area("Observaciones")

    fotos = st.file_uploader("Subir Registro Fotográfico", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    firma = st.file_uploader("Subir Firma", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("Generar PDF")

    if submitted:
        valido, error = validar_datos(hora, dni, zona, exceso, patente)
        if not valido:
            st.error(error)
        else:
            datos_formulario = {
                "Hora": hora,
                "Chofer": chofer,
                "DNI": dni,
                "Empresa": empresa,
                "Sector": sector,
                "Zona": zona,
                "Exceso": exceso,
                "Patente": patente,
                "Guardia": guardia,
                "Observaciones": observaciones
            }
            pdf = generar_pdf(datos_formulario, fotos, firma)
            pdf_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pdf.output(pdf_output.name)

            # Guardamos el PDF en la sesión para poder descargarlo fuera del form
            st.session_state["pdf_generado"] = pdf_output.name
            st.success("✅ El PDF fue generado correctamente. Descárguelo abajo.")

# ---- Botón de descarga (fuera del form) ----
if "pdf_generado" in st.session_state:
    with open(st.session_state["pdf_generado"], "rb") as f:
        st.download_button(
            "📥 Descargar Reporte PDF",
            f,
            file_name=f"Reporte_Exceso_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
