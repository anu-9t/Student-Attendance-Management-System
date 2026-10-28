"""Downloads of a Report (SAM-F-020): CSV for spreadsheets, PDF for printing or sharing."""
import csv
import io

from django.http import HttpResponse
from django.utils import timezone


def _filename(report, ext):
    return f"sams-{report.slug}-{timezone.localdate():%Y%m%d}.{ext}"


def as_csv(report):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{_filename(report, "csv")}"'
    response.write("﻿")  # so Excel opens the file as UTF-8
    writer = csv.writer(response)
    writer.writerow([report.title])
    writer.writerow([report.subtitle])
    writer.writerow([])
    writer.writerow(report.columns)
    for row in report.rows:
        writer.writerow([_safe(cell) for cell in row])
    return response


def _safe(cell):
    """Stop a spreadsheet from treating a cell as a formula (CSV injection)."""
    text = str(cell)
    return "'" + text if text[:1] in ("=", "+", "-", "@") and text != "-" else cell


def as_pdf(report, generated_by=""):
    """A printable A4 PDF of the report (landscape when it has many columns)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    pagesize = landscape(A4) if len(report.columns) > 6 else A4
    doc = SimpleDocTemplate(
        buffer, pagesize=pagesize, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
        title=report.title, author="SAMS",
    )
    styles = getSampleStyleSheet()
    stamp = f"Generated {timezone.localtime():%d %b %Y %H:%M}" + (f" by {generated_by}" if generated_by else "")
    story = [
        Paragraph(report.title[:1].upper() + report.title[1:], styles["Title"]),
        Paragraph(report.subtitle, styles["Normal"]),
        Paragraph(stamp, styles["Italic"]),
        Spacer(1, 6 * mm),
    ]
    data = [report.columns] + [[str(c) for c in row] for row in report.rows]
    if len(data) == 1:
        data.append(["No active students."] + [""] * (len(report.columns) - 1))
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6f9")]),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    story.append(table)
    doc.build(story)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{_filename(report, "pdf")}"'
    return response
