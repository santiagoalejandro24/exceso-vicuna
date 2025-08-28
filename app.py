import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile
import os
import datetime # Para la fecha de impresión
import re # Para validaciones de formato

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
    # Campos obligatorios
    if not all([hora, chofer, dni, empresa, sector, patente]):
        return False, "Por favor, complete todos los campos obligatorios."
    
    # Validar formato de hora HH:MM
    if not re.match(r"^\d{2}:\d{2}$", hora):
        return False, "Formato de hora incorrecto. Use HH:MM (ej. 09:52)."

    # Validar DNI (7 u 8 dígitos numéricos)
    if not dni.isdigit() or not (7 <= len(dni) <= 8):
        return False, "DNI inválido. Debe contener entre 7 y 8 dígitos numéricos."
    
    # Validar que zona y exceso sean números (ya lo hace st.number_input, pero precaución)
    if not isinstance(zona, (int, float)) or not isinstance(exceso, (int, float)):
        return False, "Zona y Exceso de velocidad deben ser números."

    # Podrías añadir más validaciones aquí, como para la patente.
    # Ejemplo de validación de patente (Argentina): AAA123 o AA123AA
    # if not re.match(r"^[A-Z]{3}\s?\d{3}$", patente) and not re.match(r"^[A-Z]{2}\s?\d{3}\s?[A-Z]{2}$", patente):
    #     return False, "Formato de patente inválido. Use AAA123 o AA123AA."

    return True, ""


# --- Función para generar el PDF con el nuevo formato ---
def generar_pdf_formato_oficial(datos, firma_file, fotos_files):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "", 10)

    # Margenes
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.set_top_margin(15)

    # --- Encabezado ---
    # Posición de los logos (ajustar según tamaños reales)
    # Aquí simulamos con texto y un espacio, si tuvieras los logos en imágenes, los cargarías.
    # Logo Izquierdo (simulado)
    pdf.set_font("Arial", "", 8)
    pdf.set_xy(15, 15)
    pdf.cell(30, 5, "Gral. Juan Madariaga", 0, 0, 'L')
    pdf.image("http://googleusercontent.com/file_content/0", x=15, y=15, w=15) # Esto es un placeholder, deberías tener el logo real.
    
    # Texto central del encabezado
    pdf.set_font("Arial", "", 8)
    pdf.set_xy(50, 15)
    pdf.multi_cell(100, 4, "Dirección Provincial de Política y Seguridad Vial - Ministerio de Infraestructura y Servicios Públicos", 0, 'C')

    # Logo Derecho (simulado)
    pdf.set_font("Arial", "", 8)
    pdf.set_xy(165, 15)
    pdf.multi_cell(30, 4, "GOBIERNO DE LA PROVINCIA DE BUENOS AIRES", 0, 'R')
    # pdf.image("logo_bsas.png", x=180, y=15, w=15) # Si tienes el logo de Bs As

    pdf.ln(15) # Espacio después del encabezado

    # --- Sección: INFORMACIÓN DE LA CAUSA ---
    pdf.set_fill_color(220, 220, 220) # Gris claro para el fondo del título
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "INFORMACIÓN DE LA CAUSA", 1, 1, 'C', 1)
    
    pdf.set_y(pdf.get_y() + 2) # Espacio después del título

    # Fecha de Impresión
    pdf.set_font("Arial", "", 10)
    pdf.set_x(120) # Ajustar la posición X para que esté a la derecha
    pdf.cell(40, 6, "Fecha de Impresión:", 0, 0, 'R')
    pdf.set_font("Arial", "B", 10)
    pdf.cell(35, 6, datetime.date.today().strftime("%d/%m/%Y"), 0, 1, 'L')
    
    pdf.ln(2)

    # --- Sección: Datos del Acta ---
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Datos del Acta", 0, 1, 'L')
    pdf.ln(1)

    pdf.set_font("Arial", "", 9)
    # Fila 1
    pdf.cell(50, 6, "Cant. Nro.:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(40, 6, "0Z-048-00163059-4-00", 0, 0, 'L') # Número fijo o generar dinámico
    pdf.set_font("Arial", "", 9)
    pdf.cell(30, 6, "Estado:", 0, 0, 'R')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "Citada", 0, 1, 'L')

    # Fila 2
    pdf.set_font("Arial", "", 9)
    pdf.cell(50, 6, "Fecha y Hora:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(40, 6, f"{datetime.date.today().strftime('%d/%m/%Y')} {datos['hora']}", 0, 1, 'L')

    # Fila 3
    pdf.set_font("Arial", "", 9)
    pdf.cell(50, 6, "Lugar de la Infracción:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, f"{datos['sector']}, Ruta Prov. 74 23", 0, 1, 'L') # Usa tu 'sector'
    
    # Fila 4 (Jurisdicción y Cantidad UF)
    pdf.set_font("Arial", "", 9)
    pdf.cell(50, 6, "Jurisdicción Constatación:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(40, 6, datos['empresa'].upper(), 0, 0, 'L') # Usamos la empresa aquí
    pdf.set_font("Arial", "", 9)
    pdf.cell(30, 6, "Cantidad UF:", 0, 0, 'R')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "150", 0, 1, 'L') # Fijo o variable

    # Fila 5 (Importe)
    pdf.set_font("Arial", "", 9)
    pdf.cell(50, 6, "Importe:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "$59463.5", 0, 1, 'L') # Fijo o variable

    pdf.ln(3)
    # Recuadro para Imputaciones
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Imputaciones", 0, 1, 'L')
    pdf.ln(1)
    
    # Recuadro completo para las imputaciones
    start_x = pdf.get_x()
    start_y = pdf.get_y()
    pdf.rect(start_x, start_y, pdf.w - 2 * pdf.l_margin, 20) # Rectangulo de 20mm de alto

    pdf.set_xy(start_x + 2, start_y + 2) # Margen interno
    pdf.set_font("Arial", "", 9)
    pdf.cell(30, 6, "Artículo Nro.", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "Descripción", 0, 1, 'L')
    
    pdf.set_xy(start_x + 2, start_y + 8)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(30, 6, "28", 0, 0, 'L')
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 6, "Por no respetar los límites reglamentarios de velocidad previstos.", 0, 'L')
    
    pdf.set_y(start_y + 20 + 5) # Reposiciona el cursor después del recuadro

    # --- Sección: Datos del Presunto Infractor ---
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
    pdf.cell(20, 6, "Genero:", 0, 0, 'L') # No tenemos este dato en el formulario
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "M", 0, 1, 'L')

    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Apellido y Nombre:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, datos['chofer'], 0, 1, 'L')

    pdf.ln(3)

    # --- Sección: Datos del Vehículo ---
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
    pdf.cell(30, 6, "2015", 0, 0, 'L') # Fijo o variable
    pdf.set_font("Arial", "", 9)
    pdf.cell(20, 6, "Tipo:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "AUTOMÓVIL", 0, 1, 'L')

    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Marca:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(30, 6, "HONDA", 0, 0, 'L') # Fijo o variable
    pdf.set_font("Arial", "", 9)
    pdf.cell(40, 6, "Modelo:", 0, 0, 'L')
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "HR-V LX CVT", 0, 1, 'L') # Fijo o variable

    pdf.ln(3)

    # --- Sección: Especificaciones del Equipo de Constatación ---
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

    # --- Sección: Imágenes de la Infracción ---
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Imágenes de la Infracción", 0, 1, 'L')
    pdf.ln(2)

    if fotos_files:
        col_width = (pdf.w - 2 * pdf.l_margin) / 2 - 2 # Ancho para dos columnas, con un pequeño margen entre ellas
        current_y = pdf.get_y()
        max_height_in_row = 0
        
        for i, foto_file in enumerate(fotos_files):
            imagen_optimizada = optimizar_imagen(foto_file, max_ancho=int(col_width * 3.7)) # Ajustar max_ancho
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                imagen_optimizada.save(tmp.name, format="PNG")
                
                # Calcular alto proporcional
                img_w, img_h = imagen_optimizada.size
                height_mm = col_width * img_h / img_w

                x_pos = pdf.l_margin if i % 2 == 0 else pdf.l_margin + col_width + 4 # Margen entre columnas
                
                # Si la imagen excede el alto de la página o no hay espacio suficiente
                if current_y + height_mm > pdf.h - pdf.b_margin - 10: # 10mm de margen inferior extra
                    pdf.add_page()
                    current_y = pdf.get_y() # Resetear Y para la nueva página
                
                pdf.image(tmp.name, x=x_pos, y=current_y, w=col_width, h=height_mm)
                os.unlink(tmp.name)
                
                # Agregar texto de descripción debajo de la imagen (ajustar si es necesario)
                pdf.set_xy(x_pos, current_y + height_mm + 1)
                pdf.set_font("Arial", "", 7)
                # Puedes crear un texto dinámico o tomarlo de algún input si lo tuvieras
                pdf.multi_cell(col_width, 3, f"{datos['hora']} {datetime.date.today().strftime('%d/%m/%Y')} Ruta Prov. 74 Km {datos['sector']} ...", 0, 'L')
                
                max_height_in_row = max(max_height_in_row, height_mm + 10) # Sumar el espacio del texto

                if i % 2 == 1: # Si es la segunda imagen de la fila
                    current_y += max_height_in_row + 5 # Avanzar Y para la siguiente fila
                    pdf.set_y(current_y)
                    max_height_in_row = 0 # Resetear para la siguiente fila
        
        if len(fotos_files) % 2 == 1: # Si la última fila tiene una sola imagen
            current_y += max_height_in_row + 5
            pdf.set_y(current_y)
            
    # --- Firma del guardia ---
    # Podrías colocar la firma en la parte inferior de la última página.
    if firma_file:
        pdf.set_y(pdf.h - pdf.b_margin - 40) # Posicionar cerca del final
        pdf.set_x(pdf.w - pdf.r_margin - 60) # Alinear a la derecha
        
        pdf.set_font("Arial", "", 9)
        pdf.cell(60, 5, "Firma del guardia:", 0, 1, 'C') # Título

        imagen_optimizada_firma = optimizar_imagen(firma_file, max_ancho=150) # Ajustar para la firma
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_sig:
            imagen_optimizada_firma.save(tmp_sig.name, format="PNG")
            
            img_w_sig, img_h_sig = imagen_optimizada_firma.size
            # Calcular alto para una firma de 50mm de ancho (ej.)
            width_firma_mm = 50
            height_firma_mm = width_firma_mm * img_h_sig / img_w_sig

            # Centrar la firma en el espacio asignado (60mm de ancho)
            x_firma = pdf.w - pdf.r_margin - width_firma_mm - 5 # Ajuste para centrar en 60mm
            pdf.image(tmp_sig.name, x=x_firma, y=pdf.get_y(), w=width_firma_mm, h=height_firma_mm)
            os.unlink(tmp_sig.name)
        pdf.ln(10) # Espacio después de la firma

    # --- Guardar PDF ---
    pdf_output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(pdf_output_path)
    return pdf_output_path


# ---- Contenedor del formulario ----
with st.container():
    with st.form("formulario_reporte"):
        st.markdown("### Complete los datos del registro")
        
        # Campos del formulario
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

# ---- Vista previa de fotos y firma ----
if fotos:
    st.markdown("### Fotos subidas")
    for idx, foto in enumerate(fotos):
        # Para evitar problemas con el búfer, re-leer la imagen para la vista previa
        foto.seek(0) # Rebobinar el puntero del archivo
        st.image(foto, width=200, caption=f"Foto {idx+1}")
        foto.seek(0) # Rebobinar de nuevo si se va a usar en el PDF

if firma:
    st.markdown("### Firma subida")
    firma.seek(0)
    st.image(firma, width=200, caption="Firma del Guardia")
    firma.seek(0)

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
        # Filtrar fotos que excedan el tamaño
        fotos_validas = []
        for foto in fotos if fotos else []:
            if foto.size > 30 * 1024 * 1024:
                st.warning(f"El archivo {foto.name} supera 30 MB y no será incluido en el PDF.")
            else:
                fotos_validas.append(foto)

        with st.spinner("Generando PDF, por favor espere..."):
            try:
                # Pasar los objetos UploadedFile directamente para que la función los optimice
                pdf_file_path = generar_pdf_formato_oficial(datos_formulario, firma, fotos_validas)

                with open(pdf_file_path, "rb") as f:
                    st.download_button("Descargar Reporte PDF", f, file_name="Reporte_Exceso_Vicuña.pdf", mime="application/pdf")
                
                st.success("Reporte generado correctamente.")
            except Exception as e:
                st.error(f"Hubo un error al generar el PDF: {e}")
            finally:
                # Limpiar el archivo temporal del PDF
                if 'pdf_file_path' in locals() and os.path.exists(pdf_file_path):
                    os.unlink(pdf_file_path)

