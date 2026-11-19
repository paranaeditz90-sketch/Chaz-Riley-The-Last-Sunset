"""Folhas de sprite do jogo, copiadas fielmente das folhas do Gemini (nada redesenhado).

Fontes (pixel-art/<nome>/fonte/):
  chaz:  chaz_gemini_v2.jpg (fundo xadrez, 4x7: frente, esquerda, direita, costas parado+andar + 3 extras)
         chaz_costas_correr_gemini.jpg (fundo verde, 1x4: costas parado + correr x3; escala maior, ajustada)
  riley: riley_gemini.jpg (fundo verde, 4x7)
  nevoa: nevoa_gemini.jpg (fundo verde, 4x7)

Saída por personagem: pixel-art/<nome>/<nome>_folha.png + preview + GIFs,
e pro jogo: game/public/assets/sprites/<nome>.png + sprites.json (tamanho do quadro e animações).

Rodar da raiz do projeto:  python3 -P pixel-art/build_sprites.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from sheet_copy import color_match, despeckle, grid, head_cx, key_checker, key_green, load, place  # noqa: E402

PA = os.path.join(ROOT, "pixel-art")
GAME = os.path.join(ROOT, "game", "public", "assets", "sprites")
DIRS = ["frente", "esquerda", "direita", "costas"]
NCOL = 7  # parado, andar 1-3, correr 1-3


def sheet(path, kind, nrows, ncols, scale=1.0):
    a = load(path, scale)
    k = key_green(a) if kind == "green" else key_checker(a)
    return grid(despeckle(k), nrows, ncols)


def chaz():
    src = os.path.join(PA, "chaz", "fonte")
    v2 = sheet(os.path.join(src, "chaz_gemini_v2.jpg"), "checker", 4, 7)
    # folha avulsa do correr de costas: mesma altura do "costas parado" da v2 e mesma cor
    raw = sheet(os.path.join(src, "chaz_costas_correr_gemini.jpg"), "green", 1, 4)
    s = v2[(3, 0)].shape[0] / raw[(0, 0)].shape[0]
    run = sheet(os.path.join(src, "chaz_costas_correr_gemini.jpg"), "green", 1, 4, scale=s)
    run = {k: color_match(v, [((1, 1, 2), (1, 1, 6)), ((14, 44, 231), (26, 51, 223))]) for k, v in run.items()}
    rows = {}
    for r, d in enumerate(DIRS[:3]):
        rows[d] = [v2[(r, c)] for c in range(7)]
    rows["costas"] = [v2[(3, c)] for c in range(4)] + [run[(0, c)] for c in (1, 2, 3)]
    rows["extras"] = [v2[(3, 4)], v2[(3, 5)], v2[(3, 6)]]
    extras = {"comemorar": [0], "extra_braços": [1], "extra_passo": [2]}
    return rows, extras, f"correr de costas: folha avulsa reduzida {s:.3f}x"


def simple(nome):
    fr = sheet(os.path.join(PA, nome, "fonte", f"{nome}_gemini.jpg"), "green", 4, 7)
    return {d: [fr[(r, c)] for c in range(7)] for r, d in enumerate(DIRS)}, {}, ""


chars = {"chaz": chaz(), "riley": simple("riley"), "nevoa": simple("nevoa")}

# célula comum: cabe o maior quadro dos três com a cabeça no centro
left = max(head_cx(f) for rows, _, _ in chars.values() for fs in rows.values() for f in fs)
right = max(f.shape[1] - head_cx(f) for rows, _, _ in chars.values() for fs in rows.values() for f in fs)
tall = max(f.shape[0] for rows, _, _ in chars.values() for fs in rows.values() for f in fs)
half = int(np.ceil(max(left, right))) + 4
CW, CH = 2 * half, tall + 8
CW, CH = CW + CW % 2, CH + CH % 2
GROUND, CX = CH - 4, half
print(f"célula {CW}x{CH}, chão y={GROUND}")

os.makedirs(GAME, exist_ok=True)
meta = {"frameWidth": CW, "frameHeight": CH, "originY": GROUND / CH, "characters": {}}

for nome, (rows, extras, note) in chars.items():
    order = list(rows.keys())
    folha = Image.new("RGBA", (CW * NCOL, CH * len(order)), (0, 0, 0, 0))
    cells = {}
    for r, d in enumerate(order):
        for c, f in enumerate(rows[d]):
            im = place(f, CW, CH, GROUND, CX)
            cells[(d, c)] = im
            folha.alpha_composite(Image.fromarray(im, "RGBA"), (c * CW, r * CH))
    out = os.path.join(PA, nome)
    folha.save(os.path.join(out, f"{nome}_folha.png"))
    folha.save(os.path.join(GAME, f"{nome}.png"))
    prev = Image.new("RGBA", folha.size, (235, 235, 240, 255))
    prev.alpha_composite(folha)
    prev.convert("RGB").save(os.path.join(out, "preview_folha.png"))

    anims = {}
    for d in DIRS:
        base = order.index(d) * NCOL
        anims[f"{d}_parado"] = {"frames": [base], "fps": 1, "repeat": 0}
        anims[f"{d}_andar"] = {"frames": [base + i for i in (1, 2, 3, 2)], "fps": 6.67, "repeat": -1}
        anims[f"{d}_correr"] = {"frames": [base + i for i in (4, 5, 6, 5)], "fps": 10, "repeat": -1}
    if "extras" in order:
        base = order.index("extras") * NCOL
        for k, fs in extras.items():
            anims[k] = {"frames": [base + i for i in fs], "fps": 1, "repeat": 0}
    meta["characters"][nome] = {"image": f"assets/sprites/{nome}.png", "rows": order, "anims": anims}

    def gif(name, keys, ms):
        frs = []
        for k in keys:
            bg = Image.new("RGBA", (CW, CH), (42, 38, 51, 255))
            bg.alpha_composite(Image.fromarray(cells[k], "RGBA"))
            frs.append(bg.convert("P", palette=Image.ADAPTIVE))
        frs[0].save(os.path.join(out, name), save_all=True, append_images=frs[1:], duration=ms, loop=0, disposal=2)

    for d in DIRS:
        gif(f"gif_andar_{d}.gif", [(d, i) for i in (1, 2, 3, 2)], 150)
        gif(f"gif_correr_{d}.gif", [(d, i) for i in (4, 5, 6, 5)], 100)
    print(nome, "ok", folha.size, note)

json.dump(meta, open(os.path.join(GAME, "sprites.json"), "w"), ensure_ascii=False, indent=1)
print("jogo:", GAME)
