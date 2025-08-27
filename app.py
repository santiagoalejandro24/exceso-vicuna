import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

st.set_page_config(page_title="Reporte Vicuña", layout="centered")

st.markdown(
    """
    <style>
    body {
        background-color: #1e1e1e;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📋 Control Diario - Proyecto Vicuña")

# --- Datos del formulario ---
chofer = st.text_input("Nombre del Chofer")
vehiculo = st.text_input("Vehículo")
fecha = st.date_input("Fecha")
hora = st.time_input("Hora")

if st.button("Generar PDF"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # --- Título ---
    title = Paragraph("<b>REPORTE DE CONTROL - PROYECTO VICUÑA</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # --- Datos principales en tabla ---
    data = [
        ["Fecha", str(fecha)],
        ["Hora", str(hora)],
        ["Chofer", chofer],
        ["Vehículo", vehiculo],
    ]

    table = Table(data, colWidths=[100, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4A90E2")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.8, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # --- Observaciones ---
    obs = Paragraph("<b>Observaciones:</b> ____________________________", styles['Normal'])
    elements.append(obs)

    # --- Firma ---
    firma = Paragraph("<br/><br/><b>Firma Responsable: _____________________</b>", styles['Normal'])
    elements.append(firma)

    # Construir PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    st.download_button(
        label="📥 Descargar Reporte PDF",
        data=pdf,
        file_name="reporte_vicuna.pdf",
        mime="application/pdf",
    )
