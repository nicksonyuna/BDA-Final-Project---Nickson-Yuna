# -*- coding: utf-8 -*-
"""
Menyusun tangkapan layar komposit 'Executive Dashboard' dengan menggabungkan
panel KPI, confusion matrix, feature importance, dan time-series ke dalam satu
bingkai bergaya dashboard untuk disisipkan sebagai Gambar 7.1 pada laporan.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figures")
BG = (14, 17, 23)
HEADER_BG = (10, 25, 41)
ACCENT = (30, 136, 229)
WHITE = (227, 242, 253)
SUB = (144, 202, 249)


def load(name):
    return Image.open(os.path.join(FIG, name)).convert("RGB")


def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def fit_width(img, target_w):
    w, h = img.size
    nh = int(h * target_w / w)
    return img.resize((target_w, nh), Image.LANCZOS)


# Kanvas
W = 2000
PAD = 40
HEADER_H = 170
GAP = 30

kpi = fit_width(load("fig_kpi.png"), W - 2 * PAD)
cm = load("fig_confusion_matrix.png")
fi = load("fig_feature_importance.png")
ts = fit_width(load("fig_timeseries.png"), W - 2 * PAD)

# Baris tengah: confusion matrix + feature importance berdampingan
row_w = (W - 2 * PAD - GAP) // 2
cm = fit_width(cm, row_w)
fi = fit_width(fi, row_w)
mid_h = max(cm.size[1], fi.size[1])

total_h = HEADER_H + PAD + kpi.size[1] + GAP + mid_h + GAP + ts.size[1] + PAD
canvas = Image.new("RGB", (W, total_h), BG)
draw = ImageDraw.Draw(canvas)

# Header bar
draw.rectangle([0, 0, W, HEADER_H], fill=HEADER_BG)
draw.rectangle([0, HEADER_H - 5, W, HEADER_H], fill=ACCENT)
draw.text((PAD, 38), "Executive Dashboard — Sistem Peringatan Dini Banjir DKI Jakarta",
          font=font(46, bold=True), fill=WHITE)
draw.text((PAD, 104),
          "Integrasi Prediksi Machine Learning (Spark MLlib) & Graph Analytics — DAS Ciliwung",
          font=font(28), fill=SUB)

y = HEADER_H + PAD
canvas.paste(kpi, (PAD, y)); y += kpi.size[1] + GAP
canvas.paste(cm, (PAD, y))
canvas.paste(fi, (PAD + row_w + GAP, y)); y += mid_h + GAP
canvas.paste(ts, (PAD, y))

out = os.path.join(FIG, "fig_dashboard_overview.png")
canvas.save(out, quality=95)
print("saved:", out, canvas.size)
