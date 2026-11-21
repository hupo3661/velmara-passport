#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Draws, entirely procedurally with Pillow, one open passport spread for the
invented Republic of Velmara (a fictional Adriatic island nation) and writes
it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

No network, no external images, no real country's passport design.
Every person, place, date and number on the page is fictional.

Layout (1024 x 720, a two-page spread):
  Left page  - data page: coat of arms, portrait, personal data, signature,
               machine-readable zone (ICAO check digits computed properly).
  Right page - visas page: arrival/departure stamps from the neighbouring
               fictional states Dravar, Korvath and Selanor, a visitor visa,
               and a harbour-tax fee stamp.
All dates are internally consistent: the passport was issued
14 MAR 2024 and every stamp falls after that date.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 720
PAPER = (244, 239, 228)
PAPER_DARK = (232, 225, 207)
INK = (28, 32, 48)
GOLD = (150, 112, 38)
GOLD_LIGHT = (186, 152, 74)
NAVY = (31, 58, 95)
TEAL = (23, 94, 98)
RUST = (146, 58, 34)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF_I = "DejaVuSerif-Italic.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
MONO = "DejaVuSansMono.ttf"
MONO_B = "DejaVuSansMono-Bold.ttf"


def T(draw, xy, s, fname, size, fill, anchor="la"):
    draw.text(xy, s, font=font(fname, size), fill=fill, anchor=anchor)


def mrz_check(s):
    """ICAO 7-3-1 check digit."""
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(s):
        if ch.isdigit():
            v = int(ch)
        elif ch == "<":
            v = 0
        else:
            v = ord(ch) - 55
        total += v * weights[i % 3]
    return str(total % 10)


def build_mrz():
    line1 = "P<VLMVOSS<<ELENA<MARIS"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "VM482913"
    doc_cd = mrz_check(doc)
    dob = "910517"
    dob_cd = mrz_check(dob)
    exp = "340313"
    exp_cd = mrz_check(exp)
    line2_body = doc + doc_cd + "VLM" + dob + dob_cd + "F" + exp + exp_cd
    # pad to 43 chars, then the composite check digit as char 44
    line2 = line2_body + "<" * (43 - len(line2_body))
    line2 = line2 + mrz_check(line2)
    return line1, line2


def guilloche(draw, box, color, step=7, amp=3):
    """Faint wavy security lines inside a box."""
    x0, y0, x1, y1 = box
    for y in range(y0, y1, step):
        pts = []
        for x in range(x0, x1 + 1, 6):
            yy = y + amp * math.sin((x - x0) / 26.0 + y / 31.0)
            pts.append((x, yy))
        draw.line(pts, fill=color, width=1)


def coat_of_arms(draw, cx, cy, s):
    """Velmara's arms: a shield with three waves, a star and a lighthouse."""
    # shield outline
    shield = [(cx - 0.62 * s, cy - 0.55 * s), (cx + 0.62 * s, cy - 0.55 * s),
              (cx + 0.62 * s, cy + 0.10 * s), (cx, cy + 0.75 * s),
              (cx - 0.62 * s, cy + 0.10 * s)]
    draw.polygon(shield, outline=GOLD, width=3)
    draw.polygon([(cx - 0.52 * s, cy - 0.45 * s), (cx + 0.52 * s, cy - 0.45 * s),
                  (cx + 0.52 * s, cy + 0.08 * s), (cx, cy + 0.62 * s),
                  (cx - 0.52 * s, cy + 0.08 * s)], outline=GOLD_LIGHT, width=1)
    # star above shield
    star_cx, star_cy, r = cx, cy - 0.78 * s, 0.16 * s
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((star_cx + rr * math.cos(ang), star_cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=GOLD)
    # lighthouse: tower + light beams
    bx, by = cx, cy - 0.18 * s
    draw.polygon([(bx - 0.10 * s, by + 0.42 * s), (bx + 0.10 * s, by + 0.42 * s),
                  (bx + 0.06 * s, by - 0.28 * s), (bx - 0.06 * s, by - 0.28 * s)],
                 fill=NAVY)
    draw.rectangle([bx - 0.09 * s, by - 0.36 * s, bx + 0.09 * s, by - 0.26 * s],
                   fill=NAVY)
    draw.ellipse([bx - 0.05 * s, by - 0.44 * s, bx + 0.05 * s, by - 0.34 * s],
                 fill=GOLD)
    for sgn in (-1, 1):
        draw.polygon([(bx + sgn * 0.10 * s, by - 0.33 * s),
                      (bx + sgn * 0.48 * s, by - 0.48 * s),
                      (bx + sgn * 0.48 * s, by - 0.18 * s)], fill=(214, 178, 94))
    # three waves at the foot of the shield
    for k, wy in enumerate((0.22, 0.36, 0.50)):
        y = cy + wy * s
        pts = []
        for x in range(int(cx - 0.48 * s), int(cx + 0.48 * s) + 1, 4):
            pts.append((x, y + 0.045 * s * math.sin((x - cx) / (0.16 * s) + k)))
        draw.line(pts, fill=TEAL, width=3)


def draw_portrait(img, box):
    """Stylised passport photograph of the fictional holder."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    photo = Image.new("RGB", (w, h), (203, 214, 218))
    d = ImageDraw.Draw(photo)
    # soft backdrop gradient
    for yy in range(h):
        t = yy / h
        col = (int(205 - 28 * t), int(216 - 30 * t), int(220 - 28 * t))
        d.line([(0, yy), (w, yy)], fill=col)
    cx = w // 2
    # shoulders / navy blazer
    d.polygon([(cx - 78, h), (cx - 62, h - 62), (cx - 30, h - 84),
               (cx + 30, h - 84), (cx + 62, h - 62), (cx + 78, h)],
              fill=(38, 54, 86))
    # white shirt V
    d.polygon([(cx - 26, h - 82), (cx + 26, h - 82), (cx, h - 38)], fill=(245, 245, 240))
    # shirt collar
    d.polygon([(cx - 26, h - 82), (cx, h - 58), (cx - 10, h - 84)], fill=(235, 235, 228))
    d.polygon([(cx + 26, h - 82), (cx, h - 58), (cx + 10, h - 84)], fill=(235, 235, 228))
    # neck
    d.rectangle([cx - 14, h - 108, cx + 14, h - 78], fill=(214, 164, 122))
    d.rectangle([cx - 14, h - 108, cx + 14, h - 96], fill=(198, 148, 106))
    # head
    d.ellipse([cx - 40, 30, cx + 40, 118], fill=(232, 185, 143))
    # soft cheek shading
    d.ellipse([cx - 40, 62, cx - 8, 108], fill=(226, 176, 132))
    d.ellipse([cx + 8, 62, cx + 40, 108], fill=(226, 176, 132))
    # ears
    d.ellipse([cx - 48, 66, cx - 36, 90], fill=(232, 185, 143))
    d.ellipse([cx + 36, 66, cx + 48, 90], fill=(232, 185, 143))
    # hair: dark bob with a fringe across the forehead
    d.pieslice([cx - 50, 6, cx + 50, 92], 180, 360, fill=(58, 38, 28))
    d.polygon([(cx - 52, 40), (cx - 44, 34), (cx - 46, 108), (cx - 56, 108),
               (cx - 58, 60)], fill=(58, 38, 28))
    d.polygon([(cx + 52, 40), (cx + 44, 34), (cx + 46, 108), (cx + 56, 108),
               (cx + 58, 60)], fill=(58, 38, 28))
    # fringe: hair sweeping down to just above the brows
    d.ellipse([cx - 42, 16, cx + 42, 58], fill=(58, 38, 28))
    d.ellipse([cx - 38, 34, cx + 38, 116], fill=(232, 185, 143))
    # brows
    d.arc([cx - 30, 62, cx - 8, 76], 200, 340, fill=(58, 38, 28), width=3)
    d.arc([cx + 8, 62, cx + 30, 76], 200, 340, fill=(58, 38, 28), width=3)
    # eyes
    for ex in (cx - 19, cx + 19):
        d.ellipse([ex - 8, 76, ex + 8, 86], fill=(250, 250, 246))
        d.ellipse([ex - 4, 77, ex + 4, 85], fill=(52, 38, 30))
        d.ellipse([ex - 1, 79, ex + 2, 82], fill=(255, 255, 255))
        d.line([(ex - 9, 76), (ex + 9, 76)], fill=(58, 38, 28), width=2)
    # nose
    d.line([(cx, 84), (cx - 3, 100), (cx + 3, 102)], fill=(198, 148, 106), width=2)
    # lips
    d.polygon([(cx - 11, 110), (cx, 107), (cx + 11, 110), (cx, 115)],
              fill=(172, 96, 84))
    d.line([(cx - 11, 110), (cx + 11, 110)], fill=(140, 70, 60), width=1)
    # blazer lapels
    d.polygon([(cx - 30, h - 84), (cx, h - 40), (cx - 12, h - 84)], fill=(30, 44, 72))
    d.polygon([(cx + 30, h - 84), (cx, h - 40), (cx + 12, h - 84)], fill=(30, 44, 72))
    img.paste(photo, box)


def stamp_layer(text_lines, color, size, rotate_deg, font_size=15):
    """A rubber-stamp overlay, rotated, returned as an RGBA image."""
    pad = 26
    w = size[0] + 2 * pad
    h = size[1] + 2 * pad
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([pad, pad, pad + size[0], pad + size[1]],
                        radius=10, outline=color + (235,), width=3)
    d.rounded_rectangle([pad + 5, pad + 5, pad + size[0] - 5, pad + size[1] - 5],
                        radius=7, outline=color + (180,), width=1)
    y = pad + 12
    for i, line in enumerate(text_lines):
        f = MONO_B if i == 0 else MONO
        fs = font_size + 2 if i == 0 else font_size
        d.text((w // 2, y), line, font=font(f, fs), fill=color + (235,),
               anchor="ma")
        y += fs + 7
    return layer.rotate(rotate_deg, expand=True, resample=Image.BICUBIC)


def circular_stamp(img, cx, cy, r, color, lines, rotate_deg=0):
    layer = Image.new("RGBA", (r * 2 + 40, r * 2 + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = r + 20
    d.ellipse([c - r, c - r, c + r, c + r], outline=color + (230,), width=3)
    d.ellipse([c - r + 7, c - r + 7, c + r - 7, c + r - 7],
              outline=color + (170,), width=1)
    y = c - 26
    for i, line in enumerate(lines):
        fs = 15 if i == 0 else 13
        d.text((c, y), line, font=font(MONO_B if i == 0 else MONO, fs),
               fill=color + (230,), anchor="ma")
        y += fs + 5
    layer = layer.rotate(rotate_deg, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (cx - layer.width // 2, cy - layer.height // 2), layer)


def data_row(d, x, y, label, value, value_font=SERIF_B, value_size=17,
             label_size=10, width=300):
    T(d, (x, y), label, SANS, label_size, (110, 105, 90))
    T(d, (x, y + 14), value, value_font, value_size, INK)
    d.line([(x, y + 36), (x + width, y + 36)], fill=(196, 184, 158), width=1)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- paper: outer border, centre spine, guilloche -------------------
    d.rectangle([6, 6, W - 7, H - 7], outline=GOLD, width=2)
    d.rectangle([11, 11, W - 12, H - 12], outline=GOLD_LIGHT, width=1)
    guilloche(d, (16, 16, W - 17, H - 17), (222, 210, 180))
    d.line([(W // 2, 12), (W // 2, H - 12)], fill=(176, 160, 120), width=2)
    # soft shadow along the spine
    for i in range(10):
        a = 26 - i * 2
        d.line([(W // 2 - 6 - i, 14), (W // 2 - 6 - i, H - 14)],
               fill=(120, 105, 70, a), width=1)
        d.line([(W // 2 + 6 + i, 14), (W // 2 + 6 + i, H - 14)],
               fill=(120, 105, 70, a), width=1)

    # ================= LEFT PAGE : DATA PAGE ==============================
    L = 26            # left margin
    mid = W // 2
    # header: coat of arms + country name
    coat_of_arms(d, L + 42, 78, 52)
    T(d, (L + 88, 40), "REPUBLIC OF VELMARA", SERIF_B, 21, NAVY)
    T(d, (L + 88, 66), "PASSPORT  ·  PASSEPORT", SANS_B, 11, GOLD)
    T(d, (L + 88, 84), "An island republic of the Velmaran Sea  ·  Est. 1919",
      SERIF_I, 11, (110, 105, 90))
    d.line([(L, 112), (mid - 26, 112)], fill=GOLD, width=2)

    # photo
    photo_box = (L + 6, 128, L + 166, 128 + 200)
    draw_portrait(img, photo_box)
    d.rectangle(photo_box, outline=INK, width=2)
    d = ImageDraw.Draw(img, "RGBA")
    T(d, (L + 6, 332), "PHOTOGRAPH", SANS, 9, (110, 105, 90))

    # personal data, right of the photo
    dx = L + 188
    data_row(d, dx, 128, "SURNAME / NOM", "VOSS")
    data_row(d, dx, 180, "GIVEN NAMES / PRÉNOMS", "ELENA MARIS")
    data_row(d, dx, 232, "NATIONALITY / NATIONALITÉ", "VELMARAN")
    data_row(d, dx, 284, "DATE / PLACE OF BIRTH", "17 MAY 1991, PORT SABLE",
             value_size=15)
    data_row(d, dx, 336, "SEX / SEXE", "F", value_size=17)
    data_row(d, dx, 388, "DOCUMENT No. / No. DU DOCUMENT", "VM 482 913",
             value_font=MONO_B, value_size=16)

    # issue / expiry block
    d.line([(L, 448), (mid - 26, 448)], fill=GOLD, width=1)
    T(d, (L, 460), "DATE OF ISSUE / DÉLIVRÉ LE", SANS, 10, (110, 105, 90))
    T(d, (L, 476), "14 MAR 2024", SERIF_B, 17, INK)
    T(d, (L + 190, 460), "DATE OF EXPIRY / EXPIRE LE", SANS, 10, (110, 105, 90))
    T(d, (L + 190, 476), "13 MAR 2034", SERIF_B, 17, INK)
    T(d, (L, 508), "AUTHORITY / AUTORITÉ", SANS, 10, (110, 105, 90))
    T(d, (L, 524), "PORT SABLE PASSPORT OFFICE", SERIF_B, 14, INK)
    T(d, (L, 548), "LANGUAGES / LANGUES:  VELMARAN  ·  ENGLISH",
      SANS, 10, (90, 85, 70))

    # endorsement: the telling detail of paperwork
    d.rounded_rectangle([L, 572, mid - 26, 622], radius=4,
                        outline=TEAL, width=2)
    T(d, (L + 10, 579), "ENDORSEMENT", SANS_B, 10, TEAL)
    T(d, (L + 10, 594), "Holder is a licensed harbour pilot -",
      SANS, 11, INK)
    T(d, (L + 10, 608), "may land at any Velmaran quay.", SANS, 11, INK)
    # signature, right side of the endorsement box
    T(d, (L + 318, 580), "Elena M. Voss", SERIF_I, 19, (52, 58, 96))
    d.line([(L + 316, 604), (mid - 32, 604)], fill=INK, width=1)
    T(d, (L + 318, 608), "HOLDER'S SIGNATURE", SANS, 8, (110, 105, 90))

    # machine-readable zone
    mrz1, mrz2 = build_mrz()
    d.rectangle([L, 636, mid - 26, 694], fill=(238, 234, 222))
    d.rectangle([L, 636, mid - 26, 694], outline=(150, 140, 115), width=1)
    T(d, (L + 8, 644), mrz1, MONO, 15, INK)
    T(d, (L + 8, 666), mrz2, MONO, 15, INK)

    # ================= RIGHT PAGE : VISAS & STAMPS ========================
    R = mid + 26
    T(d, (R, 40), "VISAS", SERIF_B, 20, NAVY)
    T(d, (R + 92, 46), "- arrivals & departures -", SERIF_I, 12,
      (110, 105, 90))
    T(d, (W - 28, 40), "p. 8–9", SANS, 11, (110, 105, 90), anchor="ra")
    d.line([(R, 70), (W - 28, 70)], fill=GOLD, width=2)

    # visa sticker (Selanor, 90 days) — the paper visa
    vx0, vy0, vx1, vy1 = R, 88, R + 250, 250
    d.rectangle([vx0, vy0, vx1, vy1], fill=(232, 238, 228),
                outline=TEAL, width=2)
    d.rectangle([vx0 + 5, vy0 + 5, vx1 - 5, vy1 - 5], outline=TEAL, width=1)
    guilloche(d, (vx0 + 8, vy0 + 8, vx1 - 8, vy1 - 8), (200, 214, 198))
    T(d, (vx0 + 12, vy0 + 12), "VISITOR VISA", SANS_B, 13, TEAL)
    T(d, (vx0 + 12, vy0 + 32), "SELANOR", SERIF_B, 20, INK)
    T(d, (vx0 + 12, vy0 + 60), "Single entry  ·  90 days", SANS, 12, INK)
    T(d, (vx0 + 12, vy0 + 78), "Valid 01 JAN 2025 – 31 MAR 2025", SANS, 12, INK)
    T(d, (vx0 + 12, vy0 + 96), "Issued at Port Sable", SANS, 12, INK)
    T(d, (vx0 + 12, vy0 + 114), "No. SEL-2025-0117", MONO, 12, INK)
    T(d, (vx0 + 12, vy0 + 134), "Fee paid: 25 VEL", SANS_B, 12, RUST)

    # stamps (all dated after the 14 MAR 2024 issue date)
    stamps = [
        # (lines, color, size, rotate, x, y)
        (["DRAVAR", "ARRIVAL", "22 JUN 2024"], (34, 96, 120), (168, 92), -7,
         R + 268, 92),
        (["KORVATH", "DEPARTURE", "09 SEP 2024"], (146, 58, 34), (168, 92), 6,
         R + 268, 200),
        (["SELANOR", "ARRIVAL", "18 JAN 2025"], (34, 96, 120), (168, 92), -5,
         R + 268, 308),
        (["DRAVAR", "DEPARTURE", "03 FEB 2026"], (146, 58, 34), (168, 92), 8,
         R + 268, 416),
    ]
    for lines, color, size, rot, x, y in stamps:
        layer = stamp_layer(lines, color, size, rot)
        img.paste(layer, (x, y), layer)
        d = ImageDraw.Draw(img, "RGBA")

    # harbour-tax fee stamp (circular)
    circular_stamp(img, R + 125, 330, 62, RUST,
                   ["HARBOUR TAX", "PAID", "12 VEL"], rotate_deg=-12)
    d = ImageDraw.Draw(img, "RGBA")
    T(d, (R + 125, 402), "PORT SABLE", MONO, 11, RUST, anchor="ma")

    # small handwritten-style arrival note, bottom of the visa page
    T(d, (R, 520), "Seen at the quay, 03 FEB 2026 - vessel MV Kestrel,",
      SERIF_I, 13, (70, 66, 90))
    T(d, (R, 540), "cargo: salt, dried figs, one crate of harbour charts.",
      SERIF_I, 13, (70, 66, 90))
    d.line([(R, 566), (W - 28, 566)], fill=GOLD, width=1)
    T(d, (R, 578), "This passport remains the property of the Republic of",
      SANS, 10, (110, 105, 90))
    T(d, (R, 592), "Velmara. If found, return to any Velmaran consulate.",
      SANS, 10, (110, 105, 90))
    T(d, (W - 28, 578), "VM 482 913", MONO_B, 12, INK, anchor="ra")

    # ---- write output ----------------------------------------------------
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img.save(out_path, format="PNG", optimize=True)
    print(f"Wrote {out_path} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
