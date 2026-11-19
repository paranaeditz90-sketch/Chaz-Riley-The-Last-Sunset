"""Chaz — mini pixel art fofo, desenhado pixel a pixel (templates em texto). Sem conversor.

Pedido do LM: fofo, "mini pixel art", orelhas menores; a folha de referência é base, não molde.
Quadro 32x32, personagem ~24 px (cabeça ~55%). Layout igual ao da referência:
4 linhas (frente, esquerda, direita, costas) x 7 frames (1 parado, 2-4 andar, 5-7 correr).

Legenda dos templates:
  B base  S sombra  H brilho  E olho  W brilho do olho / marca "3"  P bochecha  N nariz/boca  . vazio
Rodar: cd pixel-art/chaz && python3 -P build.py
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = 32
GROUND = 28                       # última linha dos pés

# paleta (7 cores): sombra gira pro violeta, brilho pro ciano (hue shift)
COL = {
    "B": "#2a44f0",   # azul do Chaz
    "S": "#2a22b4",   # sombra (violeta)
    "H": "#7d9bff",   # brilho (ciano claro)
    "O": "#140f3c",   # contorno índigo (mais macio que preto)
    "E": "#140f3c",   # olho
    "N": "#140f3c",   # nariz/boca
    "W": "#ffffff",   # brilho do olho e "3"
    "P": "#ff8fbf",   # bochecha
}
RGBA = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) + (255,) for k, v in COL.items()}

# ------------------------------------------------------------------ templates
HEAD_FRONT = [
    ".....BBBBB.....",
    "...BHHBBBBBB...",
    "..BHHBBBBBBBB..",
    ".BBBBBBBBBBBBB.",
    ".BBBBBBBBBBBBB.",
    "BBBBBBBBBBBBBBB",
    "BBBWEBBBBBWEBBB",
    "BBBEEBBBBBEEBBB",
    "BBBEEBBBBBEEBBS",
    "BBPPBBBNBBBPPBS",
    ".BBBBBNBNBBBBS.",
    "..BBBBBBBBBBS..",
    "....BBBBBSS....",
]
HEAD_BACK = [
    ".....BBBBB.....",
    "...BHHBBBBBB...",
    "..BHHBBBBBBBB..",
    ".BBBBBBBBBBBBB.",
    ".BBBBBBBBBBBBB.",
    "BBBBBBBBBBBBBBB",
    "BBBBBBBBBBBBBBB",
    "BBBBBBBBBBBBBBB",
    "BBBBBBBBBBBBBBS",
    "BBBBBBBBBBBBBBS",
    ".BBBBBBBBBBBBS.",
    "..BBBBBBBBBBS..",
    "....BBBBBSS....",
]
EAR = [        # orelha caída, 3 de largura, abraçando a cabeça (desenhada por cima, em sombra)
    "SS.",
    "SSS",
    "SSS",
    "SSS",
    "SSS",
    "SSS",
    "SSS",
    "SS.",
    ".S.",
]
HEAD_SIDE = [  # olhando pra direita
    "....BBBBBB......",
    "..BHHBBBBBBB....",
    ".BHHBBBBBBBBB...",
    ".BBBBBBBBBBBBB..",
    "BBBBBBBBBBBBBB..",
    "BBBBBBBBBBBBBBB.",
    "BBBBBBBBBBBWEBB.",
    "BBBBBBBBBBBEEBB.",
    "BBBBBBBBBBBEEBBB",
    "BBBBBBBBBBPPBBBN",
    ".BBBBBBBBBBBBNB.",
    "..BBBBBBBBBBBS..",
    "....BBBBBBBSS...",
]
EAR_SIDE = [   # orelha de perfil, no meio-trás da cabeça
    ".SSS",
    "SSSS",
    "SSSS",
    "SSSS",
    "SSSS",
    "SSSS",
    "SSSS",
    "SSS.",
    ".SS.",
]
BODY_FRONT = [
    ".BBBBBBB.",
    "BBBBBBBBS",
    "BBBWWWBBS",
    "BBBBBWBBS",
    "BBBBWWBBS",
    "BBBBBWBBS",
    ".BBWWWBS.",
]
BODY_BACK = [
    ".BBBBBBB.",
    "BBBBBBBBS",
    "BBBBBBBBS",
    "BBBBBBBBS",
    "BBBBBBBBS",
    "BBBBBBBBS",
    ".BBBBBBS.",
]
BODY_SIDE = [  # o pedaço do "3" aparece na frente do peito
    ".BBBBBB.",
    "BBBBBBBB",
    "BBBBBWWB",
    "BBBBBBWB",
    "BBBBBWWB",
    "BBBBBBWB",
    ".BBBSWW.",
]


# ------------------------------------------------------------------ desenho
class Cel:
    def __init__(self):
        self.a = np.zeros((CELL, CELL, 4), np.uint8)

    def px(self, x, y, k):
        if 0 <= x < CELL and 0 <= y < CELL:
            self.a[y, x] = RGBA[k]

    def stamp(self, rows, ox, oy, flip=False):
        for j, row in enumerate(rows):
            if flip:
                row = row[::-1]
            for i, ch in enumerate(row):
                if ch != ".":
                    self.px(ox + i, oy + j, ch)

    def rect(self, x0, y0, x1, y1, k):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, k)

    def outline(self):
        op = self.a[..., 3] > 0
        ring = np.zeros_like(op)
        ring[1:, :] |= op[:-1, :]; ring[:-1, :] |= op[1:, :]
        ring[:, 1:] |= op[:, :-1]; ring[:, :-1] |= op[:, 1:]
        ring &= ~op
        self.a[ring] = RGBA["O"]

    def image(self):
        return Image.fromarray(self.a, "RGBA")


def legs_front(c, bx, top, lifts, spread=0):
    """Duas perninhas de 3px; pé levantado encurta a perna. Pé no chão alarga 1px pra fora."""
    for (x0, side), lift in zip(((bx + 1 - spread, -1), (bx + 5 + spread, 1)), lifts):
        bottom = GROUND - lift
        c.rect(x0, top, x0 + 2, bottom, "B")
        c.px(x0 + 2, bottom, "S")
        if lift == 0:
            c.px(x0 + (0 if side < 0 else 2) + side, bottom, "B")   # pezinho


def arms_front(c, bx, by, mode):
    for side, x in ((-1, bx - 2), (1, bx + 9)):
        if mode == "down":
            c.rect(x, by + 2, x + 1, by + 4, "B"); c.px(x + (1 if side < 0 else 0), by + 4, "S")
        elif mode in ("swingL", "swingR"):
            up = (mode == "swingL") == (side < 0)
            c.rect(x, by + 2 - up, x + 1, by + 4 - up, "B")
        elif mode == "out":
            xo = x - 1 if side < 0 else x
            c.rect(xo, by + 1, xo + 2, by + 2, "B"); c.px(xo + 1, by + 2, "S")


def front(p, back=False):
    c = Cel()
    by = p.get("by", 0)
    hx, hy = 8, 7 + by
    bx, bty = 11, 19 + by
    legs_front(c, bx, bty + 7, (p.get("liftL", 0), p.get("liftR", 0)), p.get("spread", 0))
    c.stamp(BODY_BACK if back else BODY_FRONT, bx, bty)
    arms_front(c, bx, bty, p.get("arms", "down"))
    if back:                                                    # rabinho: tufo pra cima, pro lado (abana)
        w = p.get("wag", 0)
        for (x, y) in ((bx + 9, bty + 6), (bx + 10, bty + 5), (bx + 10 + w, bty + 4), (bx + 11 + w, bty + 3)):
            c.px(x, y, "B")
        c.px(bx + 11 + w, bty + 2, "B")
    c.stamp(HEAD_BACK if back else HEAD_FRONT, hx, hy)
    e = p.get("ear", 0)
    c.stamp(EAR, hx - 1, hy + 3 + e)
    c.stamp(EAR, hx + 13, hy + 3 + e, flip=True)
    tx = hx - 2 if not back else hx + 16                         # tufinho (a "asinha" do Chaz)
    c.px(tx, hy + 3, "B"); c.px(tx + (-1 if not back else 1), hy + 2, "B")
    c.rect(hx + 6, hy - 1, hx + 8, hy - 1, "B")                 # bolinha do topo
    c.outline()
    return c


def side(p):
    c = Cel()
    by = p.get("by", 0)
    hx, hy = 8, 7 + by
    bx, bty = 11, 19 + by
    top = bty + 7
    # perna de trás (sombra) e da frente: (dx, lift)
    (fdx, flift), (ndx, nlift) = p.get("far", (0, 0)), p.get("near", (0, 0))
    c.rect(bx + 1 + fdx, top, bx + 3 + fdx, GROUND - flift, "S")
    c.px(bx + 4 + fdx, GROUND - flift, "S")                     # pé apontando pra frente
    # rabinho atrás, curvado pra cima (abana)
    w = p.get("wag", 0)
    for (x, y) in ((bx - 1, bty + 4), (bx - 2, bty + 3), (bx - 2, bty + 2 - w), (bx - 3, bty + 1 - w)):
        c.px(x, y, "B")
    c.stamp(BODY_SIDE, bx, bty)
    c.rect(bx + 3 + ndx, top, bx + 5 + ndx, GROUND - nlift, "B")
    c.px(bx + 5 + ndx, GROUND - nlift, "S")
    c.px(bx + 6 + ndx, GROUND - nlift, "B")                     # pé
    # bracinho (sombra pra separar do corpo)
    a = p.get("arm", 0)
    if p.get("run"):
        c.rect(bx + 3 + a, bty + 2, bx + 4 + a, bty + 3, "S")
    else:
        c.rect(bx + 3 + a, bty + 2, bx + 4 + a, bty + 4, "S")
    c.stamp(HEAD_SIDE, hx, hy)
    eb = p.get("ear_back", 0)
    c.stamp(EAR_SIDE, hx + 3 - eb, hy + 2 - eb)
    c.px(hx - 1, hy + 3, "B"); c.px(hx - 2, hy + 2, "B")         # tufinho atrás
    c.rect(hx + 5, hy - 1, hx + 7, hy - 1, "B")                 # bolinha do topo
    c.outline()
    return c


def mirror(c):
    """Esquerda = espelho da direita, com o pedaço do '3' redesenhado no sentido certo."""
    m = Cel()
    m.a = c.a[:, ::-1].copy()
    return m


# ------------------------------------------------------------------ poses
FRONT_POSES = [
    dict(),                                                         # 1 parado
    dict(liftL=1, arms="swingL", ear=0),                            # 2 passo esquerdo
    dict(by=-1, ear=1),                                             # 3 passagem (orelha atrasa)
    dict(liftR=1, arms="swingR", ear=0),                            # 4 passo direito
    dict(by=-1, liftL=3, arms="out", ear=1, wag=1),                 # 5 corrida
    dict(by=-2, liftL=1, liftR=1, spread=1, arms="out", ear=2),     # 6 no ar
    dict(by=-1, liftR=3, arms="out", ear=1, wag=-1),                # 7 corrida
]
SIDE_POSES = [
    dict(),
    dict(near=(2, 0), far=(-2, 0), arm=-1, wag=0),
    dict(by=-1, near=(0, 0), far=(0, 1), arm=0, wag=1),
    dict(near=(-2, 0), far=(2, 0), arm=1, wag=0),
    dict(by=-1, near=(3, 1), far=(-3, 2), arm=-2, run=True, ear_back=1, wag=1),
    dict(by=-2, near=(2, 2), far=(-2, 2), arm=0, run=True, ear_back=1, wag=1),
    dict(by=-1, near=(-3, 2), far=(3, 1), arm=2, run=True, ear_back=1, wag=1),
]
FRONT_POSES_BACK = [dict(p, wag=p.get("wag", [0, 1, 0, -1, 1, 0, -1][i])) for i, p in enumerate(FRONT_POSES)]

ROWS = ["frente", "esquerda", "direita", "costas"]
ANIMS = {"walk": [1, 2, 3, 2], "run": [4, 5, 6, 5]}
MS = {"walk": 150, "run": 100}


def build():
    g = {}
    for i in range(7):
        g[("frente", i)] = front(FRONT_POSES[i]).image()
        r = side(SIDE_POSES[i])
        g[("direita", i)] = r.image()
        g[("esquerda", i)] = mirror(r).image()
        g[("costas", i)] = front(FRONT_POSES_BACK[i], back=True).image()
    return g


if __name__ == "__main__":
    os.chdir(HERE)
    g = build()
    sheet = Image.new("RGBA", (CELL * 7, CELL * 4), (0, 0, 0, 0))
    for (r, i), im in g.items():
        sheet.alpha_composite(im, (i * CELL, ROWS.index(r) * CELL))
    sheet.save("chaz_folha_1x.png")
    Z = 8
    prev = Image.new("RGBA", sheet.size, (250, 250, 250, 255)); prev.alpha_composite(sheet)
    prev.resize((sheet.width * Z, sheet.height * Z), Image.NEAREST).save("preview_folha.png")
    for r in ROWS:
        for an in ("walk", "run"):
            fr = []
            for i in ANIMS[an]:
                bg = Image.new("RGBA", (CELL, CELL), (42, 38, 51, 255)); bg.alpha_composite(g[(r, i)])
                fr.append(bg.resize((CELL * Z, CELL * Z), Image.NEAREST).convert("P", palette=Image.ADAPTIVE))
            fr[0].save(f"gif_{an}_{r}.gif", save_all=True, append_images=fr[1:], duration=MS[an], loop=0, disposal=2)
    used = sorted({"#%02x%02x%02x" % c[:3] for c in sheet.getdata() if c[3] == 255})
    print("cores:", len(used), used)
