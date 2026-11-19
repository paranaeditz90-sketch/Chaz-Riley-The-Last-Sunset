"""Chaz — sprite 48x48 desenhado pixel a pixel (pixel-art-studio). Nada de conversor de imagem.

Referências (só olhadas, nunca convertidas): folha do Chaz do LM + frames do Bruce Bronze.
Estudo: ~3 cabeças de altura, orelhas caídas até ~45% da altura, tufo no topo,
"asinha" de pelo do lado direito da cabeça (esquerda de quem olha), "3" branco no peito,
traço escuro em tudo (fase out/nov do Bruce).

Rodar: cd pixel-art/chaz && python3 -P build.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", ".claude", "skills", "pixel-art-studio", "scripts"))
from pixelstudio import Sprite  # noqa: E402

# ---------------------------------------------------------------- paleta (10 cores, máx 16)
R = ["#250d5c", "#211294", "#1a28d8", "#4270ed", "#7dbbfa"]  # corpo: sombra violeta -> luz ciano
OL = "#0a0612"     # contorno (quase preto puxado pro roxo)
SCL = "#f3e6b0"    # esclera creme
IRIS = "#8a4fd8"   # íris roxa
PUP = "#3a1a6a"    # pupila
WHT = "#f4f4f8"    # marca "3" e brilho do olho
PALETTE = R + [OL, SCL, IRIS, PUP, WHT]

LAYERS = ["tail_back", "ear_far", "arm_far", "body", "arm_near", "tail_front",
          "head", "ear_near", "face"]

THREE = ["###", "..#", ".##", "..#", "###"]


# ---------------------------------------------------------------- helpers
def shp(s, kind, args, color, only=None):
    if kind == "e":
        s.ellipse(*args, color, only=only)
    elif kind == "p":
        s.polygon(args, color, only=only)
    elif kind == "r":
        s.rect(*args, color, only=only)
    elif kind == "c":
        s.circle(*args, color, fill=True, only=only)


def moved(kind, args, dx, dy):
    if kind in ("e", "r"):
        x0, y0, x1, y1 = args
        return (x0 + dx, y0 + dy, x1 + dx, y1 + dy)
    if kind == "p":
        return [(x + dx, y + dy) for x, y in args]
    if kind == "c":
        cx, cy, r = args
        return (cx + dx, cy + dy, r)


def rim(s, color, base, xmax=99):
    """Luz de borda: pixel da cor base cujo vizinho de cima OU da esquerda está vazio."""
    pts = []
    for y in range(s.h):
        for x in range(s.w):
            c = s.get(x, y)
            if c and "#%02x%02x%02x" % c[:3] == base:
                if s.get(x, y - 1) is None or (s.get(x - 1, y) is None and x <= xmax):
                    pts.append((x, y))
    for x, y in pts:
        s.px(x, y, color)


def part(s, layer, shapes, shift=1, base=2, shade=1, light=True, outline=True, light_xmax=99):
    """Receita da forma deslocada: silhueta no tom de sombra, base repintada deslocada
    pra luz (topo-esquerda), luz de borda no lado iluminado, contorno de fora."""
    s.layer(layer)
    for k, a in shapes:
        shp(s, k, a, R[shade])
    for k, a in shapes:
        shp(s, k, moved(k, a, -shift, -shift), R[base], only="opaque")
    if light:
        rim(s, R[base + 1], R[base], light_xmax)
    if outline:
        s.outline(OL, where="outside")


def glyph(s, rows, x, y, color, cols=None):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "#" and (cols is None or i in cols):
                s.px(x + i, y + j, color)


EYE_FRONT = [".SSS.", "SWIIS", "SIPPS", "SIPPS", "SIIIS", ".SSS."]
EYE_SIDE = [".SS.", "SWII", "SIPP", "SIPP", "SIII", ".SS."]
EYE_COL = {"S": SCL, "W": WHT, "I": IRIS, "P": PUP}


def eye(s, rows, x, y):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in EYE_COL:
                s.px(x + i, y + j, EYE_COL[ch])


def drop_ear(cx, top, bottom, w, lean):
    """Orelha caída em gota: estreita em cima (presa na cabeça), larga e redonda embaixo.
    lean = quanto a ponta de baixo vai pra fora (px)."""
    bx = cx + lean
    r = w // 2
    return [("p", [(cx - 2, top), (cx + 2, top), (bx + r, bottom - r), (bx - r, bottom - r)]),
            ("e", (bx - r, bottom - 2 * r, bx + r, bottom))]


# ---------------------------------------------------------------- vistas
# Proporção do estudo (folha do LM + Bruce 10-10): cabeça ~34% | tronco ~35% | perna ~28%.
# Grade: topo da cabeça y=3, queixo y=19, virilha y=34, chão y=46.
HEAD_F = (12, 3, 35, 20)          # cabeça de frente/costas (24x18, cúpula)
NUB = ("e", (20, 1, 27, 6))      # bolinha do topo: larga e baixa, não espinho


def body_front(s, by):
    part(s, "body", [("e", (17, 17 + by, 30, 36 + by)),
                     ("r", (18, 30 + by, 22, 43)), ("r", (25, 30 + by, 29, 43)),
                     ("e", (16, 41, 23, 46)), ("e", (24, 41, 31, 46))], shift=1)
    s.layer("body")
    s.line(23, 35 + by, 23, 45, OL); s.line(24, 35 + by, 24, 45, OL)   # vão entre as pernas
    for x in (19, 21, 26, 28):
        s.px(x, 46, R[1])                                              # dedos
    s.ellipse(19, 17 + by, 28, 20 + by, R[1], only=R[2])                # sombra da cabeça no pescoço


def head_front(s, hy, tuft_left=True):
    part(s, "ear_far", [("e", (21, 0 + hy, 26, 5 + hy))], shift=1)          # bolinha do topo
    part(s, "head", [("e", moved("e", HEAD_F, 0, hy)), ("e", (15, 3 + hy, 32, 13 + hy))], shift=1)
    tuft = [(13, 8), (7, 6), (9, 9), (5, 11), (11, 13)] if tuft_left else \
           [(34, 8), (40, 6), (38, 9), (42, 11), (36, 13)]
    part(s, "ear_near", [("p", [(x, y + hy) for x, y in tuft])]
         + drop_ear(14, 8 + hy, 24 + hy, 8, -3) + drop_ear(33, 8 + hy, 24 + hy, 8, 3), shift=1)


def front(s, p):
    by, hy = p.get("by", 0), p.get("hy", 0)
    part(s, "tail_back", [("p", [(29, 36 + by), (34, 35 + by), (37, 32 + by), (37, 28 + by), (39, 26 + by),
                                 (40, 29 + by), (42, 27 + by), (42, 32 + by), (39, 36 + by), (33, 39 + by), (29, 39 + by)])])
    body_front(s, by)
    glyph(s, THREE, 22, 23 + by, WHT)
    part(s, "arm_near", [("e", (14, 21 + by, 18, 34 + by)), ("e", (29, 21 + by, 33, 34 + by))], light_xmax=24)
    head_front(s, hy)
    s.layer("face")
    eye(s, EYE_FRONT, 17, 10 + hy); eye(s, EYE_FRONT, 26, 10 + hy)
    s.px(23, 16 + hy, OL); s.px(24, 16 + hy, OL)                                           # nariz
    for x, y in ((22, 18), (25, 18), (23, 19), (24, 19)):
        s.px(x, y + hy, OL)                                                                # sorriso
    s.line(18, 6 + hy, 20, 5 + hy, R[4]); s.line(21, 7 + hy, 23, 6 + hy, R[4])             # brilho do pelo


def side(s, p):
    by, hy = p.get("by", 0), p.get("hy", 0)
    nl, fl = p.get("near", 0), p.get("far", 0)
    nlift, flift = p.get("nlift", 0), p.get("flift", 0)
    arm = p.get("arm", 0)
    t = p.get("tx", 0)
    part(s, "tail_back", [("p", [(21, 34 + by), (15, 34 + by), (12, 31 + by), (11 + t, 27 + by), (9 + t, 24 + by),
                                 (12 + t, 25 + by), (12 + t, 22 + by), (14 + t, 25 + by), (15, 29 + by), (21, 31 + by)])])
    part(s, "arm_far", [("p", [(20, 30 + by), (24, 30 + by), (24 + fl, 42 - flift), (20 + fl, 42 - flift)]),
                        ("e", (19 + fl, 41 - flift, 27 + fl, 46 - flift))], base=1, shade=0, light=False)
    part(s, "body", [("e", (19, 17 + by, 30, 36 + by)),
                     ("p", [(23, 30 + by), (27, 30 + by), (27 + nl, 42 - nlift), (23 + nl, 42 - nlift)]),
                     ("e", (22 + nl, 41 - nlift, 30 + nl, 46 - nlift))], shift=1)
    s.layer("body")
    s.ellipse(20, 17 + by, 29, 20 + by, R[1], only=R[2])
    glyph(s, THREE, 27, 23 + by, WHT, cols=(1, 2))
    part(s, "arm_near", [("e", (23 + arm, 21 + by, 26 + arm, 33 + by))])
    part(s, "ear_far", [("e", (21, 0 + hy, 26, 5 + hy))], shift=1)          # bolinha do topo
    part(s, "head", [("e", (15, 3 + hy, 34, 20 + hy)), ("e", (18, 3 + hy, 32, 13 + hy)),
                     ("e", (31, 12 + hy, 36, 19 + hy))], shift=1)
    part(s, "ear_near", [("p", [(18, 8 + hy), (12, 6 + hy), (14, 9 + hy), (10, 11 + hy), (16, 12 + hy)])]
         + drop_ear(21, 6 + hy, 24 + hy + p.get("ey", 0), 8, -2), shift=1)
    s.layer("face")
    eye(s, EYE_SIDE, 27, 9 + hy)
    s.px(36, 13 + hy, OL); s.px(37, 13 + hy, OL); s.px(37, 14 + hy, OL)   # nariz
    s.px(33, 17 + hy, OL); s.px(34, 17 + hy, OL)                          # boca
    s.line(23, 6 + hy, 25, 5 + hy, R[4])


def back(s, p):
    by, hy = p.get("by", 0), p.get("hy", 0)
    body_front(s, by)
    part(s, "arm_near", [("e", (14, 21 + by, 18, 34 + by)), ("e", (29, 21 + by, 33, 34 + by))], light_xmax=24)
    # rabo pra cima a partir do quadril, curto
    part(s, "tail_front", [("p", [(25, 34 + by), (20, 35 + by), (15, 34 + by), (11, 31 + by), (11, 27 + by),
                                  (9, 25 + by), (9, 28 + by), (7, 27 + by), (8, 32 + by), (10, 35 + by),
                                  (15, 38 + by), (20, 38 + by), (25, 37 + by)])])
    head_front(s, hy, tuft_left=False)
    s.layer("face")
    s.line(18, 7 + hy, 20, 6 + hy, R[4]); s.line(26, 6 + hy, 28, 7 + hy, R[4])


# ---------------------------------------------------------------- monta
def new_sprite():
    s = Sprite(48, 48, palette=PALETTE)
    for name in LAYERS:
        s.layer(name)
    return s


VIEWS = [("frente", front), ("perfil", side), ("costas", back)]

# Andar de perfil, 4 frames (pixel-art-studio/animation.md): contato, passagem, contato, passagem.
# Corpo sobe 1px na passagem; orelha/rabo atrasam 1 frame; braço oposto à perna da frente.
# (Cabeça atrasada 1 frame num bob de 2 frames fica em contrafase: balança sozinha. Por isso não.)
WALK = [
    dict(by=0,  near=3,  far=-3, arm=-2, tx=0),
    dict(by=-1, near=0,  far=0,  arm=0,  tx=1, flift=2),
    dict(by=0,  near=-3, far=3,  arm=2,  tx=0),
    dict(by=-1, near=0,  far=0,  arm=0,  tx=-1, nlift=2),
]
for i, f in enumerate(WALK):
    f["hy"] = f["by"]                         # cabeça acompanha o corpo
    f["ey"] = WALK[i - 1]["by"] - f["by"]     # ponta da orelha atrasa 1 frame (secundário)
WALK_MS = 150                            # medido no vídeo de referência: pose ~4-5 frames a 30fps

if __name__ == "__main__":
    os.chdir(HERE)
    s = new_sprite()
    for i, (name, fn) in enumerate(VIEWS):
        if i > 0:
            s.add_frame(copy=False)
        fn(s, {})
    s.preview("preview.png", scale=8)
    for i, (name, _) in enumerate(VIEWS):
        s.save_silhouette(f"silhouette_{name}.png", frame=i + 1, scale=4)
        s.save_png(f"chaz_{name}_1x.png", frame=i + 1)
    s.stats()

    w = new_sprite()
    for i, pose in enumerate(WALK):
        if i > 0:
            w.add_frame(copy=False)
        side(w, pose)
    w.set_duration(WALK_MS, frames=[1, 2, 3, 4])
    w.tag("walk_side", 1, 4)
    w.preview("walk_preview.png", scale=8)
    w.save_gif("walk_side.gif", scale=6, bg="#2a2633")
    w.stats()
