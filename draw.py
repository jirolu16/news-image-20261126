#!/usr/bin/env python3
"""Draw the 26 November 2026 world-news front page.

A newspaper front-page collage, 1024x1024, drawn entirely with PIL
shapes and text. Fully deterministic: no randomness, no timestamps,
no network, no file reads beyond the system fonts. The output PNG is
byte-identical on every run.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---- palette -------------------------------------------------------
PAPER = (247, 241, 227)      # warm cream paper
NAVY = (20, 33, 61)         # masthead / footer band
GOLD = (252, 163, 17)       # masthead date, accents
CREAM = (247, 241, 227)     # masthead title text
CARD = (255, 253, 246)      # panel cards
INK = (20, 33, 61)          # headlines
SUB = (84, 80, 70)          # sublines
RED = (192, 57, 43)
DARK_RED = (122, 46, 46)
BLUE = (46, 134, 171)
MID_BLUE = (69, 123, 157)
LIGHT_BLUE = (127, 179, 213)
GREEN = (42, 157, 143)
DARK_GREEN = (77, 158, 87)
GREY = (138, 143, 152)
DARK_GREY = (90, 96, 106)
TAN = (217, 164, 65)
NIGHT = (13, 27, 62)
ORANGE = (230, 126, 34)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(d, text, font, max_w):
    """Greedy word wrap, measured with the real font. Returns lines."""
    lines = []
    cur = ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(d, text, sizes, max_w, max_lines, bold=True):
    """Pick the largest size from `sizes` whose wrap fits max_lines."""
    path = FONT_BOLD if bold else FONT_REG
    for size in sizes:
        font = load_font(path, size)
        lines = wrap_text(d, text, font, max_w)
        if len(lines) <= max_lines:
            return font, lines
    font = load_font(path, sizes[-1])
    return font, wrap_text(d, text, font, max_w)


def star_points(cx, cy, r_outer, r_inner, n=8, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.radians(rot + i * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rot_rect(cx, cy, w, h, angle_deg):
    """Corners of a rectangle rotated by angle_deg around its centre."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2),
                   (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return pts


# ---- masthead and footer -------------------------------------------
def draw_masthead(d):
    d.rectangle([0, 0, W, 150], fill=NAVY)
    d.rectangle([0, 150, W, 154], fill=GOLD)
    font, lines = fit_text(d, "THE WORLD IN ONE PICTURE",
                           [64, 60, 56, 52], 980, 1, bold=True)
    d.text((W / 2, 24), lines[0], font=font, fill=CREAM, anchor="ma")
    font2 = load_font(FONT_BOLD, 34)
    d.text((W / 2, 92), "THURSDAY \u00b7 26 NOVEMBER 2026",
           font=font2, fill=GOLD, anchor="ma")


def draw_footer(d):
    d.rectangle([0, 960, W, H], fill=NAVY)
    text = ("ALSO THURSDAY: BANGKOK REFINERY BLAST INJURES NINE \u00b7 "
            "CAIRO ROAD FIRE KILLS 31 \u00b7 ISRAELI STRIKES KILL NINE "
            "IN GAZA \u00b7 EBOLA CASES IN DR CONGO PASS 12,000 \u00b7 "
            "AMERICA MARKS THANKSGIVING")
    font, lines = fit_text(d, text, [20, 19, 18, 17], 976, 2, bold=False)
    line_h = font.size + 5
    total = len(lines) * line_h
    y = 960 + (64 - total) / 2
    for line in lines:
        d.text((W / 2, y), line, font=font, fill=CREAM, anchor="ma")
        y += line_h


# ---- icons (flat-colour, drawn inside a 448 x 80 box) ---------------
def icon_drone(d, bx0, by0, bx1, by1):
    """Grey drone over a Kuwait skyline, red burst."""
    cx = (bx0 + bx1) / 2
    ground = by1 - 6
    # skyline blocks, left to right
    blocks = [(bx0 + 30, 46, 54), (bx0 + 96, 58, 62), (bx0 + 172, 38, 46),
              (bx0 + 226, 62, 58), (bx0 + 296, 44, 66), (bx0 + 358, 54, 50)]
    for x, w, h in blocks:
        d.rectangle([x, ground - h, x + w, ground], fill=GREY)
        d.rectangle([x, ground - h, x + w, ground - h + 4], fill=DARK_GREY)
    # Kuwait Towers style: stalk + sphere, centre right
    tx = bx0 + 320
    d.rectangle([tx - 3, ground - 74, tx + 3, ground], fill=DARK_GREY)
    d.ellipse([tx - 13, ground - 92, tx + 13, ground - 66], fill=GREY)
    d.ellipse([tx - 13, ground - 92, tx + 13, ground - 66], outline=DARK_GREY)
    d.rectangle([bx0 + 16, ground, bx1 - 16, ground + 3], fill=DARK_GREY)
    # drone, upper left, large enough to read at small scale
    dx, dy = cx - 130, by0 + 16
    d.rounded_rectangle([dx - 22, dy - 6, dx + 22, dy + 6], radius=5,
                        fill=DARK_GREY)
    d.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=NAVY)
    for sx, sy in ((-32, -10), (32, -10), (-32, 10), (32, 10)):
        d.line([dx, dy, dx + sx, dy + sy], fill=DARK_GREY, width=3)
        d.ellipse([dx + sx - 7, dy + sy - 4, dx + sx + 7, dy + sy + 4],
                  fill=GREY)
    d.line([dx - 22, dy + 12, dx + 22, dy + 12], fill=DARK_GREY, width=2)
    # red burst over the skyline, right side
    bx, by = bx0 + 262, ground - 52
    d.polygon(star_points(bx, by, 22, 9), fill=RED)
    d.polygon(star_points(bx, by, 12, 5), fill=(255, 120, 90))


def icon_ecb(d, bx0, by0, bx1, by1):
    """Classical bank building with columns and a gold euro coin."""
    cx = (bx0 + bx1) / 2
    base = by1 - 6
    # steps
    d.rectangle([cx - 118, base - 6, cx + 118, base], fill=GREY)
    d.rectangle([cx - 104, base - 12, cx + 104, base - 6], fill=(170, 174, 180))
    # columns
    for i in range(4):
        x = cx - 84 + i * 56
        d.rectangle([x, base - 52, x + 16, base - 12], fill=(235, 233, 226),
                    outline=NAVY, width=1)
    # entablature + pediment
    d.rectangle([cx - 104, base - 62, cx + 104, base - 52], fill=NAVY)
    d.polygon([(cx - 104, base - 62), (cx + 104, base - 62), (cx, base - 80)],
              fill=NAVY)
    d.ellipse([cx - 5, base - 76, cx + 5, base - 66], fill=GOLD)
    # big gold euro coin, overlapping the right side
    coin_cx, coin_cy, r = bx1 - 52, by0 + 34, 30
    d.ellipse([coin_cx - r, coin_cy - r, coin_cx + r, coin_cy + r],
              fill=GOLD, outline=(176, 112, 10), width=3)
    ef = load_font(FONT_BOLD, 34)
    d.text((coin_cx, coin_cy - 2), "\u20ac", font=ef, fill=NAVY,
           anchor="mm")


def icon_tariffs(d, bx0, by0, bx1, by1):
    """Cargo ship with containers and a percent price tag."""
    cx = (bx0 + bx1) / 2
    deck = by0 + 46
    # containers, two rows
    cols = [RED, BLUE, TAN, GREEN, MID_BLUE]
    for row in range(2):
        for i in range(4):
            x = cx - 108 + i * 54
            y = deck - 16 * (row + 1)
            d.rectangle([x, y, x + 48, y + 14], fill=cols[(i + row) % 5],
                        outline=NAVY, width=1)
    # hull
    d.polygon([(cx - 128, deck), (cx + 128, deck), (cx + 108, deck + 22),
               (cx - 108, deck + 22)], fill=NAVY)
    d.rectangle([cx - 128, deck, cx + 128, deck + 5], fill=RED)
    # waves
    for wx in (bx0 + 30, bx0 + 190, bx0 + 340):
        d.arc([wx, by1 - 14, wx + 56, by1 + 2], 180, 360, fill=BLUE, width=3)
    # price tag, right side
    tx, ty = bx1 - 62, by0 + 16
    tag = [(tx - 26, ty - 12), (tx + 6, ty - 12), (tx + 26, ty + 8),
           (tx + 6, ty + 28), (tx - 26, ty + 28)]
    d.polygon(tag, fill=(255, 255, 255), outline=RED, width=2)
    d.ellipse([tx - 20, ty + 2, tx - 12, ty + 10], fill=RED)
    tf = load_font(FONT_BOLD, 20)
    d.text((tx + 2, ty + 8), "%", font=tf, fill=RED, anchor="mm")


def icon_ukraine(d, bx0, by0, bx1, by1):
    """Night sky over rooftops, missile trails and a shield."""
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=8, fill=NIGHT)
    cx = (bx0 + bx1) / 2
    # stars
    for sx, sy in ((bx0 + 40, by0 + 12), (bx0 + 120, by0 + 22),
                   (bx0 + 260, by0 + 10), (bx0 + 340, by0 + 26),
                   (bx0 + 400, by0 + 14)):
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255))
    # missile / drone trails: long diagonal streaks, inside the icon box
    d.line([(bx0 + 30, by0 + 60), (bx0 + 90, by0 + 32),
            (bx0 + 132, by0 + 16)], fill=GOLD, width=3)
    d.ellipse([bx0 + 126, by0 + 10, bx0 + 138, by0 + 22], fill=GOLD)
    d.line([(bx0 + 250, by0 + 58), (bx0 + 330, by0 + 30),
            (bx0 + 398, by0 + 16)], fill=CREAM, width=3)
    d.ellipse([bx0 + 392, by0 + 10, bx0 + 404, by0 + 22], fill=CREAM)
    # rooftops
    base = by1
    for x, w, h in ((bx0 + 8, 90, 26), (bx0 + 110, 110, 34),
                    (bx0 + 230, 100, 28), (bx0 + 340, 96, 36)):
        d.polygon([(x, base), (x + w / 2, base - h), (x + w, base)],
                  fill=(8, 16, 40))
    # shield, centre left, slightly larger
    sx, sy = cx - 60, by0 + 16
    shield = [(sx - 28, sy), (sx + 28, sy), (sx + 28, sy + 20),
              (sx, sy + 48), (sx - 28, sy + 20)]
    d.polygon(shield, fill=(29, 53, 87), outline=GOLD, width=2)
    d.line([(sx - 12, sy + 20), (sx - 2, sy + 32), (sx + 14, sy + 12)],
           fill=GOLD, width=3)


def icon_hiv(d, bx0, by0, bx1, by1):
    """Syringe over an Africa continent shape, green cross."""
    cx = (bx0 + bx1) / 2
    # Africa, rough outline (normalised points, 100 x 110 box)
    pts = [(0.30, 0.02), (0.45, 0.00), (0.62, 0.04), (0.78, 0.08),
           (0.90, 0.16), (0.96, 0.28), (0.88, 0.38), (0.86, 0.50),
           (0.78, 0.62), (0.72, 0.78), (0.62, 0.95), (0.55, 1.00),
           (0.50, 0.88), (0.44, 0.72), (0.36, 0.58), (0.22, 0.46),
           (0.10, 0.34), (0.06, 0.20), (0.14, 0.08)]
    ax, ay = cx + 24, by0 - 2
    scaled = [(ax + px * 100, ay + py * 84) for px, py in pts]
    d.polygon(scaled, fill=TAN, outline=(140, 100, 30))
    d.ellipse([ax + 100, ay + 62, ax + 116, ay + 78], fill=TAN,
              outline=(140, 100, 30))
    # syringe, diagonal across the left
    sx, sy = cx - 90, by0 + 40
    d.polygon(rot_rect(sx, sy, 58, 15, -35), fill=(255, 255, 255),
              outline=NAVY, width=2)
    d.line([sx - 34, sy + 20, sx - 52, sy + 33], fill=NAVY, width=3)
    d.polygon(rot_rect(sx + 36, sy - 21, 14, 6, -35), fill=NAVY)
    d.line([sx + 42, sy - 25, sx + 52, sy - 31], fill=NAVY, width=2)
    # green cross, lower left
    gx, gy = bx0 + 52, by1 - 22
    d.rectangle([gx - 14, gy - 5, gx + 14, gy + 5], fill=GREEN)
    d.rectangle([gx - 5, gy - 14, gx + 5, gy + 14], fill=GREEN)


def icon_tanker(d, bx0, by0, bx1, by1):
    """Tanker tipped on its side in blue waves, dark slick."""
    cx = (bx0 + bx1) / 2
    # waves, all inside the icon box
    d.rectangle([bx0, by1 - 26, bx1, by1], fill=LIGHT_BLUE)
    d.ellipse([bx0 + 6, by1 - 34, bx0 + 150, by1 - 6], fill=BLUE)
    d.ellipse([bx0 + 170, by1 - 38, bx0 + 330, by1 - 8], fill=BLUE)
    d.ellipse([bx0 + 310, by1 - 30, bx1 - 6, by1 - 4], fill=MID_BLUE)
    # dark oil slick on the water
    d.ellipse([cx - 30, by1 - 24, cx + 130, by1 - 10], fill=(30, 30, 34))
    # tipped tanker hull, lower end dipping into the waves
    hx, hy = cx - 40, by0 + 42
    d.polygon(rot_rect(hx, hy, 150, 30, -24), fill=DARK_RED,
              outline=NAVY, width=2)
    d.polygon(rot_rect(hx + 46, hy - 22, 26, 18, -24), fill=GREY,
              outline=NAVY, width=2)
    d.line([hx + 58, hy - 30, hx + 70, hy - 44], fill=NAVY, width=3)
    # small life-ring
    rx, ry = cx + 92, by0 + 58
    d.ellipse([rx - 10, ry - 10, rx + 10, ry + 10], fill=(255, 255, 255),
              outline=RED, width=4)


# ---- panels --------------------------------------------------------
PANELS = [
    (icon_drone,
     "DRONE STRIKE KILLS TWO ITALIANS IN KUWAIT",
     "Tehran denies any role in the attack"),
    (icon_ecb,
     "SPAIN'S HERNANDEZ DE COS TO LEAD THE ECB",
     "Eurozone leaders pick Lagarde's successor"),
    (icon_tariffs,
     "US PROPOSES NEW TARIFFS ON 14 PARTNERS",
     "China, the EU and Indonesia among those hit"),
    (icon_ukraine,
     "RUSSIA STRIKES UKRAINE OVERNIGHT",
     "Trump urges Putin to pull back in Europe"),
    (icon_hiv,
     "CHEAPER HIV PREVENTION JAB REACHES AFRICA",
     "Twice-yearly lenacapavir at a lower cost"),
    (icon_tanker,
     "DIESEL TANKER CAPSIZES OFF IBIZA",
     "One crew member dies; 7,000 tonnes aboard"),
]


def draw_card(d, x0, y0, icon_fn, headline, subline):
    w, h = 480, 248
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=10, fill=CARD,
                        outline=NAVY, width=2)
    # icon zone: 448 wide, 80 tall
    icon_fn(d, x0 + 16, y0 + 10, x0 + 464, y0 + 90)
    # headline, bold, at most 2 lines
    font, lines = fit_text(d, headline, [36, 34, 32, 30, 28], 448, 2,
                           bold=True)
    line_h = font.size + 6
    y = y0 + 96
    for line in lines:
        d.text((x0 + w / 2, y), line, font=font, fill=INK, anchor="ma")
        y += line_h
    # subline, at most 2 lines
    sfont, slines = fit_text(d, subline, [22, 20, 18], 448, 2, bold=False)
    sline_h = sfont.size + 4
    y += 6
    for line in slines:
        d.text((x0 + w / 2, y), line, font=sfont, fill=SUB, anchor="ma")
        y += sline_h


def build_image():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    margin, gap = 24, 16
    top, row_h = 166, 248
    for i, (icon_fn, headline, subline) in enumerate(PANELS):
        col = i % 2
        row = i // 2
        x0 = margin + col * (480 + gap)
        y0 = top + row * (row_h + gap)
        draw_card(d, x0, y0, icon_fn, headline, subline)
    draw_footer(d)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build_image()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG", optimize=True)
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    main()
