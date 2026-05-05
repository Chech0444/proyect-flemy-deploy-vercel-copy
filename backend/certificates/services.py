from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def build_certificate_pdf(certificate):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(80, 720, "Certificado de Finalizacion")
    pdf.setFont("Helvetica", 14)
    pdf.drawString(80, 670, f"Estudiante: {certificate.user.get_full_name() or certificate.user.username}")
    pdf.drawString(80, 640, f"Curso: {certificate.course.title}")
    pdf.drawString(80, 610, f"Codigo unico: {certificate.code}")
    pdf.drawString(80, 580, f"Fecha: {certificate.generated_at:%Y-%m-%d}")
    pdf.save()
    buffer.seek(0)
    return buffer
