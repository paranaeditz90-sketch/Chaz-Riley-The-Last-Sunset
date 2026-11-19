"""Chaz — folha de sprites no estilo da referência do LM (desenhado pixel a pixel, sem conversor).

Estilo (medido na folha de referência com study.py, escala 6x -> ~26x32 px por personagem):
  chibi (cabeça ~48% da altura), azul chapado SEM sombra, contorno preto 1px,
  olhos = círculos brancos, nariz = triângulo branco, "3" branco no peito.
Layout: 4 linhas (frente, esquerda, direita, costas) x 7 frames
  (1 parado, 2-4 andar, 5-7 correr). Quadro 48x48, pés no chão em y=44.

Rodar: cd pixel-art/chaz && python3 -P build.py
"""
import math
import os
import sys

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", ".claude", "skills", "pixel-art-studio", "scripts"))
from pixelstudio import Sprite  # noqa: E402

BLUE = "#2634e6"   # medido na referência
OL = "#000000"
WHITE = "#ffffff"
PALETTE = [BLUE, OL, WHITE]
CELL = 48
LAYERS = ["far", "tail", "body", "near", "head", "ear", "arms", "tail_front", "face"]  # braços por cima das orelhas
THREE = ["###", "..#", ".##", "..#", "###"]


# ------------------------------------------------------------------ helpers
def part(s, layer, shapes, outline=True):
    """Cor chapada + contorno de fora. Camadas separadas = linha interna onde uma parte cobre outra."""
    s.layer(layer)
    for k, a in shapes:
        if k == "e":
            s.ellipse(*a, BLUE)
        elif k == "p":
            s.polygon(a, BLUE)
        elif k == "r":
            s.rect(*a, BLUE)
        elif k == "c":
            s.circle(*a, BLUE, fill=True)
    if outline:
        s.outline(OL, where="outside")


def limb(pts, w):
    """Membro como tubo (quads entre pontos + juntas redondas): permite joelho/cotovelo dobrado."""
    out = []
    r = w / 2
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * r, dx / L * r
        out.append(("p", [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]))
    for (x, y) in pts:
        out.append(("e", (x - r, y - r, x + r - 1, y + r - 1)))
    return out


def glyph(s, x, y, cols=(0, 1, 2)):
    for j, row in enumerate(THREE):
        for i, ch in enumerate(row):
            if ch == "#" and i in cols:
                s.px(x + i - cols[0], y + j, WHITE)


def eye(s, cx, cy):
    s.circle(cx, cy, 2, WHITE, fill=True)          # círculo 5x5


# ------------------------------------------------------------------ frente / costas
def front(s, p, back=False):
    by = p.get("by", 0)
    lL, lR = p.get("liftL", 0), p.get("liftR", 0)       # pé levantado (px)
    sx = p.get("spread", 0)                             # pernas abertas (corrida no ar)
    armL, armR = p.get("armL", 0), p.get("armR", 0)     # 0 = caído, 1 = meio, 2 = aberto (corrida)
    legs = []
    for x0, lift, d in ((19 - sx, lL, -1), (25 + sx, lR, 1)):
        knee = lift >= 3
        top = 36 + by
        foot = 44 - lift
        legs.append(("r", (x0, top, x0 + 3, foot - 2)))
        legs.append(("e", (x0 - 1 + (d if knee else 0), foot - 3, x0 + 4 + (d if knee else 0), foot)))
    part(s, "body", [("e", (18, 26 + by, 29, 39 + by))] + legs)
    s.layer("body")
    s.line(23, 39 + by, 23, 44, OL); s.line(24, 39 + by, 24, 44, OL)   # vão entre as pernas
    if back:
        # rabo de cachorro (de costas): sai do quadril, vai pro lado e curva pra cima FORA do corpo,
        # afinando até um tufo. A ponta abana (wag). Lado esquerdo de quem olha = lado esquerdo do Chaz.
        w = p.get("wag", 0)
        tip = (10 + w, 32 + by)
        part(s, "tail_front", limb([(22, 39 + by), (17, 40 + by), (12, 38 + by), (10 + w // 2, 35 + by), tip], 3)
             + [("p", [(tip[0] - 2, tip[1] + 1), (tip[0] - 2, tip[1] - 3), (tip[0], tip[1] - 2),
                       (tip[0] + 1, tip[1] - 4), (tip[0] + 2, tip[1] + 1)])])
    else:
        glyph(s, 22, 29 + by)
    arms = []
    for side, a in ((-1, armL), (1, armR)):
        sh = (19 if side < 0 else 28, 29 + by)
        hand = {0: (sh[0] + side, 35 + by),
                1: (sh[0] + 2 * side, 33 + by),
                2: (sh[0] + 7 * side, 31 + by)}[a]
        arms += limb([sh, hand], 4)
    part(s, "arms", arms)
    head(s, p, back=back)


def head(s, p, back=False):
    hy = p.get("hy", p.get("by", 0))
    eb = p.get("ear", 0)                                # quique da ponta da orelha
    part(s, "far", [("c", (23, 12 + hy, 2))])          # bolinha do topo (atrás da cabeça)
    part(s, "head", [("e", (14, 12 + hy, 33, 28 + hy)), ("e", (16, 11 + hy, 31, 20 + hy))])
    tuft_x = 13 if not back else 34
    d = -1 if not back else 1
    ears = [("p", [(tuft_x, 15 + hy), (tuft_x + 4 * d, 13 + hy), (tuft_x + 3 * d, 15 + hy),
                   (tuft_x + 5 * d, 16 + hy), (tuft_x + 1 * d, 18 + hy)])]
    for cx, lean in ((15, -3), (32, 3)):
        bx = cx + lean
        ears += [("p", [(cx - 2, 15 + hy), (cx + 2, 15 + hy), (bx + 3, 24 + hy + eb), (bx - 3, 24 + hy + eb)]),
                 ("e", (bx - 3, 21 + hy + eb, bx + 3, 27 + hy + eb))]
    part(s, "ear", ears)
    if not back:
        s.layer("face")
        eye(s, 19, 21 + hy); eye(s, 28, 21 + hy)
        for x in (22, 23, 24, 25):
            s.px(x, 24 + hy, WHITE)
        s.px(23, 25 + hy, WHITE); s.px(24, 25 + hy, WHITE)


# ------------------------------------------------------------------ perfil (olhando pra direita)
def side(s, p):
    by = p.get("by", 0)
    hx = p.get("lean", 0)                              # inclinação pra frente na corrida
    hy = p.get("hy", by)
    near, far = p.get("near", (0, 0, 0)), p.get("far", (0, 0, 0))   # (dx do pé, lift, joelho)
    an, af = p.get("arm_near", 0), p.get("arm_far", 0)              # dx da mão
    tail = p.get("tail", 0)
    ear_back = p.get("ear_back", 0)

    def leg(hipx, spec):
        dx, lift, knee = spec
        hip = (hipx, 36 + by)
        foot = (hipx + dx, 42 - lift)
        pts = [hip, ((hip[0] + foot[0]) / 2 + knee, (hip[1] + foot[1]) / 2), foot] if knee else [hip, foot]
        return limb(pts, 4) + [("e", (foot[0] - 2, foot[1] - 1, foot[0] + 4, foot[1] + 2))]

    part(s, "far", leg(22, far) + limb([(23 + hx, 29 + by), (23 + hx + af, 35 + by - abs(af) // 3)], 3))
    part(s, "tail", [("p", [(20, 37 + by), (16, 37 + by), (14 - tail, 35 + by), (12 - tail, 31 + by),
                            (14 - tail, 32 + by), (15 - tail, 30 + by), (16, 34 + by), (20, 34 + by)])])
    part(s, "body", [("e", (18 + hx, 26 + by, 28 + hx, 39 + by))] + leg(23, near))
    glyph(s, 25 + hx, 29 + by, cols=(0, 1))
    part(s, "arms", limb([(23 + hx, 29 + by), (23 + hx + an, 35 + by - abs(an) // 3)], 3))
    part(s, "far", [("c", (22 + hx, 11 + hy, 2))])
    part(s, "head", [("e", (13 + hx, 12 + hy, 34 + hx, 28 + hy)), ("e", (16 + hx, 11 + hy, 31 + hx, 20 + hy))])
    eb = ear_back
    # parada/andando: lóbulo caído. Correndo: o mesmo lóbulo jogado 2px pra trás e pra cima (vento).
    ear = (12 + hx, 13 + hy, 23 + hx, 30 + hy) if eb == 0 else (10 + hx, 12 + hy, 21 + hx, 27 + hy)
    part(s, "ear", [("e", ear),
                    ("p", [(31 + hx, 14 + hy), (35 + hx, 12 + hy), (34 + hx, 14 + hy), (36 + hx, 15 + hy), (33 + hx, 17 + hy)])])
    s.layer("face")
    eye(s, 29 + hx, 21 + hy)


# ------------------------------------------------------------------ poses (7 por direção)
FRONT_POSES = [
    dict(),                                                     # 1 parado
    dict(liftL=2, armL=1, wag=2),                               # 2 passo esquerdo
    dict(by=-1, wag=0),                                         # 3 passagem
    dict(liftR=2, armR=1, wag=-2),                              # 4 passo direito
    dict(by=-1, liftL=4, armL=2, armR=2, wag=3),                # 5 corrida: joelho esquerdo
    dict(by=-2, liftL=2, liftR=2, spread=1, armL=2, armR=2),    # 6 no ar
    dict(by=-1, liftR=4, armL=2, armR=2, wag=-3),               # 7 joelho direito
]
SIDE_POSES = [
    dict(),
    dict(near=(3, 0, 0), far=(-3, 0, 0), arm_near=-4, arm_far=4),
    dict(by=-1, near=(0, 0, 0), far=(0, 2, 0), tail=1),
    dict(near=(-3, 0, 0), far=(3, 0, 0), arm_near=4, arm_far=-4),
    dict(by=-1, lean=1, near=(5, 1, 0), far=(-5, 4, -2), arm_near=-7, arm_far=7, ear_back=4, tail=2),
    dict(by=-2, lean=2, near=(3, 3, -2), far=(-3, 3, -2), arm_near=0, arm_far=0, ear_back=5, tail=3),
    dict(by=-1, lean=1, near=(-5, 4, -2), far=(5, 1, 0), arm_near=7, arm_far=-7, ear_back=4, tail=2),
]


def render(view, pose):
    s = Sprite(CELL, CELL, palette=PALETTE)
    for name in LAYERS:
        s.layer(name)
    if view == "frente":
        front(s, pose)
    elif view == "costas":
        front(s, pose, back=True)
    else:
        side(s, pose)
    return s.composite(1)


def mirror_side(img, pose):
    """Esquerda = espelho da direita, mas o '3' é redesenhado sem espelhar."""
    m = ImageOps.mirror(img)
    by, hx = pose.get("by", 0), pose.get("lean", 0)
    px = m.load()
    x0 = CELL - 1 - (26 + hx)          # onde o pedaço do 3 caiu depois do espelho
    blue = tuple(int(BLUE[k:k + 2], 16) for k in (1, 3, 5)) + (255,)
    for j in range(5):
        for i in range(2):
            px[x0 + i, 29 + by + j] = blue
    for j, row in enumerate(THREE):
        for n, i in enumerate((1, 2)):
            if row[i] == "#":
                px[x0 + n, 29 + by + j] = (255, 255, 255, 255)
    return m


ROWS = ["frente", "esquerda", "direita", "costas"]
ANIMS = {"idle": [0], "walk": [1, 2, 3, 2], "run": [4, 5, 6, 5]}
MS = {"idle": 400, "walk": 150, "run": 100}


def build():
    grid = {}
    for r in ROWS:
        poses = FRONT_POSES if r in ("frente", "costas") else SIDE_POSES
        for i, pose in enumerate(poses):
            grid[(r, i)] = mirror_side(render("direita", pose), pose) if r == "esquerda" else render(r, pose)
    return grid


if __name__ == "__main__":
    os.chdir(HERE)
    grid = build()
    sheet = Image.new("RGBA", (CELL * 7, CELL * 4), (0, 0, 0, 0))
    for (r, i), img in grid.items():
        sheet.alpha_composite(img, (i * CELL, ROWS.index(r) * CELL))
    sheet.save("chaz_folha_1x.png")                     # prévia 1x (folha final + JSON só após aprovação)
    Z = 6
    prev = Image.new("RGBA", sheet.size, (250, 250, 250, 255))
    prev.alpha_composite(sheet)
    prev.resize((sheet.width * Z, sheet.height * Z), Image.NEAREST).save("preview_folha.png")
    for r in ROWS:
        for an in ("walk", "run"):
            frames = []
            for i in ANIMS[an]:
                bg = Image.new("RGBA", (CELL, CELL), (42, 38, 51, 255))
                bg.alpha_composite(grid[(r, i)])
                frames.append(bg.resize((CELL * Z, CELL * Z), Image.NEAREST).convert("P", palette=Image.ADAPTIVE))
            frames[0].save(f"gif_{an}_{r}.gif", save_all=True, append_images=frames[1:],
                           duration=MS[an], loop=0, disposal=2)
    cols = sorted({c[:3] for c in sheet.getdata() if c[3] == 255})
    print("cores usadas:", ["#%02x%02x%02x" % c for c in cols])
    print("ok:", sheet.size)
