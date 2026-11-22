# Zeichnet die Vorschaubilder für soziale Medien (1200 x 630): social.png auf der Startseite und in beiden Kalendern.
# Schrift: Nunito (SIL Open Font License, tools/fonts/OFL.txt).
import os, random
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "tools", "fonts", "Nunito.ttf")
W, H = 1200, 630


def font(size, weight="ExtraBold"):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name(weight)
    return f


def verlauf(oben, unten):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(oben, unten)))
    return im


def schnee(d, seed):
    r = random.Random(seed)
    for _ in range(140):
        x, y, s = r.uniform(0, W), r.uniform(0, H - 60), r.uniform(1.2, 3.6)
        if x < 730 and 95 < y < 520: continue  # kein Schnee hinter dem Text
        d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 255, 255, r.randint(120, 220)))


def tuer(d, x, y, w, h, farbe, zahl):
    d.rounded_rectangle([x + 4, y + 7, x + w + 4, y + h + 7], 22, fill=(0, 0, 0, 70))  # Schatten
    d.rounded_rectangle([x, y, x + w, y + h], 22, fill=farbe, outline=(255, 255, 255, 90), width=4)
    # Schnee auf dem Türchen: weiße Kante mit Bögen
    d.rounded_rectangle([x, y, x + w, y + 22], 22, fill="white")
    d.rectangle([x, y + 12, x + w, y + 22], fill="white")
    n = max(3, round(w / 22))
    bw = w / n
    for i in range(n):
        d.ellipse([x + i * bw, y + 14, x + (i + 1) * bw, y + 32], fill="white")
    f = font(int(min(w, h) * 0.42))
    d.text((x + w / 2, y + h / 2 + 12), str(zahl), font=f, fill="white", anchor="mm", stroke_width=0)


def schneewehe(d):
    pts = [(0, H)]
    for i in range(0, W + 1, 20):
        import math
        pts.append((i, H - 46 - 14 * math.sin(i / 130) - 8 * math.sin(i / 47)))
    pts.append((W, H))
    d.polygon(pts, fill="white")


def bild(pfad, oben, unten, farben, kicker, titel, unter, idee, akzent, zahlen, titelgroesse=96, oben_y=160):
    im = verlauf(oben, unten).convert("RGBA")
    lage = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lage)
    schnee(d, titel)
    # Türchen rechts, 3 x 3, eines groß
    gx, gy, s, g = 760, 70, 118, 16
    plan = [(0, 0, 1, 1), (1, 0, 1, 1), (2, 0, 1, 1), (0, 1, 2, 2), (2, 1, 1, 1), (2, 2, 1, 1)]
    for (cx, cy, cw, ch), z, fb in zip(plan, zahlen, farben):
        tuer(d, gx + cx * (s + g), gy + cy * (s + g), cw * s + (cw - 1) * g, ch * s + (ch - 1) * g, fb, z)
    schneewehe(d)
    # Text links
    y = oben_y
    d.text((70, oben_y - 40), kicker, font=font(26, "Bold"), fill=akzent)
    for zeile in titel.split("\n"):
        d.text((66, y), zeile, font=font(titelgroesse, "Black"), fill="white")
        y += int(titelgroesse * 1.08)
    d.text((70, y + 16), unter, font=font(32, "SemiBold"), fill=(255, 255, 255, 225))
    d.text((70, y + 70), idee, font=font(36, "ExtraBold"), fill=akzent)
    d.text((70, H - 36), "adventingeo.de", font=font(26, "Bold"), fill=(70, 80, 100), anchor="ls")
    Image.alpha_composite(im, lage).convert("RGB").save(pfad, optimize=True)
    print("ok", os.path.relpath(pfad, ROOT))


meer = ["#0e7c86", "#1565a8", "#0f8f6e", "#e07a5f", "#3d5a98", "#2a9d8f"]
tiere = ["#c0392b", "#8e44ad", "#16a085", "#d35400", "#2471a3", "#b7950b"]

bild(os.path.join(ROOT, "meereszauber", "social.png"), (24, 104, 160), (3, 26, 52), meer,
     "ADVENTSKALENDER", "Meereszauber", "Rekorde aus dem Ozean · 8–9 Jahre", "Nach einer Idee von Carola", (127, 227, 224), [7, 15, 3, 24, 11, 20], titelgroesse=86, oben_y=225)
bild(os.path.join(ROOT, "zauber-der-tiere", "social.png"), (107, 63, 160), (15, 8, 36), tiere,
     "ADVENTSKALENDER", "Zauber\nder Tiere", "Tierwesen & Fabelwesen · 6–7 Jahre", "Nach einer Idee von Maria", (255, 211, 110), [9, 2, 16, 24, 5, 13])
bild(os.path.join(ROOT, "social.png"), (59, 79, 154), (11, 16, 48), [meer[0], tiere[1], meer[3], tiere[0], meer[1], tiere[2]],
     "ZWEI ADVENTSKALENDER FÜR KINDER", "Meereszauber &\nZauber der Tiere", "Tierrekorde & Fabelwesen", "Nach Ideen von Carola und Maria", (255, 211, 110), [4, 18, 1, 24, 12, 8], titelgroesse=70)
