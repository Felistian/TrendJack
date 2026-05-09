# utils/pdf_export.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from datetime import datetime


def export_pdf(campaign_id: int, pipeline_result: dict, output_dir: str = None) -> str:
    """
    Generate PDF report for an approved campaign.

    Args:
        campaign_id    : DB campaign ID
        pipeline_result: Full result dict from loop.py
        output_dir     : Where to save PDF (default: project root)

    Returns:
        Path to generated PDF file
    """
    if output_dir is None:
        output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    filename = f"campaign_{campaign_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc    = SimpleDocTemplate(filepath, pagesize=A4,
                               leftMargin=2*cm, rightMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []

    # ── Custom Styles ────────────────────────────────────
    title_style = ParagraphStyle("title_style",
        parent=styles["Heading1"],
        fontSize=22, textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6)

    subtitle_style = ParagraphStyle("subtitle_style",
        parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#888888"),
        spaceAfter=20)

    section_style = ParagraphStyle("section_style",
        parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#16213e"),
        spaceBefore=16, spaceAfter=8)

    body_style = ParagraphStyle("body_style",
        parent=styles["Normal"],
        fontSize=10, leading=16,
        textColor=colors.HexColor("#333333"))

    # ── Header ───────────────────────────────────────────
    story.append(Paragraph("TrendJack Campaign Report", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}  |  Campaign ID: {campaign_id}",
        subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 0.4*cm))

    # ── Trend Info ───────────────────────────────────────
    trend = pipeline_result.get("trend", {})
    story.append(Paragraph("Trend Source", section_style))
    story.append(Paragraph(f"<b>Keyword:</b> {pipeline_result.get('keyword','')}", body_style))
    story.append(Paragraph(f"<b>Title:</b> {trend.get('title','')}", body_style))
    story.append(Paragraph(f"<b>URL:</b> {trend.get('url','')}", body_style))
    story.append(Spacer(1, 0.4*cm))

    # ── Ad Copy ──────────────────────────────────────────
    ad = pipeline_result.get("ad_copy", {})
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#eeeeee")))
    story.append(Paragraph("Final Ad Copy", section_style))

    for platform, label in [("instagram","Instagram"),
                              ("tiktok","TikTok"),
                              ("linkedin","LinkedIn")]:
        story.append(Paragraph(f"<b>{label}</b>", body_style))
        story.append(Paragraph(ad.get(platform, ""), body_style))
        story.append(Spacer(1, 0.3*cm))

    # ── Validation Scores ────────────────────────────────
    val = pipeline_result.get("validation", {})
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#eeeeee")))
    story.append(Paragraph("Validation Scores", section_style))

    score_data = [
        ["Criterion", "Score", "Status"],
        ["Tone",           f"{val.get('tone_score',0)}/100",
         "✓ Pass" if val.get('tone_score',0) >= 70 else "✗ Fail"],
        ["Brand Fit",      f"{val.get('brand_fit_score',0)}/100",
         "✓ Pass" if val.get('brand_fit_score',0) >= 70 else "✗ Fail"],
        ["Accuracy",       f"{val.get('accuracy_score',0)}/100",
         "✓ Pass" if val.get('accuracy_score',0) >= 70 else "✗ Fail"],
        ["Trend Relevance",f"{val.get('trend_relevance',0)}/100",
         "✓ Pass" if val.get('trend_relevance',0) >= 70 else "✗ Fail"],
        ["Overall",        f"{val.get('overall_score',0)}/100",
         "✓ Pass" if val.get('overall_score',0) >= 70 else "✗ Fail"],
    ]

    table = Table(score_data, colWidths=[8*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), colors.HexColor("#16213e")),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),
         [colors.HexColor("#f9f9f9"), colors.white]),
        ("GRID",         (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ("ALIGN",        (1,0), (-1,-1), "CENTER"),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.4*cm))

    # ── Attempts Summary ─────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#eeeeee")))
    story.append(Paragraph("Pipeline Summary", section_style))
    story.append(Paragraph(
        f"Total Attempts: {pipeline_result.get('total_attempts', 1)}  |  "
        f"Final Status: {'APPROVED' if pipeline_result.get('final_passed') else 'REVIEWED'}",
        body_style))

    # ── Build PDF ────────────────────────────────────────
    doc.build(story)
    print(f"PDF exported: {filepath}")
    return filepath

if __name__ == "__main__":
    sample_result = {
        "keyword": "skincare",
        "trend": {
            "title": "Top 8 Digital Marketing Trends for Skincare Brands in 2025",
            "url": "https://example.com/skincare-trends"
        },
        "ad_copy": {
            "instagram": "Skincare decoded. Science meets beauty. #SkincareTrends2025",
            "tiktok": "Wait — are beauty brands actually showing receipts now? Shop the science!",
            "linkedin": "The skincare industry is undergoing a trust revolution. How is your brand adapting?"
        },
        "validation": {
            "tone_score": 90, "brand_fit_score": 85,
            "accuracy_score": 95, "trend_relevance": 92,
            "overall_score": 90.5
        },
        "total_attempts": 1,
        "final_passed": True
    }

    path = export_pdf(campaign_id=1, pipeline_result=sample_result)
    print("PDF saved to:", path)