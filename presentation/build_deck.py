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
    add_text(s, 0.8, 1.12, 6.2, 0.85, "Stopped.", 44, WHITE, True)
    add_text(s, 0.8, 1.95, 6.2, 0.85, "Impounded.", 44, WHITE, True)
    add_text(s, 0.8, 2.78, 6.2, 0.85, "Unheard.", 44, GOLD, True)
    add_text(
        s,
        0.8,
        3.85,
        6.0,
        1.25,
        "A boda boda rider's bike is taken. The 48-hour court deadline passes.\nLegalBridge gives him the first sourced step — in Luganda, on any phone.",
        15,
        RGBColor(222, 226, 235),
        spacing=1.15,
    )
    add_rect(s, 0.8, 5.5, 3.2, 0.55, PURPLE, rounded=True)
    add_text(s, 1.0, 5.62, 2.8, 0.3, "LIVE · 25 NOV 2026", 12, WHITE, True, align=PP_ALIGN.CENTER)
    add_image(s, "03-boda.png", 7.25, 1.05, 5.25, 2.25)
    add_image(s, "06-voice.png", 7.25, 3.55, 5.25, 2.25)
    add_text(s, 7.25, 6.15, 5.25, 0.35, "legalbridge-app-free.onrender.com", 13, WHITE, align=PP_ALIGN.CENTER)
    set_notes(
        s,
        "0:30 — Open with one rider, not a statistics lecture: he is waved down, the bike is loaded onto a pickup, and no one tells him when he will see a court. The Constitution gives him 48 hours. Tell judges the screenshots are from the live app, not a mock-up.",
    )

    # 2 — Problem
    s = new_slide(prs)
    add_bg(s, OFFWHITE)
    add_header(s, "The roadside becomes the first court.", "01 · The rider's problem")
    add_rect(s, 0.7, 1.45, 6.15, 4.9, WHITE, LINE, rounded=True)
    add_rect(s, 0.7, 1.45, 0.10, 4.9, PURPLE)
    add_text(s, 1.05, 1.7, 5.5, 0.3, "THE 5:40PM TEST", 12, PURPLE, True)
    add_image(s, "10-police-operation.jpg", 0.95, 2.05, 5.65, 2.75, border=False)
    add_text(
        s,
        0.95,
        4.82,
        5.65,
        0.3,
        "Police stop riders during a Kampala operation, 8 Nov 2022. PHOTO/ISAAC KASAMANI · DAILY MONITOR",
        8.5,
        MUTED,
    )
    add_text(
        s,
        1.05,
        5.2,
        5.45,
        1.0,
        "No receipt. No court date.\nArticle 23 says 48 hours. For thousands, that never happens.",
        15,
        INK,
        True,
        spacing=1.12,
    )

    stats = [
        ("12,217", "motorcycles impounded nationwide in six days (7–12 Nov 2022); 10,167 penalty tickets and 2,050 still at stations."),
        ("787", "riders stopped in one week in July 2024 over helmets and reflective jackets; police said operations would continue."),
        ("37,188", "people in pre-trial detention in Aug 2026 — 44.9% of all prisoners; prisons at 353% of capacity."),
        ("10.3%", "of detainees interviewed were boda riders; 65% had spent more than six months on remand without trial."),
    ]
    for i, (big, label) in enumerate(stats):
        y = 1.45 + i * 1.24
        add_rect(s, 7.15, y, 5.48, 1.08, WHITE, LINE, rounded=True)
        add_text(s, 7.4, y + 0.10, 4.95, 0.4, big, 22, PURPLE, True)
        add_text(s, 7.4, y + 0.52, 4.95, 0.5, label, 10.2, INK, spacing=1.02)
    add_footer(
        s,
        2,
        "Sources: The Source/Daily Monitor (Nov 2022); Uganda Police Force (15 Jul 2024); World Prison Brief (Aug 2026); ASF/New Vision (29 Oct 2026).",
    )
    set_notes(
        s,
        "1:30 — Start with the photograph: it shows police stopping riders in Kampala in Nov 2022, not an illustration. Police reported 12,217 motorcycles impounded in six days, with 2,050 still at stations; 787 riders were stopped in one week in Jul 2024. No official national daily arrest count is published, so we use these documented operations rather than invent one. World Prison Brief shows 37,188 people on remand in Aug 2026 (44.9%), and the ASF study found 10.3% of interviewed detainees were boda riders, with 65% over six months on remand.",
    )

    # 3 — Gap
    s = new_slide(prs)
    add_bg(s, OFFWHITE)
    add_header(s, "The law is clear. The first step is not.", "02 · Why riders stay stuck")
    cols = [
        (
            "48 hours is the rule",
            "Article 23 requires a person to be brought to court within 48 hours of arrest. Courts have held that detention beyond 48 hours is false imprisonment.\n\nA rider on the roadside rarely knows this.",
            PURPLE,
        ),
        (
            "The bike becomes the proof",
            "Police say impounded motorcycles are released only on proof of ownership and after checking they are not linked to crime. Bikes with no case sit at stations.\n\nA court once awarded UGX 225m over an unlawful impoundment.",
            TEAL,
        ),
        (
            "Bail is known but unused",
            "In the ASF study, two-thirds of detainees knew about bail — only 7% applied. 65% had been on remand for more than six months.\n\nKnowledge, not guilt, is the missing step.",
            GOLD,
        ),
    ]
    for i, (title, body, color) in enumerate(cols):
        x = 0.7 + i * 4.08
        add_rect(s, x, 1.5, 3.78, 3.9, WHITE, LINE, rounded=True)
        add_rect(s, x, 1.5, 3.78, 0.10, color)
        add_text(s, x + 0.25, 1.8, 3.3, 0.5, title, 16, NAVY, True)
        if i == 1:
            add_image(s, "11-impounded-motorcycles.jpg", x + 0.25, 2.38, 3.3, 2.2, border=False)
            add_text(
                s,
                x + 0.25,
                4.62,
                3.3,
                0.42,
                "Impounded motorcycles at Kampala Central Police Station, Jul 2024. PHOTO | STEPHEN OTAGE · DAILY MONITOR",
                8.2,
                MUTED,
                spacing=1.0,
            )
            add_text(s, x + 0.25, 5.06, 3.3, 0.3, "Police say: proof of ownership required.", 10.5, INK, True)
        else:
            add_text(s, x + 0.25, 2.45, 3.3, 2.6, body, 12.2, INK, spacing=1.1)
    add_rect(s, 0.7, 5.7, 11.93, 0.85, NAVY, rounded=True)
    add_text(
        s,
        1.0,
        5.9,
        11.3,
        0.45,
        "A rider does not need a law degree. He needs to know what to do before 48 hours run out.",
        17,
        WHITE,
        True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(
        s,
        3,
        "Sources: Constitution of Uganda Arts 23 & 28 (ULII); ULII false-imprisonment decisions; Uganda Police Force (Jul 2024); Business Focus (25 Jun 2021); ASF/New Vision (2026).",
    )
    set_notes(
        s,
        "1:00 — The photo is real: motorcycles parked at Kampala Central Police Station in Jul 2024, with no case under inquiry, waiting for owners with proof. The High Court once awarded UGX 225m over an unlawful impoundment. The Constitution and courts are clear, but the practical pathway is not: ownership proof, no receipt, no date, bail procedures unknown. We are not accusing any rider of theft or replacing lawyers — we are closing the knowledge gap in the first 48 hours.",
    )

    # 4 — Solution
    s = new_slide(prs)
    add_bg(s, WHITE)
    add_header(s, "The first step, in his language, on his phone.", "03 · The solution")
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
            "Know My Rights — what a stop, a seizure and the 48-hour rule actually mean.",
            "Understand documents — read an EPS ticket or impound note in plain language.",
            "Ask — “Can they keep my bike? What do I do tonight?” with sourced answers.",
            "Speak or dial — Luganda voice and USSD on any phone, no data needed.",
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
        "1:00 — Point at the screenshots and name the four capabilities. The key promise: a sourced answer and a practical next action, not a guess and not an invented phone number. Judges can scan the QR code to try it after the session.",
    )

    # 5 — Flow
    s = new_slide(prs)
    add_bg(s, OFFWHITE)
    add_header(s, "From roadside panic to a plan in four steps.", "04 · Demo flow")
    steps = [
        ("1", "He is stopped", "Bike taken, no date", "03-boda.png"),
        ("2", "He checks rights", "48-hour rule, EN / LG", "02-rights.png"),
        ("3", "He reads the paper", "EPS or impound note", "08-upload.png"),
        ("4", "He finds help", "Legal aid or USSD", "07-legal-help.png"),
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
        "Every answer points to a source or a next action — never an invented station, contact or bail figure.",
        13,
        WHITE,
        True,
        align=PP_ALIGN.CENTER,
    )
    add_footer(s, 5, "Demo cue: open Know My Rights, switch English ↔ Luganda, upload a notice, then dial *384*0#.")
    set_notes(
        s,
        "1:30 — Live demo slide. Start at Know My Rights, switch to Luganda, show a document upload, then ask a question. If time allows, show the USSD code on a phone. Keep returning to: sourced answer, practical next step.",
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
            "Article 23 (48 hours) and Article 28 (fair hearing) cited from ULII.",
            "Rider and vendor rights guides authored in English and Luganda from published Ugandan materials.",
            "No invented police stations, bail amounts, contacts or legal claims.",
            "Runyankore, Acholi and Lugbara are honest drafts that fall back to English.",
            "Every answer carries a “legal information, not legal advice” disclaimer.",
        ],
        13,
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
            "USSD *384*0# works on basic and feature phones with no mobile data.",
            "GSMA: USSD needs no app and works across GSM networks.",
            "Web, phone and USSD are one product, not three disconnected pilots.",
        ],
        13,
        INK,
        8,
    )
    add_footer(
        s,
        6,
        "Sources: Constitution of Uganda Arts 23 & 28 (ULII); GSMA “Low Tech, High Impact”; UN SDG 16.3.3 metadata.",
    )
    set_notes(
        s,
        "0:45 — Judges ask how we prevented hallucination. Our answer: the guides are authored, sourced and reviewed; the AI explains those extracts rather than inventing law; unsupported languages fall back to English; and we never name a station, contact or bail figure that we cannot source.",
    )

    # 7 — Impact / ask
    s = new_slide(prs)
    add_bg(s, NAVY)
    add_rect(s, 0, 0, 0.18, 7.5, PURPLE)
    add_text(s, 0.8, 0.45, 11.8, 0.3, "06 · What we ask you to see", 11, GOLD, True)
    add_text(s, 0.8, 0.85, 11.8, 0.7, "A working bridge, not a slideware idea.", 31, WHITE, True)

    proofs = [
        ("WORKING PRODUCT", "Live web app and health-checked API; screenshots are real, not a Figma mock-up."),
        ("EVIDENCE-LED", "48-hour rule, remand data and impound figures cited to ULII, UPF, WPB and ASF."),
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
        "Knowledge of the 48-hour rule · % who complete a next step · source-click rate · escalation to legal aid",
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
        "0:45 — Separate proof from promise: the product is live and sourced; outcomes are what a supervised pilot will measure. Ask for partnership with legal-aid organisations and the Uganda Human Rights Commission, then invite judges to scan the QR. Reserve remaining time for questions.",
    )

    prs.save(OUT)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    build()
