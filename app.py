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
body { background-color: #0E1117; color: #FAFAFA; font-family: Arial, sans-serif; }
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>input {
    background-color: #1E1E1E !important; color: white !important;
    border: 1px solid #444444 !important; border-radius: 5px !important; padding: 5px !important;
}
.stButton>button { background-color: #6200EE; color: white; border-radius: 8px; padding: 0.8em 1.5em; font-weight: bold;}
.stButton>button:hover { background-color: #3700B3; color: white; }
.stForm { background-color: #121212; padding: 20px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("Control de Exceso de Velocidad - Proyecto Vicuña")

# Función para optimizar imágenes
def optimizar_imagen(imagen_bytes, max_ancho=800):
    img = Image.open(imagen_bytes)
    if img.width > max_ancho:
        proporcion = max_ancho / img.width
        nuevo_alto = int(img.height * proporcion)
        img = img.resize((max_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    return img

# Función para validar datos del formulario
def validar_formulario(hora, chofer, dni, empresa, sector, patente, zona, exceso):
    if not all([hora, chofer, dni, empresa, sector, patente]):
        return False, "Por favor, complete todos los campos obligatorios."
    
    if not re.match(r"^\d{2}:\d{2}$", hora):
        return False, "Formato de hora incorrecto. Use HH:MM (ej. 09:52)."

    if not dni.isdigit() or not (7 <= len(dni) <= 8):
        return False, "DNI inválido. Debe contener entre 7 y 8 dígitos numéricos."
    
    if not isinstance(zona, (int, float)) or not isinstance(exceso, (int, float)):
        return False, "Zona y Exceso de velocidad deben ser números."
        
    return True, ""

# --- Función para generar el PDF y devolver sus bytes ---
def generar_pdf_formato_nuevo(datos, firma_file, fotos_files):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- Encabezado ---
    # Configurar el color verde
    pdf.set_text_color(0, 128, 0)
    
    # Texto "HUARPE" - Tamaño de fuente 40
    # Altura reducida para menor separación
    pdf.set_font("Arial", "B", 40)
    pdf.cell(0, 12, "HUARPE", 0, 1, 'C')
    
    # Texto "SEGURIDAD INTEGRAL" - Tamaño de fuente 24
    # Altura reducida para menor separación
    pdf.set_font("Arial", "", 24)
    pdf.cell(0, 8, "SEGURIDAD INTEGRAL", 0, 1, 'C')

    # Volver al color negro para el resto del documento
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # --- Detalles de la solicitud ---
    pdf.set_font("Arial", "", 10)
    pdf.cell(40, 6, "Señores", 0, 1)
    pdf.cell(40, 6, "Seguridad Patrimonial", 0, 1)
    pdf.cell(40, 6, "Proyecto Vicuña", 0, 1)
    pdf.cell(40, 6, "S_/_D", 0, 1)
    pdf.ln(5)
    pdf.cell(0, 6, "Para informar, exceso de velocidad:", 0, 1)
    pdf.ln(3)

    # --- Tabla de datos ---
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(220, 220, 220)
    
    # Encabezados de la tabla
    pdf.cell(60, 8, "Hora del registro", 1, 0, 'L', 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, datos['hora'], 1, 1, 'L')
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 8, "Chofer", 1, 0, 'L', 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"{datos['chofer']} (DNI: {datos['dni']})", 1, 1, 'L')
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 8, "Empresa", 1, 0, 'L', 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, datos['empresa'], 1, 1, 'L')
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 8, "Sector", 1, 0, 'L', 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, datos['sector'], 1, 1, 'L')
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 8, "Zona de velocidad", 1, 0, 'L', 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"{datos['zona']} km/h", 1, 1, 'L')
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 8, "Exceso de velocidad", 1, 0, 'L', 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"{datos['exceso']} km/h", 1, 1, 'L')
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 8, "Dominio del vehículo", 1, 0, 'L', 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, datos['patente'], 1, 1, 'L')
    
    pdf.ln(10)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "Se remite a Staff de Seguridad Patrimonial.", 0, 1)
    pdf.cell(0, 6, "Se adjunta registro fotográfico.", 0, 1)
    pdf.ln(10)

    # --- Imágenes y firma (misma lógica que antes) ---
    if fotos_files:
        col_width = (pdf.w - 30) / 2
        max_height_in_row = 0
        for i, foto_file in enumerate(fotos_files):
            image = Image.open(foto_file)
            width_mm = min(image.width * 25.4 / 96, col_width)
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

            if len(fotos_files) % 2 == 1:
                pdf.ln(max_height_in_row + 5)

    if firma_file:
        pdf.ln(10)
        # Imprime el texto de la firma en el lado izquierdo
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 6, "Firma del guardia:", 0, 0, 'L')
        
        # Guarda las coordenadas X e Y actuales
        x_start = pdf.get_x()
        y_start = pdf.get_y()

        img = Image.open(firma_file)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_sig:
            img.save(tmp_sig.name, format="PNG")
            
            # Dibuja la caja y la imagen en la misma línea
            pdf.rect(x_start - 2, y_start - 2, 60 + 4, 30 + 4)
            pdf.image(tmp_sig.name, x=x_start, y=y_start, w=60, h=30)
            
            os.unlink(tmp_sig.name)
        
        # Avanza a la siguiente línea después de la imagen
        pdf.ln(40)

    return pdf.output(dest='S').encode('latin1')

# ---- Contenedor del formulario ----
with st.container():
    with st.form("formulario_reporte"):
        st.markdown("### Complete los datos del registro")
        
        col1, col2 = st.columns(2)
        with col1:
            hora = st.text_input("Hora del registro (ej: 09:52)", key="hora_input")
            chofer = st.text_input("Chofer (Nombre y Apellido)", key="chofer_input")
            dni = st.text_input("DNI del chofer", key="dni_input")
            empresa = st.text_input("Empresa", key="empresa_input")
        with col2:
            sector = st.text_input("Sector (ej: Km 170, La Majadita, etc.)", key="sector_input")
            zona = st.number_input("Zona de velocidad permitida (km/h)", min_value=0, max_value=200, key="zona_input")
            exceso = st.number_input("Exceso de velocidad registrado (km/h)", min_value=0, max_value=300, key="exceso_input")
            patente = st.text_input("Dominio del vehículo", key="patente_input")
        
        observaciones = st.text_area("Observaciones adicionales (opcional)", key="observaciones_input")

        st.markdown("### Firma del guardia (subir imagen .png o .jpg)")
        firma = st.file_uploader("Subir imagen de firma", type=["png", "jpg", "jpeg"], key="firma_uploader")

        fotos = st.file_uploader(
            "Adjunte archivo(s) fotográfico(s) (máx. 30 MB cada uno)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="fotos_uploader"
        )

        enviar = st.form_submit_button("Generar PDF")

# ---- Generar PDF con indicador visual ----
if enviar:
    datos_formulario = {
        "hora": hora,
        "chofer": chofer,
        "dni": dni,
        "empresa": empresa,
        "sector": sector,
        "zona": zona,
        "exceso": exceso,
        "patente": patente,
        "observaciones": observaciones
    }

    es_valido, mensaje = validar_formulario(hora, chofer, dni, empresa, sector, patente, zona, exceso)

    if not es_valido:
        st.warning(mensaje)
    else:
        fotos_validas = []
        for foto in fotos if fotos else []:
            if foto.size > 30 * 1024 * 1024:
                st.warning(f"El archivo {foto.name} supera 30 MB y no será incluido en el PDF.")
            else:
                fotos_validas.append(foto)

        with st.spinner("Generando PDF, por favor espere..."):
            try:
                pdf_bytes = generar_pdf_formato_nuevo(datos_formulario, firma, fotos_validas)
                
                st.download_button(
                    label="Descargar Reporte PDF",
                    data=pdf_bytes,
                    file_name="Reporte_Exceso_Vicuña.pdf",
                    mime="application/pdf"
                )
                
                st.success("Reporte generado correctamente. ¡Haga clic en el botón de descarga!")
            except Exception as e:
                st.error(f"Hubo un error al generar el PDF: {e}")
            
