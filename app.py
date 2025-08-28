import streamlit as st
from fpdf import FPDF
from PIL import Image
from datetime import datetime

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

# ---- Formulario ----
with st.form("formulario"):
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

    fotos = st.file_uploader(
        "Adjunte archivo(s) fotográfico(s) (máx. 30 MB cada uno)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if fotos:
        fotos_validas = []
        for foto in fotos:
            if foto.size > 30 * 1024 * 1024:
                st.warning(f"El archivo {foto.name} supera 30 MB y no será incluido.")
            else:
                fotos_validas.append(foto)
        fotos = fotos_validas

    enviar = st.form_submit_button("Generar PDF")

# ---- Generar PDF ----
if enviar:
    campos_obligatorios = [hora, chofer, dni, empresa, sector, patente]
    if any(campo.strip() == "" for campo in campos_obligatorios):
        st.warning("Por favor, complete todos los campos obligatorios.")
    else:
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

        # --- Encabezado tipo informe ---
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 6, f"A: Staff de Seguridad Patrimonial – Proyecto Vicuña", ln=True)
        pdf.cell(0, 6, f"De: Patrulla Huarpe – Seguridad Integral", ln=True)
        pdf.cell(0, 6, f"Fecha: {fecha_actual}   Hora: {hora}", ln=True)
        pdf.ln(4)
        pdf.cell(0, 6, "Asunto: Registro de Exceso de Velocidad", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 6, f"Se informa que el vehículo {patente} conducido por {chofer} excedió la velocidad permitida en la zona {sector}. Se adjuntan fotografías correspondientes al registro.")
        pdf.ln(5)

        # --- Tabla de datos con colores suaves ---
        pdf.set_font("Arial", "B", 12)
        def add_row(label, value, fill=False):
            pdf.set_font("Arial", "B", 11)
            pdf.set_fill_color(240, 240, 240) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.cell(60, 10, label, border=1, fill=True)
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 10, str(value), border=1, ln=True, fill=True)

        datos = [
            ("Hora del registro", f"{hora}Hs"),
            ("Chofer", f"{chofer} (DNI: {dni})"),
            ("Empresa", empresa),
            ("Sector", sector),
            ("Zona de velocidad", f"{zona} km/h"),
            ("Exceso de velocidad", f"{exceso} km/h"),
            ("Dominio del vehículo", patente)
        ]
        if observaciones.strip() != "":
            datos.append(("Observaciones adicionales", observaciones))

        fill = False
        for label, value in datos:
            add_row(label, value, fill)
            fill = not fill

        pdf.ln(5)

        # --- Fotos corporativas (hasta 3 por fila) ---
        if fotos:
            pdf.ln(5)
            cols = 3
            col_width = (pdf.w - 20) / cols
            max_height_row = 0

            for i, foto in enumerate(fotos):
                image = Image.open(foto)
                dpi = 96
                width_mm = min(image.width * 25.4 / dpi, col_width)
                height_mm = width_mm * image.height / image.width
                max_img_height = 70
                height_mm = min(height_mm, max_img_height)
                max_height_row = max(max_height_row, height_mm)

                col = i % cols
                x_pos = 10 + col * col_width
                y_pos = pdf.get_y()

                # Título foto
                pdf.set_xy(x_pos, y_pos)
                pdf.set_font("Arial", "B", 9)
                pdf.multi_cell(width_mm, 4, f"{chofer} - {patente} (Foto {i+1})", align="C")

                y_pos += 6
                pdf.image(foto, x=x_pos, y=y_pos, w=width_mm, h=height_mm)
                pdf.set_draw_color(0, 0, 0)
                pdf.rect(x_pos, y_pos, width_mm, height_mm)

                if col == cols - 1:
                    pdf.ln(max_height_row + 12)
                    max_height_row = 0

            if len(fotos) % cols != 0:
                pdf.ln(max_height_row + 12)

            st.markdown("### Fotos subidas")
            for foto in fotos:
                st.image(foto, width=200)

        # --- Guardar PDF en memoria con UTF-8 (FPDF2) ---
        pdf_bytes = pdf.output(dest='S').encode('utf-8')

        st.download_button(
            "Descargar Reporte PDF",
            data=pdf_bytes,
            file_name="Reporte_Exceso-Vicuna_Profesional.pdf",
            mime="application/pdf"
        )

        st.success("Reporte generado correctamente")
