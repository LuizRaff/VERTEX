from pathlib import Path
import ast
import pandas as pd
import plotly.io as pio
import IsaricDraw as idw
from reportlab.platypus import (
    SimpleDocTemplate,
    Image,
    Paragraph,
    Spacer,
    PageBreak,
    Table as RTable,
    TableStyle,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from descriptive_dashboard_public import get_visuals
from reportlab.lib import colors

idw.save_inputs_to_file = lambda locals_dict: None

root = Path(__file__).resolve().parent
data_root = root / "projects" / "Claudia" / "PUBLIC" / "data"
metadata_file = data_root / "dashboard_metadata.txt"
tmp_dir = root / "reporting" / "tmp_images"
output_pdf = root / "reporting" / "dashboard_report.pdf"


def generate_report_from_dashboard(data_root: Path, metadata_file: Path):
    """
    Uses the existing get_visuals logic to load all figures and tables.
    Returns list of (title, fig_obj).
    """
    meta_raw = metadata_file.read_text(encoding="utf-8")
    buttons = ast.literal_eval(meta_raw)

    buttons_with_visuals = get_visuals(str(data_root), buttons)

    assets = []
    for btn in buttons_with_visuals:
        title = btn.get("label") or btn.get("suffix") or "Figure"
        for fig_obj in btn["visuals"]:
            fig = fig_obj[0] if isinstance(fig_obj, tuple) else fig_obj
            assets.append((title, fig))
    return assets


def build_pdf(assets, tmp_dir: Path, output_pdf: Path):
    """
    Builds a PDF that includes Plotly figures as images and Plotly tables as native ReportLab tables,
    scaling tables to fit within page margins and allowing multi-page flows.
    """
    tmp_dir.mkdir(parents=True, exist_ok=True)
    margin = 20 * mm
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
    )
    styles = getSampleStyleSheet()
    story = []

    for idx, (title, fig) in enumerate(assets, start=1):
        story.append(Paragraph(title, styles["Heading2"]))
        story.append(Spacer(1, 4 * mm))

        if isinstance(fig, dict):
            from plotly.graph_objects import Figure

            fig = Figure(fig)

        table_traces = [t for t in fig.data if hasattr(t, "cells")]
        if table_traces:
            trace = table_traces[0]
            header = list(trace.header.values)
            cells = trace.cells.values
            rows = list(zip(*cells))
            data = [header] + [list(r) for r in rows]

            wrapped = []
            for i, row in enumerate(data):
                cells_wrapped = []
                for cell in row:
                    text = cell
                    if i == 0:
                        text = f"{cell}"
                    cells_wrapped.append(Paragraph(str(text), styles["BodyText"]))
                wrapped.append(cells_wrapped)

            num_cols = len(header)
            avail_width = A4[0] - doc.leftMargin - doc.rightMargin
            col_widths = [avail_width / num_cols] * num_cols

            tbl = RTable(wrapped, colWidths=col_widths, repeatRows=1)
            tbl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            story.append(tbl)
        else:
            img_file = tmp_dir / f"figure_{idx}.png"
            pio.write_image(fig, img_file, engine="kaleido", width=800, height=600)
            story.append(
                Image(
                    str(img_file),
                    width=A4[0] - 2 * margin,
                    height=(A4[0] - 2 * margin) * 0.75,
                )
            )

        story.append(PageBreak())

    doc.build(story)
    print(f"✅ PDF generated")

def remove_pdf(output_pdf):
    """
    Remove the generated PDF file.
    """
    if output_pdf.exists():
        output_pdf.unlink()
    
def remove_tmp_images(tmp_dir):
    """
    Remove the temporary image files.
    """
    if tmp_dir.exists():
        for img_file in tmp_dir.glob("*.png"):
            img_file.unlink()

def main():
    assets = generate_report_from_dashboard(data_root, metadata_file)
    build_pdf(assets, tmp_dir, output_pdf)
    return (str(output_pdf), str(tmp_dir))