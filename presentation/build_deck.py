"""Build the LegalBridge judge presentation deck.

Run: python presentation/build_deck.py
Output: presentation/LegalBridge_Judge_Deck.pptx
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT = ROOT / "LegalBridge_Judge_Deck.pptx"

NAVY = RGBColor(18, 24, 38)
PURPLE = RGBColor(146, 47, 124)
PURPLE_LIGHT = RGBColor(244, 229, 240)
TEAL = RGBColor(23, 145, 146)
GOLD = RGBColor(226, 169, 61)
WHITE = RGBColor(255, 255, 255)
OFFWHITE = RGBColor(248, 247, 250)
INK = RGBColor(31, 36, 48)
MUTED = RGBColor(105, 112, 128)
LINE = RGBColor(220, 222, 229)

FONT = "Arial"


def add_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, x, y, w, h, fill, line=None, rounded=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    return shape


def add_text(
    slide,
    x,
    y,
    w,
    h,
    text,
    size=16,
    color=INK,
    bold=False,
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.TOP,
    font=FONT,
    margin=0.0,
    spacing=1.0,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = align
        p.font.name = font
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = color
        p.line_spacing = spacing
    return box


def add_bullets(slide, x, y, w, h, items, size=14, color=INK, gap=6):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "•  " + item
        p.font.name = FONT
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.space_after = Pt(gap)
        p.line_spacing = 1.05
    return box


def add_link(slide, x, y, w, h, label, url, size=10, color=TEAL):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = label
    p.font.name = FONT
    p.font.size = Pt(size)
    p.font.color.rgb = color
    run = p.runs[0]
    run.hyperlink.address = url
    return box


def add_image(slide, name, x, y, w, h, border=True):
    """Fit an image inside a box, preserving aspect ratio."""
    path = ASSETS / name
    from PIL import Image

    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    px = x + (w - dw) / 2
    py = y + (h - dh) / 2
    if border:
        add_rect(slide, px - 0.05, py - 0.05, dw + 0.10, dh + 0.10, LINE, rounded=True)
    slide.shapes.add_picture(str(path), Inches(px), Inches(py), Inches(dw), Inches(dh))
    return px, py, dw, dh


def add_header(slide, title, kicker=None):
    add_rect(slide, 0, 0, 13.333, 0.12, PURPLE)
    if kicker:
        add_text(slide, 0.7, 0.28, 11.9, 0.25, kicker.upper(), 10, PURPLE, True)
    add_text(slide, 0.7, 0.55, 11.9, 0.65, title, 29, NAVY, True)


def add_footer(slide, num, source=None):
    add_rect(slide, 0.7, 7.02, 11.9, 0.012, LINE)
    if source:
        add_text(slide, 0.7, 7.08, 10.9, 0.28, source, 8.5, MUTED)
    add_text(slide, 12.2, 7.08, 0.45, 0.28, str(num), 9, MUTED, align=PP_ALIGN.RIGHT)


def set_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 1 — Title
    s = new_slide(prs)
    add_bg(s, NAVY)
    add_rect(s, 0, 0, 0.18, 7.5, PURPLE)
    add_text(s, 0.8, 0.65, 6.2, 0.3, "LEGALBRIDGE · JUDGE PRESENTATION", 11, GOLD, True)
    add_text(s, 0.8, 1.15, 6.2, 1.0, "Know your rights.", 42, WHITE, True)
    add_text(s, 0.8, 2.05, 6.2, 1.0, "Get your next step.", 42, WHITE, True)
    add_text(s, 0.8, 2.95, 6.2, 0.8, "From any phone.", 42, GOLD, True)
    add_text(
        s,
        0.8,
        3.95,
        6.0,
        1.15,
        "A rights-and-legal-help companion for people in Uganda’s informal settlements — in English, Luganda and USSD.",
        17,
        RGBColor(222, 226, 235),
        spacing=1.15,
    )
    add_rect(s, 0.8, 5.45, 3.2, 0.55, PURPLE, rounded=True)
    add_text(s, 1.0, 5.57, 2.8, 0.3, "LIVE · 25 NOV 2026", 12, WHITE, True, align=PP_ALIGN.CENTER)
    add_image(s, "02-rights.png", 7.25, 1.05, 5.25, 2.25)
    add_image(s, "06-voice.png", 7.25, 3.55, 5.25, 2.25)
    add_text(s, 7.25, 6.15, 5.25, 0.35, "legalbridge-app-free.onrender.com", 13, WHITE, align=PP_ALIGN.CENTER)
    set_notes(
        s,
        "0:30 — Open with the promise, not the technology: a person with an eviction note at 5:40pm should not need a lawyer just to learn the first right step. Tell judges the app is live and the screenshots are from the real hosted product.",
    )

    # 2 — Problem
    s = new_slide(prs)
    add_bg(s, OFFWHITE)
    add_header(s, "A legal problem does not wait for office hours.", "01 · The problem")
    add_rect(s, 0.7, 1.45, 6.15, 4.9, WHITE, LINE, rounded=True)
    add_rect(s, 0.7, 1.45, 0.10, 4.9, PURPLE)
    add_text(s, 1.05, 1.75, 5.5, 0.35, "THE 5:40PM TEST", 12, PURPLE, True)
    add_text(
        s,
        1.05,
        2.2,
        5.45,
        3.4,
        "An eviction note is slipped under a door.\nCourt is closed. A lawyer is unaffordable.\nA relative sends a WhatsApp voice note.\n\nThe person still does not know:\nCan this happen? What do I do tonight?",
        19,
        INK,
        spacing=1.18,
    )
    add_text(s, 1.05, 5.9, 5.45, 0.3, "If the first step is unclear, the system has already failed.", 13, TEAL, True)

    stats = [
        ("126 / 142", "Uganda’s overall rank, WJP Rule of Law Index 2024; civil justice rank 115 / 142."),
        ("46,000+", "cases still pending, even as Uganda’s backlog fell from 26.3% to 24.2% (Judiciary, Oct 2025)."),
        ("SDG 16.3", "“Equal access to justice for all”; UN metadata names lack of knowledge, advice, distance and cost as barriers."),
    ]
    for i, (big, label) in enumerate(stats):
        y = 1.45 + i * 1.68
        add_rect(s, 7.15, y, 5.48, 1.42, WHITE, LINE, rounded=True)
        add_text(s, 7.42, y + 0.16, 4.9, 0.5, big, 25, PURPLE, True)
        add_text(s, 7.42, y + 0.68, 4.95, 0.62, label, 12.5, INK, spacing=1.05)
    add_footer(
        s,
        2,
        "Sources: WJP Rule of Law Index 2024 (Uganda); Judiciary of Uganda, 17 Oct 2025; UN SDG indicator 16.3.3 metadata.",
    )
    set_notes(
        s,
        "1:30 — Tell the story slowly. Then land the evidence: WJP 2024 places Uganda 126/142 overall and 115/142 on civil justice. The Judiciary reported over 46,000 pending cases in October 2025 even while backlog improved. UN SDG 16.3.3 explicitly lists lack of knowledge, legal advice, distance and cost as reasons people do not access dispute resolution. This is a first-step problem.",
    )

    # 3 — Gap
    s = new_slide(prs)
    add_bg(s, OFFWHITE)
    add_header(s, "The information exists. The bridge does not.", "02 · Why current options fail")
    cols = [
        (
            "The law is published",
            "Uganda’s Constitution guarantees a fair, speedy and public hearing (Art. 28), and statutes are published online.\n\nBut a person in crisis still asks: “Where do I start?”",
            PURPLE,
        ),
        (
            "Formal justice is slow",
            "With 46,000+ cases pending and civil justice ranked 115/142, the formal route is real but distant.\n\nDelay turns a small problem into an eviction.",
            TEAL,
        ),
        (
            "Digital help excludes many",
            "Smartphone ownership, data cost and digital literacy are barriers across emerging markets.\n\nUSSD reaches basic and feature phones with no app and no internet (GSMA).",
            GOLD,
        ),
    ]
    for i, (title, body, color) in enumerate(cols):
        x = 0.7 + i * 4.08
        add_rect(s, x, 1.5, 3.78, 3.9, WHITE, LINE, rounded=True)
        add_rect(s, x, 1.5, 3.78, 0.10, color)
        add_text(s, x + 0.25, 1.8, 3.3, 0.5, title, 17, NAVY, True)
        add_text(s, x + 0.25, 2.45, 3.3, 2.6, body, 13.5, INK, spacing=1.12)
    add_rect(s, 0.7, 5.7, 11.93, 0.85, NAVY, rounded=True)
    add_text(
        s,
        1.0,
        5.9,
        11.3,
        0.45,
        "The gap is not the absence of law. It is the absence of a clear, trusted, local-language first step.",
        18,
        WHITE,
        True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(
        s,
        3,
        "Sources: Constitution of Uganda Art. 28 (ULII); WJP 2024; Judiciary of Uganda 2025; GSMA mobile-for-development research.",
    )
    set_notes(
        s,
        "1:00 — Frame the gap as a bridge problem. We are not replacing courts or lawyers. We are making the first step intelligible. The Constitution already guarantees fair hearing; the Judiciary is working on backlog; GSMA shows USSD reaches people smartphones leave behind. LegalBridge sits between the person and those institutions.",
    )

    # 4 — Solution
    s = new_slide(prs)
    add_bg(s, WHITE)
    add_header(s, "One assistant. Three ways in. Verified sources.", "03 · The solution")
    add_image(s, "02-rights.png", 0.7, 1.45, 3.0, 1.95)
    add_image(s, "08-upload.png", 3.9, 1.45, 3.0, 1.95)
    add_image(s, "05-ask.png", 0.7, 3.65, 3.0, 1.95)
    add_image(s, "06-voice.png", 3.9, 3.65, 3.0, 1.95)

    add_rect(s, 7.25, 1.45, 5.38, 4.15, PURPLE_LIGHT, rounded=True)
    add_bullets(
        s,
        7.55,
        1.75,
        4.8,
        3.6,
        [
            "Know My Rights — rider and vendor guides in English and Luganda.",
            "Ask —plain-language answers grounded in verified legal extracts.",
            "Understand documents — photograph a notice and get a plain-language reading.",
            "Speak or dial — Luganda voice, plus USSD *384*0# for any phone.",
        ],
        14,
        INK,
        9,
    )
    add_rect(s, 7.25, 5.82, 5.38, 0.78, NAVY, rounded=True)
    add_text(s, 7.5, 5.98, 3.4, 0.35, "LIVE DEMO", 12, GOLD, True)
    add_text(s, 7.5, 6.25, 4.8, 0.25, "legalbridge-app-free.onrender.com", 11, WHITE)
    add_image(s, "app-qr.png", 11.62, 5.86, 0.68, 0.68, border=False)
    add_footer(s, 4, "All screens captured from the live hosted LegalBridge web app on 25 Nov 2026.")
    set_notes(
        s,
        "1:00 — Point at the screenshots and name the four capabilities. Emphasise that each answer carries a source link or a concrete next action. The QR code opens the live app for judges who want to try it after the session.",
    )

    # 5 — Flow
    s = new_slide(prs)
    add_bg(s, OFFWHITE)
    add_header(s, "From panic to a plan in four steps.", "04 · Demo flow")
    steps = [
        ("1", "Choose your reality", "Rider or vendor entry point", "03-boda.png"),
        ("2", "Read your rights", "Sourced guide, EN / LG", "02-rights.png"),
        ("3", "Explain or ask", "Document or free-text question", "08-upload.png"),
        ("4", "Get help", "Directory or USSD escalation", "07-legal-help.png"),
    ]
    for i, (num, title, sub, img) in enumerate(steps):
        x = 0.7 + i * 3.08
        add_rect(s, x, 1.5, 2.85, 4.75, WHITE, LINE, rounded=True)
        add_rect(s, x + 0.2, 1.75, 0.55, 0.55, PURPLE, rounded=True)
        add_text(s, x + 0.2, 1.84, 0.55, 0.3, num, 15, WHITE, True, align=PP_ALIGN.CENTER)
        add_text(s, x + 0.2, 2.5, 2.45, 0.5, title, 16, NAVY, True)
        add_text(s, x + 0.2, 3.02, 2.45, 0.45, sub, 12, MUTED)
        add_image(s, img, x + 0.18, 3.55, 2.48, 2.25, border=False)
    add_rect(s, 0.7, 6.45, 11.93, 0.42, TEAL, rounded=True)
    add_text(
        s,
        0.95,
        6.53,
        11.4,
        0.28,
        "Every answer points to a source or a next action — never an invented office or phone number.",
        13,
        WHITE,
        True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(s, 5, "Demo cue: open Know My Rights, switch English ↔ Luganda, upload a notice, then dial *384*0#.")
    set_notes(
        s,
        "1:30 — This is the live demo slide. Start at Know My Rights, switch to Luganda, show a document upload, then ask a question. If time allows, show the USSD code on a phone. Keep returning to the phrase: sourced answer, practical next step.",
    )

    # 6 — Trust
    s = new_slide(prs)
    add_bg(s, WHITE)
    add_header(s, "Built to be checked, not trusted blindly.", "05 · Research integrity & inclusion")
    add_rect(s, 0.7, 1.5, 5.85, 4.75, PURPLE_LIGHT, rounded=True)
    add_text(s, 1.0, 1.8, 5.2, 0.35, "SOURCE DISCIPLINE", 12, PURPLE, True)
    add_bullets(
        s,
        1.0,
        2.25,
        5.2,
        3.6,
        [
            "Rights guides authored in English and Luganda from published Ugandan legal materials.",
            "Official-document manifest links each guide to its source.",
            "Runyankore, Acholi and Lugbara are honest drafts that fall back to English.",
            "No invented district contacts, sections or legal claims.",
            "Every answer carries a “legal information, not legal advice” disclaimer.",
        ],
        13.5,
        INK,
        8,
    )
    add_rect(s, 6.85, 1.5, 5.78, 4.75, RGBColor(230, 246, 245), rounded=True)
    add_text(s, 7.15, 1.8, 5.2, 0.35, "INCLUSION BY DESIGN", 12, TEAL, True)
    add_bullets(
        s,
        7.15,
        2.25,
        5.15,
        3.6,
        [
            "English and Luganda are complete; other languages are clearly marked.",
            "Voice questions and spoken answers support Luganda users.",
            "USSD *384*0# works on basic and feature phones.",
            "GSMA: USSD needs no app, no mobile data and works across GSM networks.",
            "Web, phone and USSD are one product, not three disconnected pilots.",
        ],
        13.5,
        INK,
        8,
    )
    add_footer(
        s,
        6,
        "Sources: Constitution of Uganda Art. 28 (ULII); UN SDG 16.3.3; GSMA “Low Tech, High Impact” and USSD research.",
    )
    set_notes(
        s,
        "0:45 — Judges often ask how we prevented hallucination. Our answer: guides are authored, sourced and reviewed; the AI explains those extracts rather than inventing law; unsupported languages fall back to English. GSMA evidence supports the USSD choice for feature-phone reach.",
    )

    # 7 — Impact / ask
    s = new_slide(prs)
    add_bg(s, NAVY)
    add_rect(s, 0, 0, 0.18, 7.5, PURPLE)
    add_text(s, 0.8, 0.45, 11.8, 0.3, "06 · What we ask you to see", 11, GOLD, True)
    add_text(s, 0.8, 0.85, 11.8, 0.7, "A working bridge, not a slideware idea.", 31, WHITE, True)

    proofs = [
        ("WORKING PRODUCT", "Live web app and health-checked API; screenshots are real, not a Figma mock-up."),
        ("EVIDENCE-LED CONTENT", "Verified source manifest, bilingual guides and visible disclaimers."),
        ("REACH BEYOND SMARTPHONES", "Web, Luganda voice and USSD for basic phones."),
    ]
    for i, (title, body) in enumerate(proofs):
        x = 0.8 + i * 4.05
        add_rect(s, x, 1.85, 3.75, 1.75, RGBColor(30, 38, 56), rounded=True)
        add_text(s, x + 0.2, 2.05, 3.35, 0.3, title, 11, GOLD, True)
        add_text(s, x + 0.2, 2.45, 3.35, 0.9, body, 12.5, WHITE, spacing=1.1)

    add_rect(s, 0.8, 3.95, 11.75, 1.35, RGBColor(30, 38, 56), rounded=True)
    add_text(s, 1.05, 4.15, 11.2, 0.3, "WHAT WE WILL MEASURE IN A SUPERVISED PILOT", 11, GOLD, True)
    add_text(
        s,
        1.05,
        4.55,
        11.2,
        0.55,
        "Time to first useful answer · % who complete a next step · language coverage · source-click rate · escalation to legal aid",
        14,
        WHITE,
    )

    add_rect(s, 0.8, 5.65, 11.75, 1.05, PURPLE, rounded=True)
    add_text(s, 1.05, 5.82, 8.9, 0.35, "Try it now: legalbridge-app-free.onrender.com", 17, WHITE, True)
    add_text(s, 1.05, 6.2, 8.9, 0.28, "USSD: *384*0#   ·   API health: /healthz", 12, RGBColor(244, 229, 240))
    add_image(s, "app-qr.png", 11.05, 5.78, 0.78, 0.78, border=False)
    add_text(s, 0.8, 7.05, 10.9, 0.25, "Facts checked 25 Nov 2026. Full source list in presentation/SOURCES.md.", 8.5, RGBColor(180, 188, 202))
    add_text(s, 12.2, 7.05, 0.45, 0.25, "7", 9, RGBColor(180, 188, 202), align=PP_ALIGN.RIGHT)
    set_notes(
        s,
        "0:45 — Close by separating proof from promise: the product is live and sourced; the outcomes are what a supervised pilot will measure. Ask for partnership with legal-aid organisations and the Uganda Human Rights Commission, then invite judges to scan the QR code. Reserve remaining time for questions.",
    )

    prs.save(OUT)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    build()
