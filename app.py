import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile
import os
import datetime
import re

# ---- Configuración página ----
st.set_page_config(page_title="Reporte Exceso Vicuña", layout="centered")

# ---- Estilos CSS ----
st.markdown("""
<style>  
body { background-color: #0E1117; color: #FAFAFA; font-family: Arial, sans-serif }  
.stTextInput > div > div > input, .stTextArea textarea { background-color: #1E1E1E; color: white; border-radius: 8px; padding: 10px; }  
.stFileUploader label { color: #D4D4D4; }  
.stButton>button { background-color: #6C63FF; color: white; border-radius: 8px; padding: 10px 24px; }  
</style>
""", unsafe_allow_html=True)

# ---- Función para validar datos ----
def validar_datos(hora, dni, zona, exceso, patente):
    try:
        datetime.datetime.strptime(hora, "%H:%M")
    except ValueError:
        return False, "Formato de hora inválido. Use HH:MM."
    if not dni.isdigit() or len(dni) not in [7, 8]:
        return False, "DNI inválido. Debe tener 7 u 8 dígitos."
    if not zona.replace('.', '', 1).isdigit():
        return False, "Zona debe ser numérica."
    if not exceso.replace('.', '', 1).isdigit():
        return False, "Exceso debe ser numérico."
    if not re.match(r"^[A-Z0-9]{6,8}$", patente.upper()):
        return False, "Patente inválida. Ejemplo válido: ABC123 o AB123CD."
    return True, ""

# ---- Clase PDF personalizada ----
class PDF(FPDF):
    def header(self):
        self.set_fill_color(46, 125, 50)
        self.set_font("Arial", "B", 16)
        self.cell(0, 12, "HUARPE SEGURIDAD INTEGRAL", 0, 1, "C", 1)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "REPORTE DE EXCESO DE VELOCIDAD - PROYECTO VICUÑA", 0, 1, "C")
        self.ln(5)

# ---- Generar PDF ----
def generar_pdf(datos, fotos, firma):
    pdf = PDF()
    pdf.add_page()

    # Fecha automática
    fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Fecha: {fecha_actual}", 0, 1, 'R')
    pdf.ln(2)

    # Datos principales
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Datos del reporte", 0, 1)

    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(230, 230, 230)
    campos = [
        ("Hora", datos['hora']),
        ("Chofer", datos['chofer']),
        ("DNI", datos['dni']),
        ("Empresa", datos['empresa']),
        ("Guardia que realizó el control", datos['guardia']),  # NUEVO CAMPO
        ("Sector", datos['sector']),
        ("Zona", datos['zona']),
        ("Exceso (Km/h)", datos['exceso']),
        ("Patente", datos['patente']),
    ]
    for campo, valor in campos:
        pdf.cell(60, 8, campo, 1, 0, 'L', 1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, valor, 1, 1, 'L')
        pdf.set_font("Arial", "B", 10)

    # Observaciones
    if datos['observaciones']:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 8, "Observaciones", 1, 0, 'L', 1)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 8, datos['observaciones'], 1, 'L')
        pdf.ln(5)

    # Registro fotográfico
    if fotos:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Registro fotográfico", 0, 1)
        pdf.ln(3)

        for foto in fotos:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                img = Image.open(foto)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Aumentar tamaño un 10%
                max_ancho = 66  # antes 60
                max_alto = 88   # antes 80
                img.thumbnail((max_ancho, max_alto))
                img.save(tmpfile.name, "PNG")

                pdf.image(tmpfile.name, w=img.width * 0.25, h=img.height * 0.25)
                pdf.ln(5)
                os.unlink(tmpfile.name)

    # Firma
    if firma:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Firma del chofer", 0, 1)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            img = Image.open(firma)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.thumbnail((100, 40))
            img.save(tmpfile.name, "PNG")
            x = pdf.get_x() + 40
            y = pdf.get_y()
            pdf.rect(x, y, 100, 40)
            pdf.image(tmpfile.name, x=x, y=y, w=100, h=40)
            pdf.ln(50)
            os.unlink(tmpfile.name)

    return pdf

# ---- Formulario en Streamlit ----
st.title("📋 Reporte de Exceso de Velocidad - Proyecto Vicuña")

with st.form("exceso_form"):
    col1, col2 = st.columns(2)
    with col1:
        hora = st.text_input("Hora del registro (ej: 09:52)", key="hora_input")
        chofer = st.text_input("Chofer (Nombre y Apellido)", key="chofer_input")
        dni = st.text_input("DNI del chofer", key="dni_input")
        empresa = st.text_input("Empresa", key="empresa_input")
        guardia = st.text_input("Nombre del guardia que realizó el control", key="guardia_input")  # NUEVO CAMPO
    with col2:
        sector = st.text_input("Sector", key="sector_input")
        zona = st.text_input("Zona (Km/h)", key="zona_input")
        exceso = st.text_input("Exceso (Km/h)", key="exceso_input")
        patente = st.text_input("Patente", key="patente_input")
        observaciones = st.text_area("Observaciones", key="observaciones_input")

    fotos = st.file_uploader("Subir fotos (opcional)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    firma = st.file_uploader("Subir firma del chofer (opcional)", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("Generar PDF")

    if submitted:
        valido, error = validar_datos(hora, dni, zona, exceso, patente)
        if not valido:
            st.error(error)
        else:
            datos_formulario = {
                "hora": hora,
                "chofer": chofer,
                "dni": dni,
                "empresa": empresa,
                "sector": sector,
                "zona": zona,
                "exceso": exceso,
                "patente": patente,
                "observaciones": observaciones,
                "guardia": guardia  # NUEVO CAMPO
            }
            pdf = generar_pdf(datos_formulario, fotos, firma)
            pdf_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pdf.output(pdf_output.name)
            with open(pdf_output.name, "rb") as f:
                st.download_button(
                    "📥 Descargar Reporte PDF",
                    f,
                    file_name=f"Reporte_Exceso_{patente}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
