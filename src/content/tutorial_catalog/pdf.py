"""Original reference sheets rendered as PDF with the BTC.EDU visual language.

Black and white with one orange signal, the dot typeface only for the brand and the
monospace face for labels and code, as in the interface.
"""
from io import BytesIO
from xml.sax.saxutils import escape

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

INK = colors.HexColor("#000000")
MUTED = colors.HexColor("#6b6b6b")
LINE = colors.HexColor("#e6e6e6")
SOFT = colors.HexColor("#f5f5f5")
ORANGE = colors.HexColor("#ff6a13")
MARGIN = 18 * mm


def brand_font():
    try:
        pdfmetrics.getFont("BTCDot")
    except KeyError:
        pdfmetrics.registerFont(TTFont("BTCDot", str(settings.BASE_DIR / "static" / "fonts" / "Ndot77JPExtended.ttf")))
    return "BTCDot"


STYLES = {
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=INK, spaceAfter=6),
    "subtitle": ParagraphStyle("subtitle", fontName="Helvetica", fontSize=11, leading=15, textColor=MUTED, spaceAfter=14),
    "heading": ParagraphStyle("heading", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=INK, spaceBefore=12, spaceAfter=6),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.5, leading=14, textColor=INK, alignment=TA_LEFT, spaceAfter=5),
    "item": ParagraphStyle("item", fontName="Helvetica", fontSize=9.5, leading=13.5, textColor=INK, leftIndent=12, bulletIndent=0, spaceAfter=3),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=INK),
    "cell_head": ParagraphStyle("cell_head", fontName="Helvetica-Bold", fontSize=8.5, leading=11.5, textColor=INK),
    "cell_mono": ParagraphStyle("cell_mono", fontName="Courier", fontSize=8.5, leading=11.5, textColor=INK),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=8.5, leading=11.5, textColor=INK),
    "source": ParagraphStyle("source", fontName="Helvetica", fontSize=8, leading=11, textColor=MUTED, spaceAfter=2),
}


def text(value):
    """Plain text with `inline code` marked in the monospace face."""
    parts = escape(value).split("`")
    return "".join(f'<font name="Courier">{part}</font>' if index % 2 else part for index, part in enumerate(parts))


def table(data):
    mono = set(data.get("mono", []))
    rows = [[Paragraph(text(column), STYLES["cell_head"]) for column in data["columns"]]]
    for row in data["rows"]:
        rows.append([Paragraph(text(cell), STYLES["cell_mono" if index in mono else "cell"]) for index, cell in enumerate(row)])
    widths = data.get("widths")
    usable = A4[0] - 2 * MARGIN
    # Blank rows are spaces to fill in by hand, so they get room to write.
    heights = [None] + [None if any(cell for cell in row) else 8 * mm for row in data["rows"]]
    result = Table(rows, colWidths=[usable * width for width in widths] if widths else None,
                   rowHeights=heights, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 1, INK),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return result


def checkbox():
    # A square drawn as a table border keeps the box independent of font glyphs.
    box = Table([[""]], colWidths=[3.4 * mm], rowHeights=[3.4 * mm])
    box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, INK)]))
    return box


def checklist(items):
    rows = [[checkbox(), Paragraph(text(item), STYLES["cell"])] for item in items]
    result = Table(rows, colWidths=[7 * mm, A4[0] - 2 * MARGIN - 7 * mm], hAlign="LEFT")
    result.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return result


def code_block(value):
    block = Table([[Preformatted(value.strip("\n"), STYLES["code"])]], colWidths=[A4[0] - 2 * MARGIN], hAlign="LEFT")
    block.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT), ("BOX", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return block


def render_material(resource, category_name):
    """Return the PDF bytes of a material described in the catalog."""
    document = resource["document"]
    font = brand_font()
    buffer = BytesIO()

    def decorate(canvas, doc):
        width, height = A4
        canvas.saveState()
        canvas.setFont(font, 15)
        canvas.setFillColor(INK)
        canvas.drawString(MARGIN, height - 14 * mm, "BTC.EDU")
        canvas.setFillColor(ORANGE)
        canvas.rect(MARGIN + canvas.stringWidth("BTC.EDU", font, 15) + 1.5 * mm, height - 14 * mm, 1.8 * mm, 1.8 * mm, stroke=0, fill=1)
        canvas.setFillColor(MUTED)
        canvas.setFont("Courier", 7.5)
        canvas.drawRightString(width - MARGIN, height - 13.5 * mm, f"{category_name.upper()} / MATERIAL")
        canvas.setStrokeColor(INK)
        canvas.setLineWidth(0.6)
        canvas.line(MARGIN, height - 17 * mm, width - MARGIN, height - 17 * mm)
        canvas.setStrokeColor(LINE)
        canvas.line(MARGIN, 14 * mm, width - MARGIN, 14 * mm)
        canvas.setFont("Courier", 7.5)
        canvas.drawString(MARGIN, 9.5 * mm, resource["title"][:90])
        canvas.drawRightString(width - MARGIN, 9.5 * mm, f"{doc.page:02d}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=26 * mm, bottomMargin=20 * mm,
        title=resource["title"], author="BTC.EDU · Colecciones", subject=document.get("subtitle", ""), invariant=1,
    )
    story = [Paragraph(text(resource["title"]), STYLES["title"])]
    if document.get("subtitle"):
        story.append(Paragraph(text(document["subtitle"]), STYLES["subtitle"]))
    for section in document["sections"]:
        block = [Paragraph(text(section["heading"]), STYLES["heading"])]
        for paragraph in section.get("paragraphs", []):
            block.append(Paragraph(text(paragraph), STYLES["body"]))
        for item in section.get("items", []):
            block.append(Paragraph(text(item), STYLES["item"], bulletText="–"))
        if section.get("checklist"):
            block.append(checklist(section["checklist"]))
        if section.get("table"):
            block.append(table(section["table"]))
        if section.get("code"):
            block.append(code_block(section["code"]))
        # Keep a heading with the start of its content.
        story.append(KeepTogether(block[:2]))
        story.extend(block[2:])
    story.append(Spacer(1, 10))
    story.append(Paragraph("Fuentes", STYLES["heading"]))
    for source in resource["sources"]:
        story.append(Paragraph(f"{text(source['title'])}: {escape(source['url'])}", STYLES["source"]))
    story.append(Paragraph("Material original de BTC.EDU. Las fuentes citadas pertenecen a sus autores.", STYLES["source"]))
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    return buffer.getvalue()
