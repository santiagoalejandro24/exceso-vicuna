import streamlit as st
from fpdf import FPDF
from datetime import datetime
import base64

# ---- CONFIGURACIÓN ----
st.set_page_config(page_title="Proyecto Vicuña - Registro de Excesos", layout="centered")

# ---- ESTILO CSS PERSONALIZADO ----
st.markdown("""
    <style>
    body {
        background-color: #f4f6f9;
    }
    .main {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1a3d7c;
        text-align: center;
    }
    footer {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# ---- ENCABEZADO ----
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Warning_icon.svg/240px-Warning_icon.svg.png", width=80)
st.title("🚨 Registro de Exceso de Velocidad")
st.markdown("**Proyecto Vicuña - Seguridad Patrimonial**")

# ---- FORMULARIO ----
with st.form("exceso_form"):
    col1, col2 = st.columns(2)
    with col1:
        hora = st.time_input("Hora del incidente", value=datetime.now().time())
        chofer = st.text_input("Nombre del chofer")
        dni = st.text_input("DNI")
        empresa = st.text_input("Empresa")
    with col2:
        sector = st.text_input("Sector")
        limite = st.number_input("Límite velocidad (km/h)", min_value=0)
        velocidad = st.number_input("Velocidad registrada (km/h)", min_value=0)
        dominio = st.text_input("Dominio del vehículo")
    foto = st.file_uploader("📷 Registro fotográfico", type=["jpg", "jpeg", "png"])
    
    submit = st.form_submit_button("✅ Generar Informe PDF")

# ---- LÓGICA ----
if submit:
    if not chofer or not dni or not empresa or not dominio:
        st.error("⚠️ Complete todos los campos obligatorios.")
    else:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Encabezado
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Informe de Exceso de Velocidad - Proyecto Vicuña", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.ln(10)

        pdf.multi_cell(0, 10, "Señores\nSeguridad Patrimonial\nProyecto Vicuña\nS_/_D\n")

        # Texto principal
        texto = f"""
Para informar, exceso de velocidad:

* Siendo las {hora.strftime('%H:%M')}Hs
- Chofer Sr. {chofer} (DNI: {dni}).
- Empresa {empresa} para Proyecto Vicuña.
- Sector {sector}.
- Zona de {limite} km/h.
- Exceso de velocidad de {velocidad} km/h.
- Camioneta dominio: {dominio}.

Se remite a Staff de Seguridad Patrimonial.
"""
        pdf.multi_cell(0, 10, texto)

        # Agregar foto si existe
        if foto:
            with open("temp.jpg", "wb") as f:
                f.write(foto.getbuffer())
            pdf.image("temp.jpg", x=10, y=120, w=100)

        # Guardar PDF
        file_name = f"Exceso_{dominio}.pdf"
        pdf.output(file_name)

        # Descargar PDF
        with open(file_name, "rb") as f:
            pdf_bytes = f.read()
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a style="background:#1a3d7c;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;" href="data:application/octet-stream;base64,{b64}" download="{file_name}">📥 Descargar PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

        # Botón WhatsApp
        mensaje = f"""Exceso de velocidad:
Chofer: {chofer} ({dni})
Empresa: {empresa}
Sector: {sector}
Velocidad: {velocidad} km/h (Zona {limite})
Dominio: {dominio}
"""
        url = f"https://wa.me/?text={mensaje.replace(' ', '%20')}"
        st.markdown(f"[📲 Enviar por WhatsApp]({url})")

        st.success("✅ Informe generado con éxito.")

# ---- FOOTER ----
st.markdown("---")
st.caption("📌 Proyecto Vicuña | Seguridad Patrimonial © 2025")
