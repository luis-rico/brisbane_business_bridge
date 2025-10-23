"""
PDF Report Generator for Brisbane Business Bridge AI
Generates professional PDF reports with match results and synergy analysis
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
import io


def generate_match_report_pdf(user_info, matches):
    """
    Generate a PDF report for delegate matches

    Args:
        user_info: Dictionary with user information
        matches: List of top 3 match dictionaries

    Returns:
        BytesIO buffer containing the PDF
    """
    try:
        buffer = io.BytesIO()
    except Exception as e:
        print(f"[PDF ERROR] Failed to create buffer: {e}")
        raise

    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    # Container for elements
    elements = []

    # Get styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0066CC'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#003366'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        leading=16
    )

    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER
    )

    # Header
    elements.append(Paragraph("Brisbane Business Bridge AI", title_style))
    elements.append(Paragraph("Delegate Matching Report", heading_style))

    # Date
    report_date = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"Generated: {report_date}", small_style))
    elements.append(Spacer(1, 0.3*inch))

    # Horizontal line
    elements.append(Spacer(1, 0.1*inch))

    # User Information Section
    elements.append(Paragraph("Participant Information", heading_style))

    user_data = [
        ["Name:", user_info.get('name', 'N/A')],
        ["Company:", user_info.get('company', 'N/A')],
        ["Email:", user_info.get('email', 'N/A')],
        ["Industry:", user_info.get('industry', 'N/A') if user_info.get('industry') else 'Not specified'],
    ]

    user_table = Table(user_data, colWidths=[1.5*inch, 4*inch])
    user_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0066CC')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(user_table)
    elements.append(Spacer(1, 0.4*inch))

    # Top Matches Section
    elements.append(Paragraph("Your Top 3 Brisbane Delegate Matches", heading_style))
    elements.append(Spacer(1, 0.2*inch))

    # Generate match cards
    for i, match in enumerate(matches, 1):
        # Match header box with rank and score
        match_header_data = [[
            f"RANK #{match['rank']}",
            f"{match['score']}% MATCH"
        ]]

        match_header_table = Table(match_header_data, colWidths=[4*inch, 2*inch])
        match_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#0066CC')),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#00CC66')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(match_header_table)

        # Delegate information
        delegate_info_data = [
            ["Name:", match['name']],
            ["Title:", match['title']],
            ["Company:", match['company']],
            ["Sector:", match['sector']],
            ["Email:", match['email']],
            ["Phone:", match['phone']],
        ]

        delegate_info_table = Table(delegate_info_data, colWidths=[1.2*inch, 4.8*inch])
        delegate_info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0066CC')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#CCCCCC')),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ]))

        elements.append(delegate_info_table)
        elements.append(Spacer(1, 0.15*inch))

        # Objectives
        elements.append(Paragraph("<b>Delegate Objectives:</b>", body_style))
        objectives_text = match['objectives'][:300] + "..." if len(match['objectives']) > 300 else match['objectives']
        elements.append(Paragraph(objectives_text, body_style))
        elements.append(Spacer(1, 0.1*inch))

        # Interested Sectors
        interested_sectors = ", ".join(match['interested_sectors'][:3])
        elements.append(Paragraph(f"<b>Interested Sectors:</b> {interested_sectors}", body_style))
        elements.append(Spacer(1, 0.15*inch))

        # Synergy Analysis
        elements.append(Paragraph("<b>AI Synergy Analysis:</b>", heading_style))

        # Parse and format the synergy analysis (it's in markdown format)
        synergy_lines = match['synergy_analysis'].split('\n')
        for line in synergy_lines:
            if line.strip():
                # Convert markdown bold to reportlab bold (proper handling)
                formatted_line = line
                # Replace ** pairs with proper <b> tags
                bold_count = formatted_line.count('**')
                if bold_count >= 2:
                    # Replace first ** with <b>, second with </b>, and so on
                    parts = formatted_line.split('**')
                    formatted_line = ''
                    for i, part in enumerate(parts):
                        if i % 2 == 0:
                            formatted_line += part
                        else:
                            formatted_line += f'<b>{part}</b>'

                # Escape any remaining special characters
                formatted_line = formatted_line.replace('&', '&amp;')

                try:
                    elements.append(Paragraph(formatted_line, body_style))
                except Exception as e:
                    # Fallback: add as plain text without formatting
                    print(f"[PDF WARNING] Could not format line, using plain text: {line[:50]}")
                    plain_line = line.replace('**', '').replace('<', '').replace('>', '')
                    elements.append(Paragraph(plain_line, body_style))

        # Add page break between matches (except for the last one)
        if i < len(matches):
            elements.append(Spacer(1, 0.3*inch))
            elements.append(PageBreak())

    # Footer section
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        "<b>Next Steps:</b>",
        heading_style
    ))

    next_steps = [
        "1. Review the synergy analysis for each match to identify collaboration opportunities",
        "2. Reach out to delegates via email to introduce yourself and your organization",
        "3. Schedule meetings during the Boldly Brisbane Forum or APCS 2025 events",
        "4. Prepare talking points based on the recommended topics in each analysis",
        "5. Follow up with Brisbane City Council for additional delegate introductions"
    ]

    for step in next_steps:
        elements.append(Paragraph(step, body_style))

    elements.append(Spacer(1, 0.4*inch))

    # Footer
    footer_text = f"""
    <para align=center>
    <b>Brisbane Business Bridge AI</b><br/>
    Powered by Rico Engineering Services RES FZ-LLC<br/>
    <font size=8 color="#666666">
    Connecting Cities, Empowering Business<br/>
    © {datetime.now().year} Rico Engineering Services. All Rights Reserved.<br/>
    For Brisbane City Council - Boldly Brisbane Forum & APCS 2025
    </font>
    </para>
    """

    elements.append(Paragraph(footer_text, small_style))

    # Build PDF
    doc.build(elements)

    # Get PDF bytes
    buffer.seek(0)
    return buffer
