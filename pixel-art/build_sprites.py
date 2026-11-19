"""Folhas de sprite do jogo, copiadas fielmente das folhas do Gemini (nada redesenhado).

Fontes (pixel-art/<nome>/fonte/):
  chaz:  chaz_gemini_v2.jpg (fundo xadrez, 4x7: frente, esquerda, direita, costas parado+andar + 3 extras)
         chaz_costas_linha_gemini.jpg (fundo verde, 1x7: costas completo; escala maior, ajustada)
  riley: riley_gemini.jpg (fundo verde, 4x7). Correr de perfil: cabeça trocada pela do andar (orelha extra
         do Gemini; conserto autorizado pelo diretor, ver tools/sheet_copy.py: trocar_cabeca)
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
from sheet_copy import (  # noqa: E402
    color_match, despeckle, fundo_verde, grid, head_cx, key_alpha, key_checker, key_green, load, place, tem_alfa,
    trocar_cabeca, trocar_rosto)

PA = os.path.join(ROOT, "pixel-art")
GAME = os.path.join(ROOT, "game", "public", "assets", "sprites")
DIRS = ["frente", "esquerda", "direita", "costas"]
NCOL = 7  # parado, andar 1-3, correr 1-3


def sheet(path, kind, nrows, ncols, scale=1.0):
    """kind: "green", "checker" ou "auto" (transparência de verdade, verde ou xadrez, o que a imagem tiver)."""
    if kind == "auto" and tem_alfa(path):
        return grid(despeckle(key_alpha(path, scale)), nrows, ncols)
    a = load(path, scale)
    if kind == "auto":
        kind = "green" if fundo_verde(a) else "checker"
    k = key_green(a) if kind == "green" else key_checker(a)
    return grid(despeckle(k), nrows, ncols)


def cor_corpo(frames):
    """Cor dominante do corpo (mediana dos pixels que não são linha nem branco/creme)."""
    px = np.concatenate([f[f[..., 3] > 0][:, :3] for f in frames]).astype(int)
    px = px[(px.max(-1) > 40) & (px.min(-1) < 150)]
    vals, cnt = np.unique(px // 8, axis=0, return_counts=True)
    top = vals[np.argmax(cnt)]
    sel = px[(px // 8 == top).all(-1)]
    return tuple(int(v) for v in np.median(sel, 0))


def extras_gemini(nome, loc, corpo):
    """Rodada 3 (4x7): linha 1 frente (piscar, olhar, gesto), 2/3 perfil esq/dir (piscar + ações), 4 frente/costas.
    Mesma escala e mesma cor da folha de locomoção."""
    path = os.path.join(PA, nome, "fonte", f"{nome}_extras_gemini.jpg")
    raw = sheet(path, "green", 4, 7)
    s = loc["frente"][0].shape[0] / raw[(0, 2)].shape[0]
    ex = sheet(path, "green", 4, 7, scale=s) if abs(s - 1) > 0.03 else raw
    c_ex = cor_corpo([ex[(0, 2)], ex[(0, 3)]])
    ex = {k: color_match(v, [((0, 0, 0), (0, 0, 0)), (c_ex, corpo)]) for k, v in ex.items()}
    return ex, s


def vida_e_acoes(rows, named, ex, corpo, gesto=None, sem=()):
    """Piscar e olhar: só os OLHOS do quadro novo vão pro quadro parado da locomoção (o corpo não pula).
    Ações: quadro inteiro do Gemini. `sem` = poses que vieram erradas e ficam de fora."""
    # só de frente: olhos fechados/de lado do Gemini colados no parado (alinha bem). De perfil o encaixe falha
    # (testado: sobra marca), então parado de lado o personagem vira pra câmera depois de uns segundos (no jogo)
    vida = [trocar_rosto(rows["frente"][0], ex[(0, 1)], corpo),
            trocar_rosto(rows["frente"][0], ex[(0, 2)], corpo),
            trocar_rosto(rows["frente"][0], ex[(0, 3)], corpo)]
    rows["vida"] = vida
    named.update({"frente_piscar": [("vida", 0)], "frente_olhar_esq": [("vida", 1)], "frente_olhar_dir": [("vida", 2)]})
    if gesto:
        rows["gesto"] = [ex[(0, c)] for c in gesto["cols"]]
        for k, cs in gesto["anims"].items():
            named[k] = [("gesto", c) for c in cs]
    acoes = ["agachar", "tapar", "susto", "pegar", "ler", "bater"]
    for r, d in ((1, "esquerda"), (2, "direita")):
        rows[f"acoes_{d}"] = [ex[(r, c)] for c in range(1, 7)]
        for i, a in enumerate(acoes):
            if f"{a}_{d}" not in sem:
                named[f"{a}_{d}"] = [(f"acoes_{d}", i)]
    rows["acoes_frente_costas"] = [ex[(3, c)] for c in range(7)]
    for i, a in enumerate(["agachar_frente", "tapar_frente", "susto_frente", "medo_frente", "sentado_frente",
                           "agachar_costas", "sentado_costas"]):
        if a not in sem:
            named[a] = [("acoes_frente_costas", i)]


def chaz():
    src = os.path.join(PA, "chaz", "fonte")
    v2 = sheet(os.path.join(src, "chaz_gemini_v2.jpg"), "checker", 4, 7)
    # linha de costas avulsa (7 quadros de uma vez): mesma altura do "costas parado" da v2 e mesma cor
    linha = os.path.join(src, "chaz_costas_linha_gemini.jpg")
    raw = sheet(linha, "green", 1, 7)
    s = v2[(3, 0)].shape[0] / raw[(0, 0)].shape[0]
    costas = sheet(linha, "green", 1, 7, scale=s)
    costas = {k: color_match(v, [((1, 1, 2), (1, 1, 6)), ((24, 51, 217), (26, 52, 225))]) for k, v in costas.items()}
    rows = {}
    for r, d in enumerate(DIRS[:3]):
        rows[d] = [v2[(r, c)] for c in range(7)]
    # de frente o Gemini fez andar (2 de 3) e correr (3 de 3) de olho fechado: rosto do parado, mesma folha
    AZUL = (26, 52, 225)
    for c in (1, 2, 4, 5, 6):
        rows["frente"][c] = trocar_rosto(v2[(0, c)], v2[(0, 0)], AZUL)
    rows["costas"] = [costas[(0, c)] for c in range(7)]
    rows["extras"] = [v2[(3, 4)], v2[(3, 5)], v2[(3, 6)]]
    named = {"comemorar": [("extras", 0)], "extra_braços": [("extras", 1)], "extra_passo": [("extras", 2)]}
    ex, se = extras_gemini("chaz", rows, AZUL)
    vida_e_acoes(rows, named, ex, AZUL,
                 gesto={"cols": [4, 5, 6], "anims": {"gesto": [0, 1, 1, 2]}})
    # piscada de frente: rosto de olho fechado da própria v2 (andar 1) fica mais fiel que o da folha nova
    rows["vida"][0] = trocar_rosto(v2[(0, 0)], v2[(0, 1)], AZUL)
    return rows, named, f"costas: linha avulsa {s:.3f}x; poses extras {se:.3f}x"


def simple(nome):
    fr = sheet(os.path.join(PA, nome, "fonte", f"{nome}_gemini.jpg"), "green", 4, 7)
    return {d: [fr[(r, c)] for c in range(7)] for r, d in enumerate(DIRS)}


def riley():
    rows = simple("riley")
    for d in ("esquerda", "direita"):
        for c, w in ((4, 1), (5, 2), (6, 3)):
            rows[d][c] = trocar_cabeca(rows[d][c], rows[d][w])
    named = {}
    corpo = cor_corpo([rows["frente"][0]])
    ex, se = extras_gemini("riley", rows, corpo)
    # o Gemini deu à Riley os gestos do Chaz (celular) e orelha redonda em 3 poses de frente: ficam de fora
    vida_e_acoes(rows, named, ex, corpo, sem=("agachar_frente", "tapar_frente", "medo_frente"))
    return rows, named, f"correr de perfil com cabeça do andar; poses extras {se:.3f}x (sem gesto, sem 3 de frente)"


def nevoa():
    rows = simple("nevoa")
    named = {}
    corpo = cor_corpo([rows["frente"][0]])
    ex, se = extras_gemini("nevoa", rows, corpo)
    vida_e_acoes(rows, named, ex, corpo,
                 gesto={"cols": [4, 5, 6], "anims": {"gesto": [0], "deitado": [1], "acordando": [2]}})
    return rows, named, f"poses extras {se:.3f}x"


chars = {"chaz": chaz(), "riley": riley(), "nevoa": nevoa()}

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

for nome, (rows, named, note) in chars.items():
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
        anims[f"{d}_andar"] = {"frames": [base + i for i in (1, 2, 3, 2)], "fps": 8, "repeat": -1}
        anims[f"{d}_correr"] = {"frames": [base + i for i in (4, 5, 6, 5)], "fps": 12, "repeat": -1}
    for k, refs in named.items():
        fps = 12 if k.endswith("_piscar") else 3 if k == "gesto" else 4
        anims[k] = {"frames": [order.index(r) * NCOL + c for r, c in refs], "fps": fps, "repeat": 0}
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
