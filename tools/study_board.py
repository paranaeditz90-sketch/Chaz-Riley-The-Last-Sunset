"""Roda o study.py (pixel-art-studio) nos frames finais e monta o quadro-resumo do estudo.

Uso (da raiz do projeto): python3 -P tools/study_board.py
Saída: frames_estudo/study/RESUMO_estudo.png  (fora do git: contém frames de terceiros)
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SK = ".claude/skills/pixel-art-studio/scripts"
sys.path.insert(0, SK)
from pixelstudio import ramp  # noqa: E402

ST = "frames_estudo/study"
REF = "/home/user/gpt-mine/bruce-bronze-refs/character-sheets/"
TTF = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
TTFB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F = ImageFont.truetype(TTF, 15)
FB = ImageFont.truetype(TTFB, 19)
FS = ImageFont.truetype(TTF, 12)
M = {(r["who"], r["video"], r["kf"]): r for r in json.load(open(f"{ST}/measures.json"))}

# ------------------------------------------------------------------ study.py
FINAL = {"chaz": f"{ST}/chaz_2026-11-16_kf10.png", "riley": f"{ST}/riley_2026-11-16_kf20.png"}
study = {}
for who, path in FINAL.items():
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    rgb = Image.fromarray(a[..., :3]).quantize(16, method=Image.Quantize.MEDIANCUT).convert("RGB")
    q = np.dstack([np.array(rgb), np.where(a[..., 3] > 127, 255, 0).astype(np.uint8)])
    qpath = path.replace(".png", "_q16.png")
    Image.fromarray(q, "RGBA").save(qpath)
    for tag, p, extra in (("raw", path, []), ("q16", qpath, ["--save-palette", f"bruce_{who}"])):
        out = f"{ST}/study_{who}_{tag}"
        r = subprocess.run([sys.executable, "-P", f"{SK}/study.py", p, "--out", out] + extra,
                           capture_output=True, text=True)
        rep = json.load(open(f"{out}/report.json"))
        study[(who, tag)] = rep
        print(f"study.py {who}/{tag}: {rep['color_count']} cores, true {rep['true_size']}, "
              f"dark-edge {rep['edge_dark_pct']}%, dither {rep['dither_checker_pct']}%")

# ------------------------------------------------------------------ helpers
def fit(img, h):
    img = img.convert("RGBA")
    return img.resize((max(1, int(img.width * h / img.height)), h), Image.LANCZOS)


def swatches(cols, w=34, h=34, labels=False):
    im = Image.new("RGB", (len(cols) * w, h + (16 if labels else 0)), (24, 24, 28))
    d = ImageDraw.Draw(im)
    for i, c in enumerate(cols):
        d.rectangle([i * w, 0, i * w + w - 2, h - 1], fill=c)
        if labels:
            d.text((i * w, h + 1), c[1:], fill=(200, 200, 200), font=ImageFont.truetype(TTF, 8))
    return im


def section(title, items, gap=14, h_pad=10):
    tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(title, font=FB)) + 2 * h_pad
    W = max(sum(i.width for i in items) + gap * (len(items) - 1) + 2 * h_pad, tw)
    H = max(i.height for i in items) + 40
    s = Image.new("RGB", (W, H), (32, 30, 40))
    ImageDraw.Draw(s).text((h_pad, 8), title, fill=(255, 214, 120), font=FB)
    x = h_pad
    for i in items:
        s.paste(i, (x, 36), i if i.mode == "RGBA" else None)
        x += i.width + gap
    return s


def captioned(img, lines, w=None):
    tl = max(int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(ln, font=F)) for ln in lines) + 6
    w = max(w or img.width, tl)
    t = Image.new("RGB", (w, img.height + 20 * len(lines) + 4), (32, 30, 40))
    t.paste(img, (0, 0), img if img.mode == "RGBA" else None)
    d = ImageDraw.Draw(t)
    for i, ln in enumerate(lines):
        d.text((2, img.height + 2 + 20 * i), ln, fill=(235, 235, 235), font=F)
    return t


# ------------------------------------------------------------------ 1. evolução do traço
evo = [("2026-09-12", 4, "set/12: quase sem linha,", "borda pintada + luz de contra"),
       ("2026-10-10", 5, "out/10: linha fina", "azul-marinho escuro"),
       ("2026-10-23", 7, "out/23: linha PRETA grossa", ""),
       ("2026-11-16", 10, "nov/16: linha preta média,", "cor mais chapada")]
tiles = []
for d, k, l1, l2 in evo:
    r = M[("chaz", d, k)]
    a = Image.open(f"frames_estudo/{d}/kf_{k:03d}.png").convert("RGB")
    x0, y0, x1, y1 = r["box"]
    cx = x0 + int((x1 - x0) * 0.30)
    z = a.crop((cx - 50, y0 - 10, cx + 70, y0 + 110)).resize((240, 240), Image.NEAREST)
    lc = "#%02x%02x%02x" % tuple(r["line_rgb"])
    z2 = Image.new("RGB", (240, 262), (32, 30, 40)); z2.paste(z, (0, 0))
    ImageDraw.Draw(z2).rectangle([0, 244, 60, 260], fill=lc)
    ImageDraw.Draw(z2).text((66, 244), f"traço {r['line_w_px']}px {lc}", fill=(235, 235, 235), font=FS)
    tiles.append(captioned(z2, [l1, l2]))
S1 = section("1. Evolução do traço (Chaz, zoom 2x na borda da cabeça; pincel tem px fixo, não acompanha o zoom)", tiles)

# ------------------------------------------------------------------ 2. paleta + study.py
pal_items = []
for who in ("chaz", "riley"):
    crop = fit(Image.open(FINAL[who]), 200)
    sw = Image.open(f"{ST}/study_{who}_q16/swatch.png").convert("RGB")
    hue = M[(who, "2026-11-16", 10 if who == "chaz" else 20)]["hue"]
    lines = [f"{who.upper()} (nov/16) - study.py: {study[(who, 'raw')]['color_count']} cores brutas",
             f"-> 16 cores: borda escura {study[(who, 'q16')]['edge_dark_pct']}%",
             f"base {hue['base']} H{hue['base_hsv'][0]}  sombra {hue['shadow']} H{hue['shadow_hsv'][0]}",
             "=> SEM hue shift: Bruce só escurece"]
    box = Image.new("RGB", (max(crop.width + 10 + sw.width, 460), 200), (32, 30, 40))
    box.paste(crop, (0, 0), crop); box.paste(sw, (crop.width + 10, 0))
    pal_items.append(captioned(box, lines))
S2 = section("2. Paleta dos frames finais (study.py) + teste de hue shift", pal_items)

# ------------------------------------------------------------------ 3. proporções
def prop_tile(img, marks, h=330):
    img = fit(img, h)
    W = img.width + 150
    t = Image.new("RGB", (W, h + 4), (200, 200, 200))
    t.paste(img, (0, 2), img)
    d = ImageDraw.Draw(t)
    for pct, name, col in marks:
        y = 2 + int(h * pct / 100)
        d.line([(0, y), (img.width + 6, y)], fill=col, width=2)
        d.text((img.width + 10, y - 9), f"{pct}% {name}", fill=(0, 0, 0), font=FS)
    return t


def sheet_cell(path, cell, bgfn):
    from scipy import ndimage as ndi
    im = Image.open(path).convert("RGBA"); a = np.array(im).astype(int)
    x0, y0, x1, y1 = cell; sub = a[y0:y1, x0:x1]
    m = ~bgfn(sub); m = ndi.binary_opening(m, iterations=2); lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1)); m = lab == (1 + np.argmax(sizes))
    ys, xs = np.nonzero(m)
    return im.crop((x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1))


white = lambda a: (a[..., 0] > 215) & (a[..., 1] > 215) & (a[..., 2] > 215)
alpha = lambda a: a[..., 3] < 40
red, blu, grn = (220, 30, 30), (30, 60, 220), (20, 140, 40)
pt = [captioned(prop_tile(sheet_cell(REF + "chaz_sheet.png", (0, 0, 400, 437), white),
                          [(3, "topo cabeça", red), (37, "queixo", red), (72, "virilha", blu), (100, "pé", grn)]),
                ["CHAZ ~3 cabeças de altura", "cabeça 34% | tronco 35% | perna 28%", "orelha cai até ~45%"]),
      captioned(prop_tile(sheet_cell(REF + "riley_sheet.png", (100, 0, 437, 400), alpha),
                          [(3, "ponta orelha", red), (17, "topo crânio", red), (46, "queixo", red),
                           (74, "virilha", blu), (100, "pé", grn)]),
                ["RILEY: crânio 29% + orelhas 14%", "tronco 28% | perna 26%", "orelha = a silhueta dela"])]
S3 = section("3. Proporções (grade de 5% nas suas folhas; confere com Bruce 10-10)", pt)

# ------------------------------------------------------------------ 4. rampas propostas p/ o jogo
import colorsys
def hsvhex(h, s_, v):
    r, g, b = colorsys.hsv_to_rgb(h / 360, s_, v)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))
chaz_default = ramp("#1a28d8", 5, hue_shift=18)
# ajuste manual: sombra gira pro VIOLETA, luz pro CIANO, saturação cai nas pontas
chaz_r = [hsvhex(258, 0.86, 0.36), hsvhex(247, 0.88, 0.58), "#1a28d8", hsvhex(224, 0.72, 0.93), hsvhex(210, 0.50, 0.98)]
riley_r = ramp("#7e0c1c", 5, hue_shift=18, light=0.45)
shared = ["#0a0612", "#f3e6b0", "#8a4fd8", "#3a1a6a", "#f4f4f8"]
rows = [captioned(swatches(chaz_default, labels=True), ["ramp() padrão no Chaz: sombra fica azul puro", "(ele já é azul, não há pra onde girar) -> descartada"])]
for name, rp in (("Chaz", chaz_r), ("Riley", riley_r)):
    sw = swatches(rp + shared, labels=True)
    rows.append(captioned(sw, [f"{name}: 5 tons de corpo + contorno, esclera,", f"íris, pupila, marca '3' = {len(rp) + len(shared)} cores (máx. 16)"]))
S4 = section("4. Rampas propostas pro jogo (sombra gira pro frio/roxo, luz pro quente/ciano)", rows)

# ------------------------------------------------------------------ 5. elenco extra
extra = []
for d, k, lab in (("2026-09-26", 5, "cachorro laranja (09-26)"), ("2026-10-10", 17, "cavalier vermelho/branco (10-10)")):
    extra.append(captioned(fit(Image.open(f"frames_estudo/{d}/kf_{k:03d}.png"), 230), [lab]))
extra.append(captioned(fit(sheet_cell(REF + "terceiro_sheet.png", (0, 0, 256, 341),
                                      lambda a: (abs(a[..., 0] - 28) < 16) & (abs(a[..., 1] - 18) < 14) & (abs(a[..., 2] - 30) < 16)), 230),
                       ["terceiro (sua folha):", "não aparece nos vídeos"]))
S5 = section("5. Outros personagens que aparecem", extra)

# ------------------------------------------------------------------ montagem
secs = [S1, S2, S3, S4, S5]
W = max(s.width for s in secs) + 20
H = sum(s.height for s in secs) + 12 * len(secs) + 60
board = Image.new("RGB", (W, H), (18, 16, 24))
d = ImageDraw.Draw(board)
d.text((10, 12), "Estudo Bruce Bronze - 5 vídeos, 99 frames-chave (troca de cena, 720x962)", fill=(255, 255, 255), font=FB)
y = 52
for s in secs:
    board.paste(s, (10, y)); y += s.height + 12
board.save(f"{ST}/RESUMO_estudo.png")
print("board", board.size, "->", f"{ST}/RESUMO_estudo.png")
print("chaz ramp", chaz_r, "\nriley ramp", riley_r)
