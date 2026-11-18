"""Estudo dos frames de referência (Bruce Bronze) -> números + quadros visuais.

Mede, por personagem e por vídeo:
  * espessura do traço (px a 720p e em permil da largura da cabeça, pra não depender do zoom)
  * cor do traço (preto puro? escuro colorido?)
  * paleta de 16 cores só dos pixels do personagem
  * hue shift: a sombra muda de matiz em relação à cor base?
  * proporções (cabeças de altura) nos frames em pé

Uso: python3 -P tools/study_refs.py   (roda a partir da raiz do projeto)
Saída: frames_estudo/study/  (fora do git: material de terceiros)
"""
import colorsys
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

FR = "frames_estudo"
OUT = os.path.join(FR, "study")
os.makedirs(OUT, exist_ok=True)
FONT = ImageFont.load_default(size=15)


def load(d, k):
    return np.array(Image.open(f"{FR}/{d}/kf_{k:03d}.png").convert("RGB")).astype(int)


def fill_mask(a, who):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if who == "chaz":
        m = (b > r + 60) & (b > g + 40) & (b > 90)
    else:  # riley: vermelho escuro, sem pegar o laranja/vermelho vivo do fundo
        m = (r > 70) & (r < 190) & (g < 50) & (b < 80) & (r > 2.2 * g) & (r > 1.4 * b)
    m = ndi.binary_opening(m, iterations=1)
    lab, n = ndi.label(m)
    if n == 0:
        return m
    sizes = ndi.sum(m, lab, range(1, n + 1))
    keep = np.isin(lab, 1 + np.argsort(sizes)[::-1][:1])  # maior componente
    return keep


def silhouette(fill):
    s = ndi.binary_closing(fill, iterations=6)
    s = ndi.binary_fill_holes(s)
    return ndi.binary_dilation(s, iterations=4)  # inclui o contorno


def line_stats(a, fill):
    # traço = pixel escuro em VALOR (max canal), não em luminância:
    # o azul do Chaz tem luminância baixa e era contado como traço.
    val = a.max(axis=2)
    band = ndi.binary_dilation(fill, iterations=14) & ~fill
    line = (val < 80) & band
    if line.sum() < 50:
        return None
    edt = ndi.distance_transform_edt(line)
    ridge = (edt >= 1) & (edt == ndi.maximum_filter(edt, size=3)) & line
    widths = 2 * edt[ridge] - 1
    core = line & (edt >= 1.5)
    col = np.median(a[core], axis=0) if core.sum() > 20 else np.median(a[line], axis=0)
    return float(np.median(widths)), [int(c) for c in col]


def head_width(fill):
    ys, xs = np.nonzero(fill)
    top, bot = ys.min(), ys.max()
    rows = range(top, top + int((bot - top) * 0.45))
    return max((fill[y].sum() for y in rows), default=1)


def palette16(a, sil):
    px = a[sil].astype(np.uint8)
    im = Image.fromarray(px.reshape(1, -1, 3), "RGB")
    q = im.quantize(16, method=Image.Quantize.MEDIANCUT)
    pal = np.array(q.getpalette()[:48]).reshape(16, 3)
    counts = np.bincount(np.array(q).ravel(), minlength=16)
    order = np.argsort(counts)[::-1]
    return [("#%02x%02x%02x" % tuple(pal[i]), round(100 * counts[i] / counts.sum(), 1)) for i in order if counts[i]]


def hsv(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return round(h * 360), round(s, 2), round(v, 2)


def hue_shift(pal, who):
    """matiz da cor base (mais usada da família) vs a sombra (mais escura da família)."""
    fam = [(c, p) for c, p in pal if (hsv(c)[2] > 0.18 and hsv(c)[1] > 0.35)]
    fam = [(c, p) for c, p in fam if (200 <= hsv(c)[0] <= 270) == (who == "chaz")]
    if len(fam) < 2:
        return None
    base = fam[0][0]
    dark = min(fam, key=lambda t: hsv(t[0])[2])[0]
    light = max(fam, key=lambda t: hsv(t[0])[2])[0]
    return dict(base=base, base_hsv=hsv(base), shadow=dark, shadow_hsv=hsv(dark),
                light=light, light_hsv=hsv(light))


def proportions(sil):
    ys, xs = np.nonzero(sil)
    top, bot = ys.min(), ys.max()
    H = bot - top + 1
    widths = np.array([sil[y].sum() for y in range(top, bot + 1)])
    lo, hi = int(H * 0.25), int(H * 0.60)
    neck = lo + int(np.argmin(widths[lo:hi]))
    return dict(total_h=int(H), head_h=int(neck), heads_tall=round(H / max(neck, 1), 2),
                head_w=int(widths[:neck].max()), body_w=int(widths[neck:].max()),
                neck_y=int(top + neck), top=int(top), bot=int(bot))


# --------------------------------------------------------------------------
# frames escolhidos (data, keyframe, personagem, em_pé?)
# --------------------------------------------------------------------------
PICKS = [
    ("2026-09-12", 4, "chaz", False), ("2026-09-12", 4, "riley", False),
    ("2026-09-26", 12, "riley", False),
    ("2026-10-10", 5, "chaz", False), ("2026-10-10", 16, "chaz", True),
    ("2026-10-23", 7, "chaz", False), ("2026-10-23", 16, "riley", False),
    ("2026-11-16", 10, "chaz", False), ("2026-11-16", 20, "riley", False),
    ("2026-11-16", 24, "chaz", True),
]

results = []
for d, k, who, standing in PICKS:
    a = load(d, k)
    fill = fill_mask(a, who)
    sil = silhouette(fill)
    hw = head_width(fill)
    ls = line_stats(a, fill)
    pal = palette16(a, sil)
    rec = dict(video=d, kf=k, who=who, fill_px=int(fill.sum()), head_w_px=int(hw),
               line_w_px=round(ls[0], 1) if ls else None,
               line_w_permil=round(1000 * ls[0] / hw, 1) if ls else None,
               line_rgb=ls[1] if ls else None, palette=pal, hue=hue_shift(pal, who))
    if standing:
        rec["prop"] = proportions(sil)
    # recorte do personagem (fundo removido) pro study.py e pros quadros
    ys, xs = np.nonzero(sil)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    rgba = np.dstack([a.astype(np.uint8), (sil * 255).astype(np.uint8)])
    crop = Image.fromarray(rgba, "RGBA").crop(box)
    name = f"{who}_{d}_kf{k:02d}"
    crop.save(f"{OUT}/{name}.png")
    rec["crop"] = f"{OUT}/{name}.png"
    rec["box"] = [int(v) for v in box]
    results.append(rec)
    print(f"{name:28s} head_w={hw:4d}px  line={rec['line_w_px']}px ({rec['line_w_permil']}‰)  "
          f"line_rgb={rec['line_rgb']}  " + (f"prop={rec['prop']}" if standing else ""))

json.dump(results, open(f"{OUT}/measures.json", "w"), indent=1)
print("ok ->", f"{OUT}/measures.json")
