# -*- coding: utf-8 -*-
"""Komposit panel Graph Analytics (network + pagerank + indegree) untuk Gambar 7.3."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figures")
BG = (14, 17, 23); HEADER_BG = (10, 25, 41); ACCENT = (30, 136, 229)
WHITE = (227, 242, 253); SUB = (144, 202, 249)


def load(n): return Image.open(os.path.join(FIG, n)).convert("RGB")
def font(s, b=False):
    for c in (["C:/Windows/Fonts/segoeuib.ttf"] if b else ["C:/Windows/Fonts/segoeui.ttf"]):
        if os.path.exists(c): return ImageFont.truetype(c, s)
    return ImageFont.load_default()
def fit(img, w):
    ww, hh = img.size; return img.resize((w, int(hh * w / ww)), Image.LANCZOS)


W, PAD, HEADER_H, GAP = 2000, 40, 150, 30
net = load("fig_network.png")
pr = load("fig_pagerank.png")
ind = load("fig_indegree.png")

left_w = int((W - 2 * PAD - GAP) * 0.56)
right_w = (W - 2 * PAD - GAP) - left_w
net = fit(net, left_w)
pr = fit(pr, right_w)
ind = fit(ind, right_w)
right_h = pr.size[1] + GAP + ind.size[1]
body_h = max(net.size[1], right_h)
total_h = HEADER_H + PAD + body_h + PAD

canvas = Image.new("RGB", (W, total_h), BG)
d = ImageDraw.Draw(canvas)
d.rectangle([0, 0, W, HEADER_H], fill=HEADER_BG)
d.rectangle([0, HEADER_H - 5, W, HEADER_H], fill=ACCENT)
d.text((PAD, 34), "Graph Analytics — Episentrum & Leher Botol Rambatan Air",
       font=font(44, True), fill=WHITE)
d.text((PAD, 92), "Analisis topologi DAS Ciliwung: PageRank & In-Degree Centrality",
       font=font(26), fill=SUB)

y = HEADER_H + PAD
canvas.paste(net, (PAD, y + max(0, (body_h - net.size[1]) // 2)))
rx = PAD + left_w + GAP
canvas.paste(pr, (rx, y))
canvas.paste(ind, (rx, y + pr.size[1] + GAP))

out = os.path.join(FIG, "fig_graph_overview.png")
canvas.save(out, quality=95)
print("saved:", out, canvas.size)
