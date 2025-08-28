import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Reporte Exceso Vicuña", layout="centered")

# ---- Estilos CSS para portal profesional ----
st.markdown("""
    <style>
        body { background-color: #0E1117; color: #FAFAFA; font-family: Arial, sans-serif; }
        h1, label, p { color: #FAFAFA !important; font-family: Arial, sans-serif; }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>input { 
            background-color: #1E1E1E !important; 
            color: white !important; 
            border: 1px solid #444444 !important;
            border-radius: 5px !important;
            padding: 5px !important;
        }
        .stButton>button { 
            background-color: #6200EE; 
            color: white; 
            border-radius: 8px; 
            padding: 0.8em 1.5em; 
            font-family: Arial, sans-serif; 
            font-weight: bold;
        }
        .stButton>button:hover { background-color: #3700B3; color: white; }
        .stForm { background-color: #121212; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("Control de Exceso de Velocidad - Proyecto Vicuña")

# ---- Formulario profesional ----
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
    enviar = st.form_submit_button("Generar PDF")

# ---- Generar PDF corporativo ----
if enviar:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "", 12)

    # Encabezado corporativo
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Señores", ln=True)
    pdf.cell(0, 10, "Seguridad Patrimonial", ln=True)
    pdf.cell(0, 10, "Proyecto Vicuña", ln=True)
    pdf.cell(0, 10, "S_/_D", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Para informar, exceso de velocidad:", ln=True)
    pdf.ln(5)

    # ---- Tabla con colores alternos ----
    pdf.set_font("Arial", "B", 12)
    def add_row(label, value, fill=False):
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(230, 230, 230) if fill else pdf.set_fill_color(245, 245, 245)
        pdf.cell(60, 10, label, border=1, fill=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, str(value), border=1, ln=True, fill=True)

    # Alternando colores
    add_row("Hora del registro", f"{hora}Hs", fill=True)
    add_row("Chofer", f"{chofer} (DNI: {dni})", fill=False)
    add_row("Empresa", empresa, fill=True)
    add_row("Sector", sector, fill=False)
    add_row("Zona de velocidad", f"{zona} km/h", fill=True)
    add_row("Exceso de velocidad", f"{exceso} km/h", fill=False)
    add_row("Dominio del vehículo", patente, fill=True)

    if observaciones.strip() != "":
        add_row("Observaciones adicionales", observaciones, fill=False)

    pdf.ln(5)
    pdf.multi_cell(0, 10, "Se remite a Staff de Seguridad Patrimonial.\nSe adjunta registro fotográfico.")

    # Pie de página corporativo
    pdf.set_y(-30)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Reporte generado automáticamente - Proyecto Vicuña", ln=True, align="C")

    # Guardar PDF
    pdf_file = "Reporte_Exceso_Vicuna_Profesional.pdf"
    pdf.output(pdf_file)

    with open(pdf_file, "rb") as f:
        st.download_button("Descargar Reporte PDF", f, file_name=pdf_file, mime="application/pdf")

    st.success("Reporte generado correctamente")
