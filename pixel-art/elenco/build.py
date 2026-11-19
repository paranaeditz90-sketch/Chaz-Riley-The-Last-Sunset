"""Elenco chibi (Chaz, Riley, Fumaça) — frente parado, 48x48, desenhado por script (pixel-art-studio).

Estilo pedido pelo LM (exemplos de pixel art fofa): contorno COLORIDO (tom mais escuro do personagem,
nunca preto), olho de anime (íris em degradê + 2 brilhos + cílio grosso), bochecha rosada,
sombra suave com hue shift, brilho em arco na cabeça, proporção chibi (cabeça ~50%).
Nada de conversor de imagem: formas + carimbos pixel a pixel.

Rodar: cd pixel-art/elenco && python3 -P build.py
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", ".claude", "skills", "pixel-art-studio", "scripts"))
from pixelstudio import Sprite  # noqa: E402

CELL = 48

# ------------------------------------------------------------------ paletas (<=16 cores cada)
CHAZ = dict(ol="#17125a", deep="#1f1f8f", shadow="#2834c4", base="#3550f2", light="#5f7dff", hl="#a8c4ff",
            iris_d="#4b237f", iris_m="#8a4fd8", iris_l="#c79bff", sclera="#fff3c8", white="#ffffff",
            blush="#ff8fb8", mouth="#ff6f91", mark="#ffffff")
RILEY = dict(ol="#2c0516", deep="#4a0b2a", shadow="#6b1230", base="#8e1a2e", light="#b8364a", hl="#e2708a",
             iris_d="#4b237f", iris_m="#8a4fd8", iris_l="#c79bff", sclera="#fff3c8", white="#ffffff",
             blush="#ff9ab5", mouth="#2c0516", mark="#ffe9d6", inner="#e88aa0")
FUMACA = dict(ol="#2b2635", deep="#4d475c", shadow="#6a6378", base="#8b8597", light="#aaa5b8", hl="#cfcbe0",
              iris_d="#5e4a86", iris_m="#9b86c9", iris_l="#c9b8ef", sclera="#f3eefc", white="#ffffff",
              blush="#e7a0c0", mouth="#2b2635", mark="#ece8f6")


# ------------------------------------------------------------------ helpers
def shp(s, k, a, c, only=None):
    {"e": lambda: s.ellipse(*a, c, only=only), "p": lambda: s.polygon(a, c, only=only),
     "r": lambda: s.rect(*a, c, only=only), "c": lambda: s.circle(*a, c, fill=True, only=only)}[k]()


def mv(k, a, dx, dy):
    if k in ("e", "r"):
        return (a[0] + dx, a[1] + dy, a[2] + dx, a[3] + dy)
    if k == "p":
        return [(x + dx, y + dy) for x, y in a]
    return (a[0] + dx, a[1] + dy, a[2])


def part(s, layer, shapes, C, shift=1, light=None, outline=True):
    """Receita da forma deslocada: sombra -> base deslocada pra luz (topo-esq) -> luz -> contorno colorido."""
    s.layer(layer)
    for k, a in shapes:
        shp(s, k, a, C["shadow"])
    for k, a in shapes:
        shp(s, k, mv(k, a, -shift, -shift), C["base"], only="opaque")
    for k, a in (light or []):
        shp(s, k, a, C["light"], only="opaque")
    if outline:
        s.outline(C["ol"], where="outside")


def stamp(s, rows, x, y, legend):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in legend:
                s.px(x + i, y + j, legend[ch])


def eye_legend(C):
    return {"k": C["ol"], "a": C["iris_d"], "m": C["iris_m"], "l": C["iris_l"], "w": C["white"], "c": C["sclera"]}


# olhos 6x7 (glint sempre em cima à esquerda nos dois olhos = luz única)
EYE_OPEN = [".kkkk.",
            "kkkkkk",
            "kwwaak",
            "cwwmmc",
            "cmmmmc",
            "clllwc",
            ".cccc."]
EYE_GRUMPY = ["......",          # pálpebra caída (Riley): linha reta e grossa, íris cortada em cima
              "......",
              "kkkkkk",
              "kwwaak",
              "cmmmmc",
              "clllwc",
              ".cccc."]
EYE_SLEEPY = ["......",          # sono (Fumaça): só a metade de baixo + olheira
              "......",
              "......",
              "kkkkkk",
              "cwmmmc",
              ".llll.",
              ".dddd."]


def face(s, C, cx, ey, eye, mouth):
    L = eye_legend(C); L["d"] = C["deep"]
    stamp(s, eye, cx - 9, ey, L)
    stamp(s, eye, cx + 3, ey, L)
    for bx in (cx - 11, cx + 7):                         # bochechas
        s.rect(bx, ey + 7, bx + 3, ey + 8, C["blush"])
    s.px(cx - 1, ey + 7, C["ol"]); s.px(cx, ey + 7, C["ol"])   # narizinho
    stamp(s, mouth, cx - len(mouth[0]) // 2, ey + 8, {"k": C["ol"], "p": C["mouth"]})


MOUTH_HAPPY = ["k....k", ".kppk.", "..kk.."]   # sorriso aberto
MOUTH_FLAT = ["....", ".kk."]
MOUTH_SMALL = ["....", ".kk."]


def mark3(s, x, y, c):
    stamp(s, ["###", "..#", ".##", "..#", "###"], x, y, {"#": c})


# ------------------------------------------------------------------ corpo comum (chibi)
def body(s, C, cx=24):
    # pernas curtas + pés redondos (camada própria pra ter linha entre elas)
    part(s, "legs", [("r", (cx - 6, 36, cx - 2, 43)), ("r", (cx + 1, 36, cx + 5, 43)),
                     ("e", (cx - 7, 41, cx - 1, 46)), ("e", (cx, 41, cx + 6, 46))], C)
    part(s, "body", [("e", (cx - 7, 25, cx + 6, 39))], C, light=[("e", (cx - 6, 26, cx - 1, 31))])


def arms_down(s, C, cx=24):
    part(s, "arms", [("e", (cx - 11, 27, cx - 6, 36)), ("e", (cx + 5, 27, cx + 10, 36))], C)


# ------------------------------------------------------------------ Chaz
def chaz(s):
    C = CHAZ; cx = 24
    part(s, "tail", [("p", [(cx + 4, 37), (cx + 10, 36), (cx + 13, 32), (cx + 13, 28), (cx + 15, 27), (cx + 16, 30),
                            (cx + 18, 28), (cx + 18, 33), (cx + 15, 38), (cx + 9, 41), (cx + 4, 41)])], C)
    body(s, C, cx)
    mark3(s, cx - 2, 29, C["mark"])
    arms_down(s, C, cx)
    part(s, "nub", [("e", (cx - 2, 2, cx + 1, 6))], C, outline=True)
    part(s, "head", [("e", (cx - 13, 4, cx + 12, 27))], C, shift=2,
         light=[("e", (cx - 11, 5, cx + 1, 13))])
    # orelhas caídas moderadas: abraçam a cabeça e terminam na bochecha
    part(s, "ears", [("p", [(cx - 12, 9), (cx - 18, 7), (cx - 15, 10), (cx - 19, 12), (cx - 13, 14)]),
                     ("e", (cx - 17, 9, cx - 10, 25)), ("e", (cx + 9, 9, cx + 16, 25))], C,
         light=[("e", (cx - 16, 10, cx - 13, 16))])
    s.layer("face")
    for (x, y) in ((cx - 8, 7), (cx - 7, 6), (cx - 6, 6), (cx - 5, 5)):    # brilho em arco no topo
        s.px(x, y, C["hl"])
    face(s, C, cx, 14, EYE_OPEN, MOUTH_HAPPY)


# ------------------------------------------------------------------ Riley
def riley(s):
    C = RILEY; cx = 24
    # rabo comprido em S, atrás, à direita
    part(s, "tail", [("p", [(cx + 4, 40), (cx + 11, 40), (cx + 15, 36), (cx + 15, 30), (cx + 18, 25), (cx + 21, 26),
                            (cx + 18, 31), (cx + 18, 37), (cx + 13, 43), (cx + 4, 43)])], C)
    body(s, C, cx)
    mark3(s, cx - 2, 33, C["mark"])
    # braços cruzados (emburrada), finos e altos pra não cobrir o "3"
    part(s, "arms", [("e", (cx - 10, 26, cx + 4, 31)), ("e", (cx - 4, 27, cx + 9, 32))], C)
    # orelhas de gato atrás da cabeça (com miolo rosado)
    part(s, "ears_back", [("p", [(cx - 13, 14), (cx - 12, 1), (cx - 3, 8)]),
                          ("p", [(cx + 12, 14), (cx + 11, 1), (cx + 2, 8)])], C)
    s.layer("ears_back")
    s.polygon([(cx - 11, 11), (cx - 11, 5), (cx - 6, 9)], C["inner"], only="opaque")
    s.polygon([(cx + 10, 11), (cx + 10, 5), (cx + 5, 9)], C["inner"], only="opaque")
    part(s, "head", [("e", (cx - 13, 6, cx + 12, 28)),
                     # tufos de pelo nas bochechas
                     ("p", [(cx - 12, 18), (cx - 16, 19), (cx - 13, 21), (cx - 16, 23), (cx - 11, 24)]),
                     ("p", [(cx + 11, 18), (cx + 15, 19), (cx + 12, 21), (cx + 15, 23), (cx + 10, 24)])],
         C, shift=2, light=[("e", (cx - 11, 7, cx + 1, 15))])
    s.layer("face")
    for (x, y) in ((cx - 1, 9), (cx - 1, 10), (cx + 1, 8), (cx + 1, 9), (cx - 3, 10)):   # risquinhos na testa (Bruce)
        s.px(x, y, C["hl"])
    face(s, C, cx, 15, EYE_GRUMPY, MOUTH_FLAT)


# ------------------------------------------------------------------ Fumaça
def fumaca(s):
    C = FUMACA; cx = 24
    part(s, "tail", [("p", [(cx + 4, 37), (cx + 11, 37), (cx + 15, 40), (cx + 17, 37), (cx + 18, 41), (cx + 15, 44),
                            (cx + 9, 44), (cx + 4, 42)])], C)                   # rabo peludo caído
    body(s, C, cx)
    # marca de nuvem no peito
    stamp(s, ["..##...", ".#..##.", "#.....#", ".#####."], cx - 4, 30, {"#": C["mark"]})
    arms_down(s, C, cx)
    part(s, "head", [("e", (cx - 13, 5, cx + 12, 27)),
                     # franja/pelo bagunçado no topo
                     ("p", [(cx - 10, 8), (cx - 8, 1), (cx - 5, 6), (cx - 2, 0), (cx + 1, 5), (cx + 4, 1), (cx + 6, 6),
                            (cx + 10, 3), (cx + 10, 9)])], C, shift=2, light=[("e", (cx - 11, 6, cx + 1, 13))])
    # orelhas caídas desgrenhadas (ponta irregular)
    part(s, "ears", [("p", [(cx - 12, 9), (cx - 17, 13), (cx - 18, 22), (cx - 16, 25), (cx - 15, 23), (cx - 13, 26),
                            (cx - 11, 22), (cx - 10, 12)]),
                     ("p", [(cx + 11, 9), (cx + 16, 13), (cx + 17, 22), (cx + 15, 25), (cx + 14, 23), (cx + 12, 26),
                            (cx + 10, 22), (cx + 9, 12)])], C)
    s.layer("face")
    for (x, y) in ((cx - 7, 8), (cx - 6, 7), (cx - 5, 7)):
        s.px(x, y, C["hl"])
    face(s, C, cx, 14, EYE_SLEEPY, MOUTH_SMALL)


LAYERS = ["tail", "legs", "body", "mark", "arms", "nub", "ears_back", "head", "ears", "face"]
CAST = [("chaz", chaz), ("riley", riley), ("fumaca", fumaca)]

if __name__ == "__main__":
    os.chdir(HERE)
    imgs = []
    for name, fn in CAST:
        s = Sprite(CELL, CELL)
        for ly in LAYERS:
            s.layer(ly)
        fn(s)
        s.save_png(f"{name}_frente_1x.png")
        imgs.append(s.composite(1))
        cols = {c[:3] for c in s.composite(1).getdata() if c[3] > 0}
        print(name, "cores:", len(cols))
    # prévia: 6x num fundo claro e num escuro + 1x
    Z = 6
    W = len(imgs) * (CELL * Z + 12) + 12
    prev = Image.new("RGBA", (W, CELL * Z * 2 + 36 + CELL + 12), (245, 240, 236, 255))
    for i, im in enumerate(imgs):
        x = 12 + i * (CELL * Z + 12)
        big = im.resize((CELL * Z, CELL * Z), Image.NEAREST)
        prev.alpha_composite(big, (x, 12))
        dark = Image.new("RGBA", big.size, (40, 34, 52, 255)); dark.alpha_composite(big)
        prev.alpha_composite(dark, (x, CELL * Z + 24))
        prev.alpha_composite(im, (x, CELL * Z * 2 + 36))
    prev.save("preview_elenco.png")
    print("ok", prev.size)
