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

# Función para optimizar imágenes (ya incluida, pero revisada para el flujo de PDF)
def optimizar_imagen(imagen_bytes, max_ancho=800):
    img = Image.open(imagen_bytes)
    # Convertir a RGB si es necesario (para compatibilidad con FPDF y evitar errores PNG/paleta)
    if img.mode == 'P':
        img = img.convert('RGB')
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

    # --- Imágenes ---
    if fotos_files:
        # Ancho disponible para cada columna (con márgenes de 15mm a cada lado y 5mm entre columnas)
        ancho_pagina = pdf.w - 2 * pdf.l_margin
        ancho_columna = (ancho_pagina - 5) / 2 # 5mm de espacio entre columnas
        max_alto_imagen = 70 # Altura máxima para cada imagen para evitar que sean demasiado grandes

        # Lista para almacenar las rutas temporales de las imágenes
        temp_image_paths = []

        try:
            for i, foto_file in enumerate(fotos_files):
                img_bytes = foto_file.getvalue()
                # Optimizar la imagen y guardarla temporalmente
                img_pil = optimizar_imagen(img_bytes, max_ancho=int(ancho_columna * pdf.dpi / 25.4))
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    img_pil.save(tmp.name, format="PNG")
                    temp_image_paths.append(tmp.name)

            for i, temp_path in enumerate(temp_image_paths):
                # Calcular dimensiones de la imagen en mm
                img_pil = Image.open(temp_path)
                ancho_px, alto_px = img_pil.size
                
                # Convertir de píxeles a mm (considerando una resolución típica de 96 DPI para imágenes web, si no se especifica otra)
                # OJO: La conversión de px a mm depende de la DPI. FPDF asume 72 DPI por defecto, pero PIL maneja la imagen en px.
                # Para evitar problemas, ajustamos el ancho en mm basándonos en el ancho de columna deseado.
                # Y el alto se calcula proporcionalmente.
                ancho_mm = ancho_columna
                alto_mm = (alto_px / ancho_px) * ancho_mm

                # Si la imagen es demasiado alta, la reescalamos manteniendo la proporción
                if alto_mm > max_alto_imagen:
                    alto_mm = max_alto_imagen
                    ancho_mm = (ancho_px / alto_px) * alto_mm
                    # Asegurarse de que no exceda el ancho de columna después de reescalar por alto
                    if ancho_mm > ancho_columna:
                        ancho_mm = ancho_columna
                        alto_mm = (alto_px / ancho_px) * ancho_mm


                # Determinar la posición X
                if i % 2 == 0: # Imagen en la columna izquierda
                    x_pos = pdf.l_margin
                else: # Imagen en la columna derecha
                    x_pos = pdf.l_margin + ancho_columna + 5 # 5mm de espacio entre columnas
                
                # Determinar la posición Y
                # Verificar si hay espacio suficiente para la imagen actual
                if pdf.get_y() + alto_mm > (pdf.h - pdf.b_margin):
                    pdf.add_page() # Añadir nueva página si no hay espacio

                y_pos = pdf.get_y()
                pdf.image(temp_path, x=x_pos, y=y_pos, w=ancho_mm, h=alto_mm)

                if i % 2 == 1: # Si es la segunda imagen de un par (o si es la última y hay un par)
                    pdf.ln(alto_mm + 5) # Salto de línea después de un par de imágenes o la última imagen
                elif i == len(temp_image_paths) - 1: # Si es la última imagen y es impar
                    pdf.ln(alto_mm + 5) # Salto de línea para la imagen impar

        finally:
            # Limpiar archivos temporales
            for p in temp_image_paths:
                os.unlink(p)

    # --- Firma ---
    if firma_file:
        pdf.ln(10) # Espacio antes de la firma
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 6, "Firma del guardia:", 0, 0, 'L')
        
        # Guarda las coordenadas X e Y actuales para la caja de la firma
        x_start_box = pdf.get_x() # Obtener la posición X actual después del texto
        y_start_box = pdf.get_y()

        img_firma = Image.open(firma_file)
        # Optimizamos la imagen de la firma también
        img_firma_opt = optimizar_imagen(firma_file, max_ancho=int(60 * pdf.dpi / 25.4)) # Ancho deseado 60mm
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_sig:
            img_firma_opt.save(tmp_sig.name, format="PNG")
            
            ancho_firma_mm = 60 # Ancho fijo para la imagen de la firma
            alto_firma_mm = 30 # Alto fijo para la imagen de la firma

            # Dibujar el rectángulo primero
            # Ajustar la posición X para que la caja esté a la derecha del texto "Firma del guardia:"
            # El ancho de la caja es el ancho de la imagen más un pequeño padding
            # El alto de la caja es el alto de la imagen más un pequeño padding
            # x_box_pos = x_start_box - 2
            # pdf.rect(x_box_pos, y_start_box - 2, ancho_firma_mm + 4, alto_firma_mm + 4)
            
            # Dibujar la imagen de la firma
            # La imagen se superpone al texto de la firma, si se usa la misma línea
            # Para ponerla a la derecha del texto, necesitas calcular la posición
            ancho_texto_firma = pdf.get_string_width("Firma del guardia:")
            margen_izquierdo_firma_img = pdf.l_margin + ancho_texto_firma + 5 # 5mm de espacio después del texto
            
            # Asegurar que la firma no se superponga al texto y que quepa en la página
            if margen_izquierdo_firma_img + ancho_firma_mm > (pdf.w - pdf.r_margin):
                 # Si no cabe a la derecha, la ponemos en una nueva línea centrada
                 pdf.ln(8) # Baja una línea para evitar solapamiento con el texto
                 x_img = (pdf.w - ancho_firma_mm) / 2
                 pdf.image(tmp_sig.name, x=x_img, y=pdf.get_y() + 2, w=ancho_firma_mm, h=alto_firma_mm)
                 pdf.rect(x_img - 2, pdf.get_y(), ancho_firma_mm + 4, alto_firma_mm + 4)
                 pdf.ln(alto_firma_mm + 5)
            else:
                 # Si cabe a la derecha del texto "Firma del guardia:"
                 pdf.image(tmp_sig.name, x=margen_izquierdo_firma_img, y=pdf.get_y() - 1, w=ancho_firma_mm, h=alto_firma_mm)
                 pdf.rect(margen_izquierdo_firma_img - 2, pdf.get_y() - 3, ancho_firma_mm + 4, alto_firma_mm + 4)
                 pdf.ln(alto_firma_mm + 5) # Avanza después de la imagen y la caja

            os.unlink(tmp_sig.name)
        
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

        st.markdown("### Adjuntar fotografías del incidente (máx. 30 MB cada una)")
        fotos = st.file_uploader(
            "Seleccionar archivo(s) de imagen",
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
                
                # Nombre de archivo más descriptivo
                fecha_actual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_pdf = f"Reporte_Exceso_Vicuña_{datos['patente']}_{fecha_actual}.pdf"

                st.download_button(
                    label="Descargar Reporte PDF",
                    data=pdf_bytes,
                    file_name=nombre_pdf,
                    mime="application/pdf"
                )
                
                st.success("Reporte generado correctamente. ¡Haga clic en el botón de descarga!")
            except Exception as e:
                st.error(f"Hubo un error al generar el PDF: {e}")

