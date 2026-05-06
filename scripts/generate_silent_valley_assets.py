from pathlib import Path
import math
import random

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "images"

INK = (38, 35, 31, 255)
INDIGO = (54, 82, 118, 255)
OCHRE = (166, 129, 58, 255)
PAPER = (247, 244, 235, 255)


ASSETS = [
    ("hero_valley.png", (1792, 1024), "valley"),
    ("event_cepo.png", (1024, 1024), "coast"),
    ("event_dafen.png", (1024, 1024), "cloudsea"),
    ("event_cikasuan.png", (1024, 1024), "terraces"),
    ("event_truku.png", (1024, 1024), "gorge"),
    ("divider_mountain.png", (1024, 512), "divider_mountain"),
    ("divider_water.png", (1024, 512), "divider_water"),
    ("divider_valley.png", (1024, 512), "divider_valley"),
    ("divider_coast.png", (1024, 512), "divider_coast"),
]


def wash(color, alpha):
    return color[:3] + (alpha,)


def paper(size, seed):
    rng = random.Random(seed)
    img = Image.new("RGBA", size, PAPER)
    px = img.load()
    w, h = size
    for y in range(h):
        for x in range(w):
            if rng.random() < 0.045:
                d = rng.randint(-7, 8)
                base = tuple(max(0, min(255, c + d)) for c in PAPER[:3])
                px[x, y] = base + (255,)
    return img.filter(ImageFilter.GaussianBlur(0.25))


def poly_mountain(draw, w, h, base, amp, offset, color, alpha):
    pts = [(0, h)]
    steps = 14
    for i in range(steps + 1):
        x = w * i / steps
        y = base - amp * (0.35 + 0.65 * math.sin(i * 1.23 + offset) ** 2)
        y += math.sin(i * 2.1 + offset) * amp * 0.18
        pts.append((x, y))
    pts += [(w, h)]
    draw.polygon(pts, fill=wash(color, alpha))
    for i in range(0, steps, 2):
        x = w * i / steps
        y = base - amp * (0.35 + 0.65 * math.sin(i * 1.23 + offset) ** 2)
        draw.line([(x, y + 8), (x + w * 0.09, base + amp * 0.1)], fill=wash(INK, max(12, alpha // 3)), width=max(1, w // 600))


def mist(draw, w, h, bands):
    for y, a, width in bands:
        for j in range(width):
            alpha = max(0, int(a * (1 - abs(j - width / 2) / (width / 2))))
            draw.line([(w * 0.05, y + j), (w * 0.95, y + j + math.sin(j / 20) * 8)], fill=(255, 252, 244, alpha), width=2)


def river(draw, w, h, start_y, end_y, alpha=96):
    pts = []
    for i in range(80):
        t = i / 79
        x = w * (0.16 + 0.68 * t)
        y = start_y * (1 - t) + end_y * t + math.sin(t * math.tau * 2.2) * h * 0.06
        pts.append((x, y))
    for width, a in [(20, alpha // 5), (10, alpha // 3), (4, alpha)]:
        draw.line(pts, fill=wash(INDIGO, a), width=max(1, width), joint="curve")


def coast(draw, w, h):
    draw.rectangle((0, h * 0.58, w, h), fill=wash(INDIGO, 32))
    for i in range(7):
        y = h * (0.63 + i * 0.045)
        draw.arc((w * -0.1, y - 60, w * 1.1, y + 80), 190, 350, fill=wash(INDIGO, 52 - i * 4), width=3)
    cliff = [(0, h * 0.42), (w * 0.26, h * 0.36), (w * 0.46, h * 0.48), (w * 0.58, h * 0.55), (0, h)]
    draw.polygon(cliff, fill=wash(INK, 56))
    for x in range(60, int(w * 0.55), 110):
        draw.ellipse((x, h * 0.60, x + 150, h * 0.68), fill=wash(INK, 44))


def terraces(draw, w, h):
    for i in range(12):
        y = h * (0.48 + i * 0.038)
        draw.arc((w * -0.1, y - 70, w * 1.2, y + 80), 180, 358, fill=wash(OCHRE, 70 - i * 3), width=3)
    for i in range(6):
        x = w * (0.14 + i * 0.13)
        draw.line([(x, h * 0.52), (x + w * 0.16, h * 0.92)], fill=wash(INK, 26), width=2)
    river(draw, w, h, h * 0.56, h * 0.91, 46)


def gorge(draw, w, h):
    left = [(0, h), (0, h * 0.20), (w * 0.32, h * 0.42), (w * 0.43, h)]
    right = [(w, h), (w, h * 0.16), (w * 0.65, h * 0.36), (w * 0.54, h)]
    draw.polygon(left, fill=wash(INK, 72))
    draw.polygon(right, fill=wash(INDIGO, 70))
    for x in [w * 0.23, w * 0.32, w * 0.67, w * 0.75]:
        draw.line([(x, h * 0.25), (x - w * 0.08, h * 0.92)], fill=(255, 252, 244, 80), width=3)
    river(draw, w, h, h * 0.72, h * 0.98, 82)


def water_lines(draw, w, h):
    for i in range(9):
        y = h * (0.35 + i * 0.045)
        pts = [(w * (0.10 + t * 0.80), y + math.sin(t * math.tau * 2 + i) * 16) for t in [j / 90 for j in range(91)]]
        draw.line(pts, fill=wash(INDIGO if i % 2 else INK, 52 - i * 2), width=3 if i < 4 else 2)


def render(name, size, kind):
    img = paper(size, name)
    draw = ImageDraw.Draw(img, "RGBA")
    w, h = size

    if kind in {"valley", "cloudsea", "divider_mountain", "divider_valley"}:
        poly_mountain(draw, w, h, h * 0.45, h * 0.20, 0.2, INDIGO, 34)
        poly_mountain(draw, w, h, h * 0.57, h * 0.24, 1.4, INK, 42)
        if kind == "valley":
            poly_mountain(draw, w, h, h * 0.66, h * 0.28, 2.3, OCHRE, 30)
            river(draw, w, h, h * 0.58, h * 0.84, 92)
        if kind == "cloudsea":
            mist(draw, w, h, [(h * 0.40, 170, 120), (h * 0.54, 150, 130), (h * 0.67, 120, 100)])
            poly_mountain(draw, w, h, h * 0.74, h * 0.16, 3.1, INK, 30)
        if kind == "divider_mountain":
            mist(draw, w, h, [(h * 0.48, 190, 130)])
        if kind == "divider_valley":
            river(draw, w, h, h * 0.52, h * 0.72, 50)

    if kind == "coast":
        coast(draw, w, h)
        poly_mountain(draw, w, h, h * 0.40, h * 0.12, 1.1, INK, 22)

    if kind == "terraces":
        poly_mountain(draw, w, h, h * 0.44, h * 0.18, 1.9, INDIGO, 34)
        mist(draw, w, h, [(h * 0.42, 100, 90)])
        terraces(draw, w, h)

    if kind == "gorge":
        gorge(draw, w, h)
        mist(draw, w, h, [(h * 0.32, 120, 100), (h * 0.50, 90, 80)])

    if kind == "divider_water":
        water_lines(draw, w, h)

    if kind == "divider_coast":
        coast(draw, w, h)

    img = img.filter(ImageFilter.GaussianBlur(0.35))
    OUT.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(OUT / name, "PNG", optimize=True)
    print(f"wrote {OUT / name}")


def main():
    for name, size, kind in ASSETS:
        render(name, size, kind)


if __name__ == "__main__":
    main()
