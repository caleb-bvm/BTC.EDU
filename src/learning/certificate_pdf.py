from io import BytesIO
from xml.sax.saxutils import escape

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def render_certificate(certificate):
    output = BytesIO()
    page = landscape(A4)
    document = SimpleDocTemplate(output, pagesize=page, leftMargin=25 * mm, rightMargin=25 * mm,
                                 topMargin=24 * mm, bottomMargin=22 * mm, title="Certificado de finalización BTC.EDU", author="BTC.EDU")
    label = ParagraphStyle("label", fontName="Helvetica", fontSize=11, leading=16, textColor=colors.HexColor("#354039"))
    title = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24, leading=29, spaceAfter=14)
    name = ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=23, leading=28, spaceAfter=14)
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=12, leading=18, spaceAfter=12)
    small = ParagraphStyle("small", fontName="Helvetica", fontSize=9, leading=14)
    # Paragraph wraps even long names/titles; no user text is interpreted as markup.
    story = [Paragraph("BTC.EDU / CERTIFICADO DE FINALIZACIÓN", label), Spacer(1, 10 * mm),
             Paragraph(escape(certificate.course_title), title), Paragraph("Otorgado a", body),
             Paragraph(escape(certificate.student_name), name),
             Paragraph(f"Por completar las lecciones requeridas y aprobar las evaluaciones obligatorias de la versión {certificate.enrollment.version.number}.", body),
             Paragraph(f"Por {escape(certificate.creator_name)}. Emitido el {timezone.localtime(certificate.issued_at):%d/%m/%Y}.", body),
             Spacer(1, 5 * mm), Paragraph(f"Identificador: {certificate.pk}", small),
             Paragraph("Certificado de finalización. No acredita una titulación oficial.", small),
             Paragraph("El titular puede activar y compartir su página de verificación desde BTC.EDU.", small)]

    def frame(canvas, doc):
        canvas.setStrokeColor(colors.HexColor("#26312b"))
        canvas.setLineWidth(1.5)
        canvas.rect(12 * mm, 12 * mm, page[0] - 24 * mm, page[1] - 24 * mm)

    document.build(story, onFirstPage=frame, onLaterPages=frame)
    return output.getvalue()
