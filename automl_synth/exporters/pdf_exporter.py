"""PDF exporter - generates dataset card PDF."""

from __future__ import annotations

import html

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors

from automl_synth.types import GeneratedRow, QualityReport, ResearchReport


def _safe(text: str) -> str:
    """Escape HTML special characters for ReportLab Paragraph."""
    return html.escape(str(text))


def _wrap_text(text: str, max_len: int = 200) -> Paragraph:
    """Create a Paragraph with proper text wrapping."""
    escaped = _safe(text[:max_len])
    escaped = escaped.replace("\n", "<br/>")
    if len(text) > max_len:
        escaped = escaped.rstrip("...") + "..."
    return Paragraph(escaped, getSampleStyleSheet()["Normal"])


def export_pdf(
    rows: list[GeneratedRow],
    research: ResearchReport,
    quality: QualityReport,
    output_path: str,
) -> str:
    """Generate a PDF dataset card."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )
    styles = getSampleStyleSheet()
    story = []

    title_style = styles["Title"]
    title_style.fontSize = 24
    story.append(Paragraph("Dataset Card", title_style))
    story.append(Spacer(1, 12))

    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    story.append(Paragraph("Overview", heading_style))
    story.append(Paragraph(f"<b>Topic:</b> {_safe(research.topic)}", normal_style))
    story.append(Paragraph(f"<b>Total Rows:</b> {quality.total_rows}", normal_style))
    story.append(Paragraph(f"<b>Labels:</b> {_safe(', '.join(research.labels))}", normal_style))
    story.append(Paragraph(f"<b>Quality Score:</b> {quality.quality_score}/100 ({_safe(quality.quality_grade)})", normal_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Label Distribution", heading_style))
    label_data = [[Paragraph("<b>Label</b>", normal_style), Paragraph("<b>Count</b>", normal_style)]]
    for label, count in quality.label_distribution.items():
        label_data.append([Paragraph(_safe(label), normal_style), Paragraph(str(count), normal_style)])
    table = Table(label_data, colWidths=[3 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Quality Metrics", heading_style))
    story.append(Paragraph(f"<b>Class Balance Ratio:</b> {quality.class_balance_ratio}", normal_style))
    story.append(Paragraph(f"<b>Duplicate Rows:</b> {quality.duplicate_rows}", normal_style))
    story.append(Paragraph(f"<b>Avg Text Length:</b> {quality.avg_text_length} chars", normal_style))
    story.append(Paragraph(f"<b>Avg Word Count:</b> {quality.avg_word_count}", normal_style))
    story.append(Paragraph(f"<b>Vocabulary Diversity:</b> {quality.unique_vocabulary_ratio:.1%}", normal_style))
    story.append(Spacer(1, 12))

    if quality.warnings:
        story.append(Paragraph("Warnings", heading_style))
        for w in quality.warnings:
            story.append(Paragraph(f"- {_safe(w)}", normal_style))
        story.append(Spacer(1, 12))

    story.append(Paragraph("Sample Rows", heading_style))
    sample_data = [
        [
            Paragraph("<b>ID</b>", normal_style),
            Paragraph("<b>Text</b>", normal_style),
            Paragraph("<b>Label</b>", normal_style),
            Paragraph("<b>Difficulty</b>", normal_style),
        ]
    ]
    for row in rows[:10]:
        sample_data.append([
            Paragraph(str(row.id), normal_style),
            _wrap_text(row.text, max_len=250),
            Paragraph(_safe(row.label), normal_style),
            Paragraph(_safe(row.difficulty), normal_style),
        ])
    sample_table = Table(
        sample_data,
        colWidths=[0.4 * inch, 4.2 * inch, 1 * inch, 0.9 * inch],
        repeatRows=1,
    )
    sample_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("LEADING", (1, 1), (1, -1), 10),
        ("LEFTPADDING", (1, 1), (1, -1), 4),
        ("RIGHTPADDING", (1, 1), (1, -1), 4),
    ]))
    story.append(sample_table)

    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "<i>This dataset is synthetically generated by AutoML-Synth. "
        "Quality metrics are automated estimates and should be validated for production use.</i>",
        styles["Italic"],
    ))

    doc.build(story)
    return output_path
