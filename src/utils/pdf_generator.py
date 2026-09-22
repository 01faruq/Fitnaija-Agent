"""Clean, bulletproof ReportLab PDF generator for FitNaija+.

Features:
- Robust ASCII / Latin-1 sanitization to prevent Unicode missing-glyph errors.
- Translates Markdown headings and formatting into valid ReportLab XML tags.
- Executive clinical styling with FitNaija+ green palette (#1E4620, #2E7D32).
- Formatted Biometric Summary card and structured plan sections.
"""

import io
import re
import html
import unicodedata
from typing import Optional, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Character substitution map for Unicode to ASCII
UNICODE_TO_ASCII_MAP = {
    "\u2018": "'",   # Left single quote
    "\u2019": "'",   # Right single quote
    "\u201a": ",",   # Single low-9 quote
    "\u201b": "'",   # Single high-reversed-9 quote
    "\u201c": '"',   # Left double quote
    "\u201d": '"',   # Right double quote
    "\u201e": '"',   # Double low-9 quote
    "\u2014": " - ", # Em dash
    "\u2013": " - ", # En dash
    "\u2026": "...", # Horizontal ellipsis
    "\u2022": "* ",  # Bullet
    "\u2023": "* ",  # Triangular bullet
    "\u25aa": "* ",  # Black small square
    "\u25ab": "* ",  # White small square
    "\u25cf": "* ",  # Black circle
    "\u2192": " -> ", # Right arrow
    "\u2190": " <- ", # Left arrow
    "\u2194": " <-> ",
    "\u2713": "[x]", # Checkmark
    "\u2714": "[x]", # Heavy checkmark
    "\u2717": "[ ]", # Ballot X
    "\u00d7": "x",   # Multiplication sign
    "\u00f7": "/",   # Division sign
    "\u2264": "<=",  # Less-than or equal to
    "\u2265": ">=",  # Greater-than or equal to
    "\u2248": "~",   # Almost equal to
    "\u00b1": "+/-", # Plus-minus
    "\u00b0": " deg", # Degree
    "\u00a0": " ",   # Non-breaking space
    "\u200b": "",    # Zero-width space
}

# Regex for emojis and high unicode symbols (surrogates & astral planes)
EMOJI_PATTERN = re.compile(
    "["
    "\U00010000-\U0010ffff"  # Supplemental symbols, pictographs, emojis
    "\u2600-\u26ff"          # Miscellaneous symbols
    "\u2700-\u27bf"          # Dingbats
    "\ufe00-\ufe0f"          # Variation selectors
    "]+",
    flags=re.UNICODE
)


def sanitize_to_ascii(text: str) -> str:
    """Sanitize string to safe printable ASCII to prevent ReportLab missing-glyph crashes.
    
    1. Replaces known typographic Unicode punctuation with ASCII equivalents.
    2. Strips out emojis and decorative unicode symbols.
    3. Normalizes remaining accented characters via NFKD decomposition.
    4. Encodes to ASCII with replacement or stripping.
    """
    if not text:
        return ""

    # Replace known typographic unicode characters
    for uni_char, ascii_char in UNICODE_TO_ASCII_MAP.items():
        text = text.replace(uni_char, ascii_char)

    # Remove emojis and dingbats
    text = EMOJI_PATTERN.sub("", text)

    # Normalize unicode (decompose accented characters e.g. e + accent)
    text = unicodedata.normalize("NFKD", text)

    # Encode to ASCII, dropping any remaining non-encodable glyphs safely
    clean_bytes = text.encode("ascii", "ignore")
    return clean_bytes.decode("ascii")


def markdown_to_reportlab(text: str) -> str:
    """Convert safe text with light markdown to ReportLab Paragraph XML."""
    # First sanitize unicode characters
    safe = sanitize_to_ascii(text)

    # Escape HTML/XML entities
    safe = html.escape(safe)

    # Bold: **bold** -> <b>bold</b>
    safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)

    # Italic: *italic* -> <i>italic</i>
    safe = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", safe)

    # Replace newlines with break tags
    safe = safe.replace("\n", "<br/>")

    return safe


def build_pdf(
    raw_text: str,
    biometrics: Optional[Dict[str, Any]] = None,
    user_metadata: Optional[Dict[str, Any]] = None,
    user_name: Optional[str] = None
) -> io.BytesIO:
    """Generate a clean, beautifully styled PDF plan for FitNaija+.
    
    Args:
        raw_text: Markdown or plain text of the plan
        biometrics: Optional dictionary of computed biometrics (BMI, BMR, Caloric Target, etc.)
        user_metadata: Optional metadata (culture, goal, language)
        user_name: Optional client preferred name
        
    Returns:
        io.BytesIO: In-memory PDF buffer seeked to 0.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Resolve client name
    client_name = user_name or (biometrics.get("user_name") if biometrics else None) or "Faruq"

    # Custom FitNaija+ Palette Styles
    primary_color = colors.HexColor("#1E4620")   # Deep Forest Green
    secondary_color = colors.HexColor("#2E7D32") # Rich Leaf Green
    slate_dark = colors.HexColor("#2D3748")      # Dark Slate for body
    slate_light = colors.HexColor("#F0FDF4")     # Light Mint table background
    border_color = colors.HexColor("#86EFAC")    # Soft green border

    title_style = ParagraphStyle(
        "FitNaijaTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "FitNaijaSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=13,
        textColor=secondary_color,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        "FitNaijaH1",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4
    )

    h2_style = ParagraphStyle(
        "FitNaijaH2",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=secondary_color,
        spaceBefore=6,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        "FitNaijaBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=slate_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "FitNaijaBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=slate_dark,
        leftIndent=15,
        spaceAfter=3
    )

    story = []

    # Title & Branding Personalized for User
    story.append(Paragraph("FitNaija+ AI Health Engine", title_style))
    story.append(Paragraph(
        f"Personalized African Clinical Nutrition & Joint-Safe Mobility Plan &bull; Prepared for: <b>{sanitize_to_ascii(client_name)}</b>",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceBefore=0, spaceAfter=8))

    # Biometric Profile Table if available
    if biometrics:
        bmi = biometrics.get("bmi", "N/A")
        bmi_cat = biometrics.get("bmi_category", "")
        target_cal = biometrics.get("target_calories", "N/A")
        bmr = biometrics.get("bmr", "N/A")
        water = biometrics.get("water_target_liters", "N/A")
        goal = biometrics.get("goal", "Health Optimization")

        table_data = [
            [
                Paragraph(f"<b>Client:</b> {sanitize_to_ascii(client_name)}", body_style),
                Paragraph(f"<b>BMI:</b> {bmi} ({bmi_cat})", body_style),
                Paragraph(f"<b>BMR:</b> {bmr} kcal", body_style),
            ],
            [
                Paragraph(f"<b>Goal:</b> {sanitize_to_ascii(str(goal))}", body_style),
                Paragraph(f"<b>Daily Caloric Target:</b> ~{target_cal} kcal", body_style),
                Paragraph(f"<b>Daily Water Target:</b> {water} Liters", body_style),
            ]
        ]

        # Add Exercise Physiology row if metadata present
        eq_tier = (user_metadata.get("equipment_tier") if user_metadata else None) or biometrics.get("equipment_tier")
        hr_zone = (user_metadata.get("target_heart_rate_zone") if user_metadata else None) or biometrics.get("target_heart_rate_zone")
        burn_val = (user_metadata.get("est_calories_burned_per_session") if user_metadata else None) or biometrics.get("est_calories_burned_per_session")

        if eq_tier or hr_zone:
            table_data.append([
                Paragraph(f"<b>Equipment:</b> {sanitize_to_ascii(str(eq_tier or 'Home Workout'))}", body_style),
                Paragraph(f"<b>Zone 2 FatMax HR:</b> {sanitize_to_ascii(str(hr_zone or '112-131 bpm'))}", body_style),
                Paragraph(f"<b>Est. Session Burn:</b> ~{burn_val or 160} kcal", body_style),
            ])

        bio_table = Table(table_data, colWidths=[180, 180, 180])
        bio_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), slate_light),
            ("BOX", (0, 0), (-1, -1), 1, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(bio_table)
        story.append(Spacer(1, 10))

    # Parse raw plan text blocks safely
    paragraphs = raw_text.split("\n\n")
    for block in paragraphs:
        block = block.strip()
        if not block:
            continue

        # Handle headings
        if block.startswith("# "):
            clean_heading = block.lstrip("# ").strip()
            story.append(Paragraph(markdown_to_reportlab(clean_heading), h1_style))
        elif block.startswith("## "):
            clean_heading = block.lstrip("# ").strip()
            story.append(Paragraph(markdown_to_reportlab(clean_heading), h1_style))
        elif block.startswith("### "):
            clean_heading = block.lstrip("# ").strip()
            story.append(Paragraph(markdown_to_reportlab(clean_heading), h2_style))
        elif block.startswith("- ") or block.startswith("* "):
            # Bullet list block
            lines = block.split("\n")
            for line in lines:
                line_clean = line.strip().lstrip("-* ").strip()
                if line_clean:
                    story.append(Paragraph(f"&bull; {markdown_to_reportlab(line_clean)}", bullet_style))
        else:
            story.append(Paragraph(markdown_to_reportlab(block), body_style))
            story.append(Spacer(1, 4))

    # Footer notice with FAO/INFOODS citation
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=6, spaceAfter=6))
    
    citation_text = "Nutritional benchmarks formulated using the FAO/INFOODS West African Food Composition Table & FMOH Guidelines."
    story.append(Paragraph(f"<b>Nutritional Benchmark:</b> {sanitize_to_ascii(citation_text)}", subtitle_style))
    
    disclaimer = (
        "Clinical Disclaimer: FitNaija+ is an algorithmic preventative health engine. "
        "Consult your physician before beginning any new caloric deficit or physical exercise regimen."
    )
    story.append(Paragraph(f"<i>{sanitize_to_ascii(disclaimer)}</i>", subtitle_style))

    # Build document
    doc.build(story)
    buffer.seek(0)
    return buffer

