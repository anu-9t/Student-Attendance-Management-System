"""Downloads of a Report (SAM-F-020): CSV for spreadsheets, PDF for printing or sharing."""
import csv

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
