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
def generar_pdf_formato_oficial(datos, firma_file, fotos_files):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "", 10)

    # ... (El código de generación del PDF es el mismo que el anterior) ...
    # Asegúrate de que todas las imágenes temporales se eliminen dentro de esta función.

    # --- Encabezado ---
    # Posición de los logos (ajustar según tamaños reales)
    pdf.set_font("Arial", "", 8)
    pdf.set_xy(15, 15)
    pdf.cell(30, 5, "Gral. Juan Madariaga", 0, 0, 'L')
    
    pdf.set_font("Arial", "", 8)
    pdf.set_xy(50, 15)
    pdf.multi_cell(100, 4, "Dirección Provincial de Política y Seguridad Vial - Ministerio de Infraestructura y Servicios Públicos", 0, 'C')

    pdf.set_font("Arial", "", 8)
    pdf.set_xy(165, 15)
    pdf.multi_cell(30, 4, "GOBIERNO DE LA PROVINCIA DE BUENOS AIRES", 0, 'R')
    pdf.ln(15)

    # --- Sección: INFORMACIÓN DE LA CAUSA ---
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "INFORMACIÓN DE LA CAUSA", 1, 1, 'C', 1)
    
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font("Arial", "", 10)
    pdf.set_x(120)
    pdf.cell(40, 6, "Fecha de Impresión:", 0, 0, 'R')
    pdf.set_font("Arial", "B", 10)
    pdf.cell(35, 6, datetime.date.today().strftime("%d/%m/%Y"), 0, 1, 'L')
    
    pdf.ln(2)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Datos del Acta", 0, 1, 'L')
    pdf.ln(1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(50, 6, "Cant. Nro.:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(40, 6, "0Z-048-00163059-4-00", 0, 0, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(30, 6, "Estado:", 0, 0, 'R')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "Citada", 0, 1, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(50, 6, "Fecha y Hora:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(40, 6, f"{datetime.date.today().strftime('%d/%m/%Y')} {datos['hora']}", 0, 1, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(50, 6, "Lugar de la Infracción:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, f"{datos['sector']}", 0, 1, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(50, 6, "Jurisdicción Constatación:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(40, 6, datos['empresa'].upper(), 0, 0, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(30, 6, "Cantidad UF:", 0, 0, 'R')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "150", 0, 1, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(50, 6, "Importe:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "$59463.5", 0, 1, 'L')
    pdf.ln(3)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Imputaciones", 0, 1, 'L')
    pdf.ln(1)
    
    start_x = pdf.get_x()
    start_y = pdf.get_y()
    pdf.rect(start_x, start_y, pdf.w - 2 * pdf.l_margin, 20)
    pdf.set_xy(start_x + 2, start_y + 2)
    pdf.set_font("Arial", "", 9)
    pdf.cell(30, 6, "Artículo Nro.", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "Descripción", 0, 1, 'L')
    
    pdf.set_xy(start_x + 2, start_y + 8)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(30, 6, "28", 0, 0, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 6, "Por no respetar los límites reglamentarios de velocidad previstos.", 0, 'L')
    
    pdf.set_y(start_y + 20 + 5)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Datos del Presunto Infractor", 0, 1, 'L')
    pdf.ln(1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Tipo Documento:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(30, 6, "DNI", 0, 0, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Nro:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(30, 6, datos['dni'], 0, 0, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(20, 6, "Genero:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "M", 0, 1, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Apellido y Nombre:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, datos['chofer'], 0, 1, 'L')
    pdf.ln(3)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Datos del Vehículo", 0, 1, 'L')
    pdf.ln(1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Dominio:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(30, 6, datos['patente'].upper(), 0, 0, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Año:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(30, 6, "2015", 0, 0, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(20, 6, "Tipo:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "AUTOMÓVIL", 0, 1, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Marca:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(30, 6, "HONDA", 0, 0, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Modelo:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "HR-V LX CVT", 0, 1, 'L')
    pdf.ln(3)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Especificaciones del Equipo de Constatación", 0, 1, 'L')
    pdf.ln(1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Equipo Marca:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(30, 6, "SIVSA", 0, 0, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Nro Serie:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "00091", 0, 1, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Modelo:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "V002", 0, 1, 'L')
    pdf.ln(5)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Imágenes de la Infracción", 0, 1, 'L')
    pdf.ln(2)

    if fotos_files:
        col_width = (pdf.w - 2 * pdf.l_margin) / 2 - 2
        current_y = pdf.get_y()
        max_height_in_row = 0
        
        for i, foto_file in enumerate(fotos_files):
            imagen_optimizada = optimizar_imagen(foto_file, max_ancho=int(col_width * 3.7))
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                imagen_optimizada.save(tmp.name, format="PNG")
                
                img_w, img_h = imagen_optimizada.size
                height_mm = col_width * img_h / img_w

                x_pos = pdf.l_margin if i % 2 == 0 else pdf.l_margin + col_width + 4
                
                if current_y + height_mm > pdf.h - pdf.b_margin - 10:
                    pdf.add_page()
                    current_y = pdf.get_y()
                
                pdf.image(tmp.name, x=x_pos, y=current_y, w=col_width, h=height_mm)
                os.unlink(tmp.name)
                
                pdf.set_xy(x_pos, current_y + height_mm + 1)
                pdf.set_font("Arial", "", 7)
                pdf.multi_cell(col_width, 3, f"{datos['hora']} {datetime.date.today().strftime('%d/%m/%Y')} Ruta Prov. 74 Km {datos['sector']} ...", 0, 'L')
                
                max_height_in_row = max(max_height_in_row, height_mm + 10)

                if i % 2 == 1:
                    current_y += max_height_in_row + 5
                    pdf.set_y(current_y)
                    max_height_in_row = 0
        
        if len(fotos_files) % 2 == 1:
            current_y += max_height_in_row + 5
            pdf.set_y(current_y)
            
    if firma_file:
        pdf.set_y(pdf.h - pdf.b_margin - 40)
        pdf.set_x(pdf.w - pdf.r_margin - 60)
        
        pdf.set_font("Arial", "", 9)
        pdf.cell(60, 5, "Firma del guardia:", 0, 1, 'C')

        imagen_optimizada_firma = optimizar_imagen(firma_file, max_ancho=150)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_sig:
            imagen_optimizada_firma.save(tmp_sig.name, format="PNG")
            
            img_w_sig, img_h_sig = imagen_optimizada_firma.size
            width_firma_mm = 50
            height_firma_mm = width_firma_mm * img_h_sig / img_w_sig
            x_firma = pdf.w - pdf.r_margin - width_firma_mm - 5
            pdf.image(tmp_sig.name, x=x_firma, y=pdf.get_y(), w=width_firma_mm, h=height_firma_mm)
            os.unlink(tmp_sig.name)
        pdf.ln(10)

    # El cambio más importante está aquí: en lugar de guardar en un archivo,
    # obtén el contenido del PDF como bytes
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
    # Datos para la validación y el PDF
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
                # La función ahora devuelve el contenido del PDF, no una ruta de archivo.
                pdf_bytes = generar_pdf_formato_oficial(datos_formulario, firma, fotos_validas)
                
                # El botón de descarga usa directamente los bytes.
                st.download_button(
                    label="Descargar Reporte PDF",
                    data=pdf_bytes,
                    file_name="Reporte_Exceso_Vicuña.pdf",
                    mime="application/pdf"
                )
                
                st.success("Reporte generado correctamente. ¡Haga clic en el botón de descarga!")
            except Exception as e:
                st.error(f"Hubo un error al generar el PDF: {e}")
