"""Chaz — folha final a partir da folha v2 que o LM gerou no Gemini (aprovada: "ficou MUITO melhor").

1. tools/restore_gemini.py devolve a folha ao grid real. A arte do Gemini tem densidade de ~2.34 px
   por pixel (grid 512): em 256 a linha da orelha (azul-escura, meio pixel) sumia. Em 512 ela volta.
   Olho e "3" NÃO são aproveitados: viram azul e são redesenhados aqui à mão.
2. Aqui: recorta os 28 frames, alinha (bolinha do topo + pé), apaga restos de olho sem tocar o
   contorno, e carimba o MESMO olho em todo frame de movimento (íris centralizada = não fica vesgo),
   e o "3". A boca do original é mantida.
3. Folha do jogo: frente | esquerda | direita | costas (parado, andar 3, correr 3) + extras. Quadro 96x96.

Rodar (da raiz do projeto):
  python3 -P tools/restore_gemini.py pixel-art/chaz/fonte/chaz_gemini_v2.jpg pixel-art/chaz/fonte/chaz_restaurado.png 512 0.30 110
  python3 -P pixel-art/chaz/build.py
"""
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "fonte", "chaz_restaurado.png")
DET = os.path.join(HERE, "fonte", "chaz_restaurado_detalhes.json")
CELL, GROUND, CX = 96, 90, 48

BLUE = (42, 59, 232, 255)
LEG = {"w": (255, 255, 255, 255), "p": (138, 79, 216, 255), "a": (58, 26, 106, 255), "k": (0, 0, 0, 255)}

# ------------------------------------------------------------------ carimbos (desenhados à mão, 8x9)
# íris oval (cantos brancos) com brilho e pupila 1x2 — centralizada de frente, pra frente de perfil
EYE_FRONT = ["..kkkk..", ".kwwwwk.", "kwwppwwk", "kwpwppwk", "kwppapwk", "kwppapwk", "kwwppwwk", ".kwwwwk.", "..kkkk.."]
EYE_RIGHT = ["..kkkk..", ".kwwwwk.", "kwwwppwk", "kwwpwppk", "kwwppapk", "kwwppapk", "kwwwppwk", ".kwwwwk.", "..kkkk.."]
EYE_LEFT = [r[::-1] for r in EYE_RIGHT]
EYE_HALF = ["........", "........", "........", "kkkkkkkk", "kwppapwk", "kwwppwwk", ".kwwwwk.", "..kkkk..", "........"]
EYE_CLOSED = ["........", "........", "........", "........", "k......k", ".k....k.", "..kkkk..", "........", "........"]
THREE = ["wwwwww", "wwwwww", "....ww", "....ww", "..wwww", "..wwww", "....ww", "....ww", "wwwwww", "wwwwww"]


def runs(v, minlen=16):
    out, s = [], None
    for i, x in enumerate(v):
        if x and s is None:
            s = i
        if not x and s is not None:
            out.append((s, i - 1)); s = None
    if s is not None:
        out.append((s, len(v) - 1))
    return [q for q in out if q[1] - q[0] > minlen]


def stamp(img, rows, x, y):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in LEG and 0 <= x + i < CELL and 0 <= y + j < CELL:
                img[y + j, x + i] = LEG[ch]


def interior(img, x, y):
    """Pixel opaco com os 4 vizinhos opacos = não é contorno da silhueta."""
    if not img[y, x, 3]:
        return False
    return all(0 <= x + dx < CELL and 0 <= y + dy < CELL and img[y + dy, x + dx, 3]
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))


def clear_round(img, cx, cy, rx, ry):
    """Apaga restos (anel do olho, olho fechado, ^^) num oval pequeno, sem tocar o contorno da silhueta."""
    todo = []
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if 0 <= x < CELL and 0 <= y < CELL and ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 and interior(img, x, y):
                todo.append((x, y))
    for x, y in todo:
        img[y, x] = BLUE


def clear_rect(img, x0, y0, x1, y1):
    """Apaga restos numa faixa retangular, sem tocar o contorno da silhueta."""
    todo = [(x, y) for y in range(int(round(y0)), int(round(y1)) + 1) for x in range(int(round(x0)), int(round(x1)) + 1)
            if 0 <= x < CELL and 0 <= y < CELL and interior(img, x, y)]
    for x, y in todo:
        img[y, x] = BLUE


# ------------------------------------------------------------------ recorte e alinhamento
sheet = np.array(Image.open(SRC).convert("RGBA"))
det = json.load(open(DET))
op = sheet[..., 3] > 0
COLS, ROWS_ = runs(op.any(axis=0)), runs(op.any(axis=1))
assert len(COLS) == 7 and len(ROWS_) == 4, (COLS, ROWS_)

frames = {}
for r, (y0, y1) in enumerate(ROWS_):
    for c, (x0, x1) in enumerate(COLS):
        crop = sheet[y0:y1 + 1, x0:x1 + 1]
        o = crop[..., 3] > 0
        ys = np.nonzero(o.any(axis=1))[0]
        top, bot = ys.min(), ys.max()
        xs = np.nonzero(o[top + 1:top + 5].any(axis=0))[0]          # bolinha do topo = âncora horizontal
        hcx = (xs.min() + xs.max()) / 2
        dx, dy = int(round(CX - hcx)), GROUND - bot
        img = np.zeros((CELL, CELL, 4), np.uint8)
        h, w = crop.shape[:2]
        yy0, xx0 = max(0, dy), max(0, dx)
        img[yy0:min(CELL, h + dy), xx0:min(CELL, w + dx)] = crop[yy0 - dy:min(CELL, h + dy) - dy, xx0 - dx:min(CELL, w + dx) - dx]
        wh = [dict(cx=(d["x0"] + d["x1"]) / 2 - x0 + dx, cy=(d["y0"] + d["y1"]) / 2 - y0 + dy,
                   w=d["x1"] - d["x0"] + 1, h=d["y1"] - d["y0"] + 1, n=d["n"])
              for d in det["whites"] if x0 - 3 <= d["x0"] <= x1 + 3 and y0 - 3 <= d["y0"] <= y1 + 3]
        frames[(r, c)] = dict(img=img, top=top + dy, wh=wh)


def eyes_of(f):
    return sorted([d for d in f["wh"] if f["top"] + 14 <= d["cy"] <= f["top"] + 34 and d["n"] >= 15], key=lambda d: d["cx"])


def three_of(f):
    c = [d for d in f["wh"] if d["cy"] > f["top"] + 34]
    if not c:
        return None
    return sum(d["cx"] * d["n"] for d in c) / sum(d["n"] for d in c), sum(d["cy"] * d["n"] for d in c) / sum(d["n"] for d in c)


REF = {}
for r in (0, 1, 2):
    f = frames[(r, 0)]
    REF[r] = dict(eyes=[(d["cx"], d["cy"] - f["top"]) for d in eyes_of(f)], three=three_of(f), top=f["top"])
REF[3] = REF[0]


def face(r, c, mode, img=None):
    f = frames[(r, c)]
    img = f["img"].copy() if img is None else img
    ref, top = REF[r], f["top"]
    de = eyes_of(f)
    centers = [(d["cx"], d["cy"]) for d in de] if len(de) == len(ref["eyes"]) else [(x, y + top) for x, y in ref["eyes"]]
    if mode is not None:
        E = {"open": EYE_FRONT if r in (0, 3) else (EYE_LEFT if r == 1 else EYE_RIGHT),
             "half": EYE_HALF, "closed": EYE_CLOSED}[mode]
        # limpa uma FAIXA cobrindo os dois olhos (restos de anel/olho fechado ficam entre e ao lado deles)
        xs, ys = [x for x, _ in centers], [y for _, y in centers]
        clear_rect(img, min(xs) - 8, sum(ys) / len(ys) - 5, max(xs) + 8, sum(ys) / len(ys) + 5)
        for (ex, ey) in centers:
            stamp(img, E, int(round(ex - 3.5)), int(round(ey - 4)))
    t = three_of(f) or (ref["three"][0], ref["three"][1] - ref["top"] + top)
    x, y = int(round(t[0] - 3)), int(round(t[1] - 5))
    clear_round(img, t[0], t[1], 4.5, 6.0)
    stamp(img, THREE, x, y)
    return img


OUT = {}
for c in range(7):
    OUT[("frente", c)] = face(0, c, "open")
    OUT[("esquerda", c)] = face(1, c, "open")
    OUT[("direita", c)] = face(2, c, "open")
for c in range(4):
    OUT[("costas", c)] = frames[(3, c)]["img"]
for c, src in ((4, 1), (5, 2), (6, 3)):            # o Gemini não fez correr de costas: usa o andar, mais rápido
    OUT[("costas", c)] = frames[(3, src)]["img"]
OUT[("extras", 0)] = face(0, 0, "half")             # piscar
OUT[("extras", 1)] = face(0, 0, "closed")
OUT[("extras", 2)] = face(3, 4, None)               # comemorar (rosto ^^ e boca do original)
OUT[("extras", 3)] = face(3, 5, None)               # calmo, olho fechado (original)
OUT[("extras", 4)] = face(3, 6, None)
ROWS = ["frente", "esquerda", "direita", "costas", "extras"]

if __name__ == "__main__":
    os.chdir(HERE)
    folha = Image.new("RGBA", (CELL * 7, CELL * 5), (0, 0, 0, 0))
    for (row, c), im in OUT.items():
        folha.alpha_composite(Image.fromarray(im, "RGBA"), (c * CELL, ROWS.index(row) * CELL))
    folha.save("chaz_folha_1x.png")
    Z = 3
    prev = Image.new("RGBA", folha.size, (250, 250, 250, 255)); prev.alpha_composite(folha)
    prev.resize((folha.width * Z, folha.height * Z), Image.NEAREST).save("preview_folha.png")

    def gif(name, keys, ms):
        fr = []
        for k in keys:
            bg = Image.new("RGBA", (CELL, CELL), (42, 38, 51, 255)); bg.alpha_composite(Image.fromarray(OUT[k], "RGBA"))
            fr.append(bg.resize((CELL * Z, CELL * Z), Image.NEAREST).convert("P", palette=Image.ADAPTIVE))
        fr[0].save(name, save_all=True, append_images=fr[1:], duration=ms, loop=0, disposal=2)

    for row in ("frente", "esquerda", "direita", "costas"):
        gif(f"gif_andar_{row}.gif", [(row, i) for i in (1, 2, 3, 2)], 150)
        gif(f"gif_correr_{row}.gif", [(row, i) for i in (4, 5, 6, 5)], 100)
    gif("gif_parado_piscando.gif", [("frente", 0)] * 8 + [("extras", 0), ("extras", 1), ("extras", 0)], 150)
    gif("gif_comemorar.gif", [("frente", 0), ("extras", 2), ("extras", 2), ("frente", 0)], 250)
    gif("gif_calmo.gif", [("extras", 3), ("extras", 4)], 500)
    print("ok", folha.size)
