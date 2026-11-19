#!/usr/bin/env python3
"""Draw the 19 November 2026 world-news front page (1024x1024).

Deterministic: no randomness, no clock, no network. Same input -> same bytes.
Run: python3 draw.py  -> writes entry.png next to this file.

Design: newspaper front page. Masthead with the date as the largest type,
headline band on the Shenzhen trilateral summit, 2x3 grid of the day's other
stories, a ticker of second-tier items, footer line. All text is drawn with
PIL (no AI image generation) so every letter is pixel-exact.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

PAPER = (247, 242, 231)
INK = (22, 22, 26)
MUTED = (107, 107, 96)
RED = (185, 28, 28)
CARD = (255, 254, 250)
BORDER = (216, 210, 195)
DARK = (22, 22, 26)
AMBER = (245, 158, 11)
SKY = (46, 58, 77)
SKY2 = (70, 88, 110)

DEJAVU = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(DEJAVU, "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(DEJAVU, "DejaVuSans-Bold.ttf")
SANS = os.path.join(DEJAVU, "DejaVuSans.ttf")

# Panel copy. ICJ lines are the "verdict due today" version: the court reads
# its judgment at 17:00 Beijing time, after this file was first written. If
# the outcome is known before the final render, update ICJ_TITLE / ICJ_FACT
# to the outcome (see prep file) and re-render.
ICJ_TITLE = "WORLD COURT RULES TODAY"
ICJ_FACT = "Verdict due on Myanmar genocide case"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(path, text, max_w, start, minimum=10):
    """Largest font size (<= start) at which text fits max_w."""
    size = start
    while size > minimum:
        f = ImageFont.truetype(path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 1
    return ImageFont.truetype(path, minimum)


def wrap(d, text, f, max_w):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_tracked(d, cx, y, text, f, fill, tracking=4):
    """Draw text centred on cx with letter tracking."""
    widths = [f.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=f, fill=fill)
        x += w + tracking


def double_rule(d, y):
    d.line([(16, y), (W - 16, y)], fill=INK, width=3)
    d.line([(16, y + 5), (W - 16, y + 5)], fill=INK, width=1)


# ---- small flat icons, drawn in a 40x40 box at (x, y) ----
def icon_scales(d, x, y, c):
    cx = x + 20
    d.line([(cx, y + 4), (cx, y + 32)], fill=c, width=3)
    d.line([(x + 4, y + 10), (x + 36, y + 10)], fill=c, width=3)
    d.line([(x + 9, y + 10), (x + 9, y + 18)], fill=c, width=2)
    d.line([(x + 31, y + 10), (x + 31, y + 18)], fill=c, width=2)
    d.polygon([(x + 2, y + 26), (x + 16, y + 26), (x + 9, y + 18)], fill=c)
    d.polygon([(x + 24, y + 26), (x + 38, y + 26), (x + 31, y + 18)], fill=c)
    d.rectangle([cx - 8, y + 32, cx + 8, y + 36], fill=c)


def icon_chip(d, x, y, c):
    d.rounded_rectangle([x + 8, y + 8, x + 32, y + 32], radius=4, fill=c)
    d.rectangle([x + 15, y + 15, x + 25, y + 25], fill=PAPER)
    for i in range(3):
        yy = y + 12 + i * 8
        d.line([(x + 2, yy), (x + 8, yy)], fill=c, width=2)
        d.line([(x + 32, yy), (x + 38, yy)], fill=c, width=2)
        xx = x + 12 + i * 8
        d.line([(xx, y + 2), (xx, y + 8)], fill=c, width=2)
        d.line([(xx, y + 32), (xx, y + 38)], fill=c, width=2)


def icon_bridge(d, x, y, c):
    d.line([(x + 4, y + 30), (x + 36, y + 30)], fill=c, width=3)
    d.line([(x + 10, y + 8), (x + 10, y + 30)], fill=c, width=3)
    d.line([(x + 30, y + 8), (x + 30, y + 30)], fill=c, width=3)
    d.arc([x + 8, y + 12, x + 32, y + 34], start=180, end=360, fill=c, width=2)
    d.line([(x + 4, y + 34), (x + 36, y + 34)], fill=c, width=2)


def icon_flame(d, x, y, c):
    d.polygon(
        [
            (x + 20, y + 2),
            (x + 28, y + 14),
            (x + 34, y + 12),
            (x + 36, y + 24),
            (x + 28, y + 36),
            (x + 12, y + 36),
            (x + 4, y + 24),
            (x + 10, y + 14),
        ],
        fill=c,
    )
    d.polygon(
        [(x + 20, y + 18), (x + 25, y + 26), (x + 20, y + 32), (x + 15, y + 26)],
        fill=PAPER,
    )


def icon_crossing(d, x, y, c):
    # a truce line (yellow) with an arrow crossing over it
    d.line([(x + 2, y + 30), (x + 38, y + 30)], fill=(214, 158, 46), width=5)
    d.line([(x + 6, y + 14), (x + 30, y + 14)], fill=c, width=3)
    d.polygon([(x + 30, y + 14), (x + 22, y + 9), (x + 22, y + 19)], fill=c)
    d.line([(x + 10, y + 14), (x + 10, y + 30)], fill=c, width=2)


def icon_drone(d, x, y, c):
    d.rectangle([x + 15, y + 15, x + 25, y + 25], fill=c)
    for cx, cy in [(x + 8, y + 8), (x + 32, y + 8), (x + 8, y + 32), (x + 32, y + 32)]:
        d.line([(x + 20, y + 20), (cx, cy)], fill=c, width=2)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], outline=c, width=2)


def draw_skyline(d, x, y, w, h):
    """Shenzhen skyline silhouette with three small flags."""
    base = y + h
    heights = [78, 128, 96, 158, 118, 84, 138, 104]
    bw = 34
    gap = 5
    cx = x
    for ht in heights:
        d.rectangle([cx, base - ht, cx + bw, base], fill=SKY)
        # lit windows, fixed pattern
        for wy in range(base - ht + 10, base - 8, 18):
            for wx in (cx + 7, cx + 19):
                if (wx + wy) % 36 < 18:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=AMBER)
        cx += bw + gap
    # three flag poles with small flags above the tallest towers
    for px, fc in [(x + 52, RED), (x + 150, (30, 80, 160)), (x + 252, (230, 230, 225))]:
        d.line([(px, base - 158), (px, base - 196)], fill=INK, width=2)
        d.polygon([(px, base - 196), (px + 22, base - 190), (px, base - 184)], fill=fc)


def draw_masthead(d):
    draw_tracked(d, W // 2, 12, "THE WORLD IN ONE DAY", font(SANS_B, 19), INK, tracking=5)
    f_date = fit_font(SERIF_B, "THURSDAY \u00b7 19 NOVEMBER 2026", 980, 46)
    dw = f_date.getlength("THURSDAY \u00b7 19 NOVEMBER 2026")
    d.text(((W - dw) / 2, 34), "THURSDAY \u00b7 19 NOVEMBER 2026", font=f_date, fill=INK)
    f_sub = font(SANS, 20)
    sub = "Seven stories that defined the day"
    d.text(((W - f_sub.getlength(sub)) / 2, 88), sub, font=f_sub, fill=MUTED)
    double_rule(d, 114)


def draw_headline(d):
    # illustration, left
    draw_skyline(d, 24, 138, 300, 210)
    # text, right
    tx = 368
    d.text((tx, 134), "SHENZHEN \u2014 APEC", font=font(SANS_B, 20), fill=RED)
    d.text((tx, 162), "TRUMP, XI &", font=font(SERIF_B, 62), fill=INK)
    d.text((tx, 228), "PUTIN MEET", font=font(SERIF_B, 62), fill=INK)
    d.text((tx, 304), "First-ever three-way summit convenes", font=font(SANS, 23), fill=INK)
    d.text(
        (tx, 334),
        "Nuclear arms, Ukraine, Iran on agenda",
        font=font(SANS, 23),
        fill=MUTED,
    )
    double_rule(d, 364)


def draw_cell(d, x, y, w, h, accent, eyebrow, title, fact, icon):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=BORDER)
    d.rectangle([x, y, x + w, y + 5], fill=accent)
    icon(d, x + 16, y + 16, accent)
    d.text((x + 66, y + 26), eyebrow, font=font(SANS_B, 16), fill=RED)
    # title: shrink until it wraps to at most 2 lines (never drop a word)
    f_title = None
    lines = []
    for size in (27, 25, 23, 21):
        f_title = font(SANS_B, size)
        lines = wrap(d, title, f_title, w - 32)
        if len(lines) <= 2:
            break
    ty = y + 70
    for ln in lines[:2]:
        d.text((x + 16, ty), ln, font=f_title, fill=INK)
        ty += 33
    f_fact = font(SANS, 19)
    flines = wrap(d, fact, f_fact, w - 32)
    fy = y + 146
    for ln in flines[:2]:
        d.text((x + 16, fy), ln, font=f_fact, fill=(51, 51, 51))
        fy += 24


def draw_grid(d):
    cells = [
        ("THE HAGUE", ICJ_TITLE, ICJ_FACT, icon_scales, (31, 78, 121)),
        ("MARKETS", "ANTHROPIC DEBUTS AT $83", "Record $81B IPO; valued near $1.5T", icon_chip, (180, 83, 9)),
        ("UKRAINE", "KERCH BRIDGE HIT AGAIN", "Third strike in a week halts rail", icon_bridge, (14, 116, 144)),
        ("DHAKA", "BANGLADESH IN TURMOIL", "Yunus home torched; violence in 28 districts", icon_flame, RED),
        ("GAZA", "ISRAEL CROSSES 'YELLOW LINE'", "Ground push past truce line; Hamas protests", icon_crossing, (51, 65, 81)),
        ("THE GULF", "NETANYAHU URGES IRAN STRIKES", "Urges US to join 4-7 day air war; no decision", icon_drone, (22, 101, 52)),
    ]
    xs = [16, 352, 688]
    ys = [380, 628]
    cw, ch = 320, 244
    for i, (eb, ti, fa, ic, ac) in enumerate(cells):
        draw_cell(d, xs[i % 3], ys[i // 3], cw, ch, ac, eb, ti, fa, ic)
    double_rule(d, 880)


def draw_ticker(d):
    d.rectangle([0, 888, W, 948], fill=DARK)
    text = "ALSO TODAY: \u20ac45B EU loan for Ukraine \u00b7 US\u2013Venezuela defence pact \u00b7 COP31 deadlocked"
    f = fit_font(SANS_B, text, 992, 20)
    tw = f.getlength(text)
    d.text(((W - tw) / 2, 908), text, font=f, fill=(247, 242, 231))
    # amber label: redraw the label part in amber on top
    label = "ALSO TODAY:"
    d.text(((W - tw) / 2, 908), label, font=f, fill=AMBER)


def draw_footer(d):
    f = font(SANS, 16)
    text = "All events reported 19 Nov 2026"
    d.text(((W - f.getlength(text)) / 2, 972), text, font=f, fill=MUTED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_headline(d)
    draw_grid(d)
    draw_ticker(d)
    draw_footer(d)
    img.save(OUT, format="PNG")
    size = os.path.getsize(OUT)
    print(f"wrote {OUT} ({size} bytes)")
    assert size <= 1024 * 1024, "image over 1 MiB"
    assert img.size == (1024, 1024)


if __name__ == "__main__":
    main()
