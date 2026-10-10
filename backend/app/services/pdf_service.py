"""One-page A4 PDF sales proposal via reportlab canvas.

Canvas (not auto-flowing Platypus) is used deliberately so output is ALWAYS a
single page: text is wrapped and truncated to fit fixed regions, and the page is
finished exactly once. Text is drawn as plain strings (no HTML interpreted).
"""

from __future__ import annotations

import io
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.schemas.proposal import ProposalContent

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
CONTENT_W = PAGE_W - 2 * MARGIN
BOTTOM = 16 * mm  # stop drawing below this; keeps everything on one page

ACCENT = (0.18, 0.33, 0.72)
INK = (0.12, 0.16, 0.22)
MUTED = (0.42, 0.46, 0.52)


def _wrap(c: canvas.Canvas, text: str, font: str, size: float, max_w: float) -> list[str]:
    words = str(text).split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if c.stringWidth(trial, font, size) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


class _Cursor:
    def __init__(self, c: canvas.Canvas):
        self.c = c
        self.y = PAGE_H - MARGIN

    def space(self, dy: float) -> None:
        self.y -= dy

    def room(self, needed: float = 10) -> bool:
        return self.y - needed > BOTTOM

    def text_block(
        self,
        text: str,
        size: float,
        *,
        font: str = "Helvetica",
        color=INK,
        leading: float | None = None,
        max_lines: int = 100,
        indent: float = 0,
    ) -> None:
        if not text or not self.room():
            return
        leading = leading or size + 2
        self.c.setFont(font, size)
        self.c.setFillColorRGB(*color)
        lines = _wrap(self.c, text, font, size, CONTENT_W - indent)
        for i, line in enumerate(lines):
            if i >= max_lines or not self.room(leading):
                # Mark truncation on the last drawn line.
                self.c.drawString(MARGIN + indent, self.y, line[:80].rstrip() + "…")
                return
            self.c.drawString(MARGIN + indent, self.y, line)
            self.y -= leading

    def heading(self, text: str) -> None:
        if not self.room(16):
            return
        self.space(4)
        self.c.setFont("Helvetica-Bold", 10)
        self.c.setFillColorRGB(*ACCENT)
        self.c.drawString(MARGIN, self.y, text.upper())
        self.y -= 13


def render_proposal_pdf(
    content: ProposalContent,
    *,
    reference_code: str,
    station_name: str,
    space_code: str,
    synthetic: bool = True,
) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(content.title)
    cur = _Cursor(c)

    # Top rule + reference/date
    c.setFillColorRGB(*ACCENT)
    c.rect(MARGIN, PAGE_H - MARGIN + 4, CONTENT_W, 3, fill=1, stroke=0)
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(*MUTED)
    c.drawRightString(
        PAGE_W - MARGIN, PAGE_H - MARGIN - 6, f"{reference_code}  ·  {date.today().isoformat()}"
    )

    cur.space(6)
    cur.text_block(content.title, 16, font="Helvetica-Bold", color=INK, leading=19, max_lines=2)
    cur.text_block(f"{station_name}  ·  Space {space_code}", 9.5, color=MUTED)
    cur.space(4)

    # Verified metrics strip
    if content.verified_metrics:
        cur.heading("Verified metrics (observed)")
        col_w = CONTENT_W / 3
        metrics = content.verified_metrics[:9]
        for row_start in range(0, len(metrics), 3):
            if not cur.room(26):
                break
            row = metrics[row_start : row_start + 3]
            for i, m in enumerate(row):
                x = MARGIN + i * col_w
                c.setFont("Helvetica", 7.5)
                c.setFillColorRGB(*MUTED)
                c.drawString(x, cur.y, m.label[:34])
                c.setFont("Helvetica-Bold", 10)
                c.setFillColorRGB(*INK)
                c.drawString(x, cur.y - 11, m.value[:28])
            cur.y -= 26

    cur.heading("Executive summary")
    cur.text_block(content.executive_summary, 9, max_lines=5)

    if content.location_highlights:
        cur.heading("Location highlights")
        for h in content.location_highlights[:5]:
            cur.text_block(f"•  {h}", 9, max_lines=2, indent=4)

    cur.heading("Commercial opportunity")
    cur.text_block(content.commercial_opportunity, 9, max_lines=5)

    cur.heading("Indicative pricing")
    cur.text_block(content.pricing_summary, 9, max_lines=4)

    if content.suggested_usage:
        cur.heading("Suggested usage")
        cur.text_block(content.suggested_usage, 9, max_lines=3)

    cur.heading("Next steps")
    cur.text_block(content.call_to_action, 9, max_lines=3)

    if content.assumptions_and_limitations:
        cur.heading("Assumptions & limitations")
        for a in content.assumptions_and_limitations[:6]:
            cur.text_block(f"•  {a}", 7.5, color=MUTED, max_lines=2, indent=4)

    # Footer disclaimer anchored near the bottom
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColorRGB(*MUTED)
    disclaimer = "Indicative proposal. Pricing is a model estimate, not a verified market rate."
    if synthetic:
        disclaimer += " Based on synthetic demonstration data."
    c.drawString(MARGIN, BOTTOM - 6, disclaimer[:150])

    c.showPage()  # exactly one page
    c.save()
    return buf.getvalue()
