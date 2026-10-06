





from html import escape
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build/doc-tools"))

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from matplotlib import get_data_path
from app.version import VERSION


def inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`(.+?)`", r"<font name='Mono'>\1</font>", text)


def main() -> None:
    fonts = Path(get_data_path()) / "fonts/ttf"
    for name, filename in (("Body", "DejaVuSans.ttf"), ("BodyBold", "DejaVuSans-Bold.ttf"), ("Mono", "DejaVuSansMono.ttf")):
        pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyBold", italic="Body", boldItalic="BodyBold")
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = "Body"
    styles["BodyText"].fontSize = 9.5
    styles["BodyText"].leading = 14.5
    styles["BodyText"].spaceAfter = 6
    styles["BodyText"].textColor = colors.HexColor("#243448")
    for name in ("Title", "Heading1", "Heading2"):
        styles[name].fontName = "BodyBold"
        styles[name].textColor = colors.HexColor("#104d7d")
    styles["Title"].alignment = TA_LEFT
    styles["Title"].fontSize = 23
    styles["Title"].leading = 30
    styles["Heading1"].fontSize = 15
    styles["Heading1"].leading = 21
    styles["Heading2"].fontSize = 11
    styles["Heading2"].leading = 16

    output = ROOT / "output/pdf"
    output.mkdir(parents=True, exist_ok=True)
    destination = output / "Manual_LumenLab.pdf"
    story = []
    lines = (ROOT / "docs/MANUAL_DE_USO.md").read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if not line:
            continue
        if line.startswith("|"):
            rows = [line]
            while index < len(lines) and lines[index].startswith("|"):
                rows.append(lines[index]); index += 1
            cells = [[Paragraph(inline(cell.strip()), styles["BodyText"]) for cell in row.strip("|").split("|")]
                     for row in rows if not re.fullmatch(r"[| :\-]+", row)]
            table = Table(cells, colWidths=[491 / len(cells[0])] * len(cells[0]), repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2edf5")),
                ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#bbc9d4")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]))
            story += [table, Spacer(1, 10)]
        elif line.startswith("# "):
            story += [Paragraph(inline(line[2:]), styles["Title"]),
                      Paragraph(f"Manual do usuário · versão {VERSION} · 10 de setembro de 2026", styles["BodyText"])]
        elif line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), styles["Heading1"]))
        elif line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), styles["Heading2"]))
        else:
            story.append(Paragraph(inline(line[2:] if line.startswith('- ') else line), styles["BodyText"],
                                   bulletText="•" if line.startswith('- ') else None))

    screenshots = ROOT / "build/release-verification/dpi-1"
    if screenshots.exists():
        story += [PageBreak(), Paragraph("Telas da versão 1.1.0", styles["Heading1"])]
        for name, caption in (("comparacao", "Fendas: comparação do perfil atual com uma referência fixa."),
                              ("polarizacao", "Polarização: cascata de três elementos e resultados de cada etapa.")):
            story += [Image(str(screenshots / f"{name}.png"), width=491, height=276),
                      Paragraph(caption, styles["BodyText"]), Spacer(1, 12)]

    def footer(canvas, doc):
        canvas.setFillColor(colors.white)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.setStrokeColor(colors.HexColor("#bbc9d4"))
        canvas.line(52, 42, A4[0] - 52, 42)
        canvas.setFont("Body", 8)
        canvas.setFillColor(colors.HexColor("#52687a"))
        canvas.drawString(52, 28, f"LumenLab {VERSION} · Manual de uso · Offline")
        canvas.drawRightString(A4[0] - 52, 28, str(doc.page))

    doc = SimpleDocTemplate(str(destination), pagesize=A4, leftMargin=52, rightMargin=52,
                            topMargin=44, bottomMargin=58, title=f"Manual LumenLab {VERSION}", author="LumenLab")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

    from PySide6.QtCore import QSize
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    pdf = QPdfDocument()
    assert pdf.load(str(destination)) == QPdfDocument.Error.None_
    rendered = ROOT / "build/manual-preview"
    rendered.mkdir(parents=True, exist_ok=True)
    text = []
    for page in range(pdf.pageCount()):
        size = pdf.pagePointSize(page)
        image = pdf.render(page, QSize(1100, round(1100 * size.height() / size.width())))
        assert not image.isNull()
        image.save(str(rendered / f"page-{page + 1:02}.png"))
        text.append(pdf.getAllText(page).text())
    (rendered / "text.txt").write_text("\n".join(text), encoding="utf-8")
    print(f"PDF: {destination}; {pdf.pageCount()} pages rendered.")


if __name__ == "__main__":
    main()
