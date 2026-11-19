"""Chaz — redesenho da folha que o LM gerou no Gemini, pixel a pixel (sem conversor de imagem).

Medido na folha do Gemini (escala ~4.69x): personagem ~33-35 px, cabeça ~48%, orelha ~7 px de largura
passando ~3 px da cabeça, corpo estreito com "3", bracinho e perna curtos. Azul chapado + contorno preto.
Pedidos do LM: melhorar o RABO (rabo de cachorro de verdade, peludo, curvado, abanando) e ARRUMAR OS OLHOS
(sempre abertos e iguais no andar/correr; íris centralizada pra não ficar vesgo; fechado só nos extras).

Folha: 5 linhas x 7 frames, quadro 48x48, pés em y=45.
  frente | esquerda | direita | costas : 1 parado, 2-4 andar, 5-7 correr
  extras (de frente): piscar(2), comemorar(2), respirar de olho fechado(2), cantarolar(1)
Rodar: cd pixel-art/chaz && python3 -P build.py
"""
import os
import sys

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", ".claude", "skills", "pixel-art-studio", "scripts"))
from pixelstudio import Sprite  # noqa: E402

BLUE, OL, WHITE = "#2a3be8", "#000000", "#ffffff"
IRIS, PUPIL, PINK = "#8a4fd8", "#3a1a6a", "#ff6f91"
PALETTE = [BLUE, OL, WHITE, IRIS, PUPIL, PINK]
CELL = 48
LAYERS = ["far", "tail", "legs", "arms", "ears", "nub", "body", "head", "arms_front", "tail_front", "face", "fx"]
THREE = ["###", "..#", ".##", "..#", "###"]
LEG = {"k": OL, "w": WHITE, "p": IRIS, "a": PUPIL, "m": PINK, "b": BLUE}

# olhos (k contorno, w branco, p íris, a pupila, m boca rosa)
EYE_F = [".kk.",           # cílio
         ".ww.",           # de frente: oval branco sem moldura, íris 2x2 CENTRALIZADA + pupila
         "wwww",
         "wppw",
         "wpaw",
         ".ww."]
EYE_S = [".kk.",           # de perfil: mesma íris 2x2, virada pra frente
         ".ww.",
         "wwww",
         "wwpp",
         "wwpa",
         ".ww."]
EYE_HALF = ["....", "....", "....", "kkkk", "wppw", ".ww."]
EYE_BLINK = ["....", "....", "....", "k..k", ".kk.", "...."]
EYE_HAPPY = ["....", "....", ".kk.", "k..k", "....", "...."]
MOUTH_W = ["k..k", ".kk."]                    # ω pequenininho
MOUTH_OPEN = [".kkk.", "kmmmk", ".kkk."]
NOTE = ["..#.", "..##", "..#.", "###.", "##.."]


# ------------------------------------------------------------------ helpers
def part(s, layer, shapes):
    s.layer(layer)
    for k, a in shapes:
        if k == "e":
            s.ellipse(*a, BLUE)
        elif k == "p":
            s.polygon(a, BLUE)
        elif k == "r":
            s.rect(*a, BLUE)
    s.outline(OL, where="outside")


def stamp(s, rows, x, y, legend=LEG):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in legend:
                s.px(x + i, y + j, legend[ch])


def glyph(s, x, y, cols=(0, 1, 2)):
    for j, row in enumerate(THREE):
        for n, i in enumerate(cols):
            if row[i] == "#":
                s.px(x + n, y + j, WHITE)


def box_mirror(b):
    return (47 - b[2], b[1], 47 - b[0], b[3])


def tail_curl(base, tip, w=3):
    """Rabo de cachorro: tubo curvo da base até a ponta + tufo peludo (3 pontas) na ponta."""
    (bx, by_), (tx, ty) = base, tip
    mx, my = (bx + tx) / 2 + (2 if tx < bx else -2), (by_ + ty) / 2 + 2
    pts = [(bx, by_), (mx, my), (tx, ty)]
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        out.append(("p", [(x0, y0 - w / 2), (x1, y1 - w / 2), (x1, y1 + w / 2), (x0, y0 + w / 2)]))
    d = -1 if tx < bx else 1
    out.append(("e", (tx - 2, ty - 2, tx + 2, ty + 2)))
    out.append(("p", [(tx - 2, ty), (tx - 2 + d, ty - 5), (tx, ty - 2), (tx + 1 * d, ty - 5), (tx + 2, ty - 1)]))
    return out


# ------------------------------------------------------------------ frente / costas
ARM = {"down": (13, 29, 17, 36), "fwd": (13, 28, 17, 34), "back": (12, 30, 16, 37),
       "out": (8, 29, 16, 33), "up": (11, 19, 15, 29)}


def front(s, p, back=False):
    by, hy = p.get("by", 0), p.get("hy", p.get("by", 0))
    hx = p.get("hx", 0)
    lL, lR = p.get("legs", (0, 0))
    sp = p.get("spread", 0)
    eL, eR = p.get("ear", (0, 0))
    w = p.get("wag", 0)
    # rabo: de frente aparece a ponta peluda atrás, à direita; de costas fica na frente, à esquerda
    if back:
        part(s, "tail_front", tail_curl((22, 39 + by), (13 + w, 31 + by)))
    else:
        part(s, "tail", tail_curl((27, 38 + by), (35 + w, 31 + by)))
    legs = []
    for x0, lift in ((18 - sp, lL), (25 + sp, lR)):
        legs += [("r", (x0, 37 + by, x0 + 4, 43 - lift)), ("e", (x0 - 1, 41 - lift, x0 + 5, 45 - lift))]
    part(s, "legs", legs)
    s.layer("legs")
    part(s, "body", [("e", (17, 27 + by, 30, 40 + by))])
    if not back:
        glyph(s, 22, 30 + by)
    aL, aR = p.get("arms", ("down", "down"))
    la, ra = ARM[aL], box_mirror(ARM[aR])
    part(s, "arms", [("e", (la[0], la[1] + by, la[2], la[3] + by)), ("e", (ra[0], ra[1] + by, ra[2], ra[3] + by))])
    # cabeça redonda + bolinha + orelhas médias (7 px, passam ~3 px da cabeça)
    tuft = [(9, 17), (4, 15), (7, 18), (3, 20), (8, 21)] if not back else [(38, 17), (43, 15), (40, 18), (44, 20), (39, 21)]
    part(s, "ears", [("p", [(x + hx, y + hy) for x, y in tuft]),
                     ("e", (6 + hx, 15 + hy, 15 + hx, 28 + hy + eL)), ("e", (32 + hx, 15 + hy, 41 + hx, 28 + hy + eR))])
    part(s, "nub", [("e", (22 + hx, 9 + hy, 25 + hx, 14 + hy))])
    part(s, "head", [("e", (11 + hx, 12 + hy, 36 + hx, 28 + hy))])
    if not back:
        s.layer("face")
        eyes = p.get("eyes", "open")
        E = {"open": EYE_F, "half": EYE_HALF, "blink": EYE_BLINK, "happy": EYE_HAPPY}[eyes]
        stamp(s, E, 16 + hx, 17 + hy)
        stamp(s, E, 28 + hx, 17 + hy)
        s.px(23 + hx, 24 + hy, OL); s.px(24 + hx, 24 + hy, OL)                 # narizinho
        mouth = MOUTH_OPEN if p.get("mouth") == "open" else MOUTH_W
        stamp(s, mouth, 24 - len(mouth[0]) // 2 + hx, 25 + hy)
    if p.get("note"):
        nx, ny = p["note"]
        s.layer("fx")
        stamp(s, NOTE, nx, ny, {"#": WHITE})
        s.outline(OL, where="outside")


# ------------------------------------------------------------------ perfil (olhando pra direita)
def side(s, p):
    by, hy = p.get("by", 0), p.get("hy", p.get("by", 0))
    hx = p.get("lean", 0)
    (ndx, nl), (fdx, fl) = p.get("near", (0, 0)), p.get("far", (0, 0))
    an, af = p.get("arm", (0, 0))
    w = p.get("wag", 0)
    eb = p.get("ear_back", 0)
    # perna e braço de trás
    part(s, "far", [("r", (20 + fdx, 37 + by, 24 + fdx, 43 - fl)), ("e", (19 + fdx, 41 - fl, 27 + fdx, 45 - fl))])
    # rabo de cachorro atrás, curvado pra cima, ponta abana
    part(s, "tail", tail_curl((20, 36 + by), (13 - w, 28 + by)))
    part(s, "legs", [("r", (23 + ndx, 37 + by, 27 + ndx, 43 - nl)), ("e", (22 + ndx, 41 - nl, 30 + ndx, 45 - nl))])
    part(s, "body", [("e", (19 + hx, 27 + by, 30 + hx, 40 + by))])
    glyph(s, 27 + hx, 30 + by, cols=(1, 2))
    part(s, "arms_front", [("e", (23 + hx + an, 30 + by, 26 + hx + an, 35 + by))])
    ear = (9 + hx, 14 + hy, 18 + hx, 29 + hy) if eb == 0 else (7 + hx, 13 + hy, 16 + hx, 26 + hy)
    part(s, "ears", [("e", ear),
                     ("p", [(x + hx, y + hy) for x, y in ((33, 15), (37, 12), (36, 15), (40, 15), (35, 18))])])
    part(s, "nub", [("e", (21 + hx, 9 + hy, 24 + hx, 14 + hy))])
    part(s, "head", [("e", (12 + hx, 12 + hy, 35 + hx, 28 + hy))])
    s.layer("head")      # a orelha de perfil cai pela parte de trás da cabeça: linha curva desenhada à mão
    for (x, y) in ((18, 14), (19, 15), (19, 16), (20, 17), (20, 18), (20, 19), (20, 20), (20, 21), (19, 22), (19, 23), (18, 24)):
        s.px(x + hx - (2 if eb else 0), y + hy, OL)
    s.layer("face")
    E = {"open": EYE_S, "half": EYE_HALF, "blink": EYE_BLINK, "happy": EYE_HAPPY}
    stamp(s, E[p.get("eyes", "open")], 28 + hx, 17 + hy)
    s.px(35 + hx, 23 + hy, OL)                                                    # nariz na ponta
    s.px(33 + hx, 25 + hy, OL); s.px(34 + hx, 25 + hy, OL)                         # boquinha


# ------------------------------------------------------------------ poses
FRONT = [
    dict(),
    dict(legs=(2, 0), arms=("back", "fwd"), ear=(1, 0), wag=1),
    dict(by=-1, ear=(1, 1)),
    dict(legs=(0, 2), arms=("fwd", "back"), ear=(0, 1), wag=-1),
    dict(by=-1, legs=(4, 0), arms=("out", "out"), ear=(-2, -2), wag=2),
    dict(by=-2, legs=(2, 2), spread=1, arms=("out", "out"), ear=(-3, -3), wag=0),
    dict(by=-1, legs=(0, 4), arms=("out", "out"), ear=(-2, -2), wag=-2),
]
SIDE = [
    dict(),
    dict(near=(3, 0), far=(-3, 0), arm=(-2, 2), wag=1),
    dict(by=-1, near=(0, 0), far=(0, 2), arm=(0, 0), wag=2),
    dict(near=(-3, 0), far=(3, 0), arm=(2, -2), wag=1),
    dict(by=-1, lean=1, near=(5, 1), far=(-5, 3), arm=(-4, 4), ear_back=1, wag=2),
    dict(by=-2, lean=1, near=(3, 3), far=(-3, 3), arm=(0, 0), ear_back=1, wag=3),
    dict(by=-1, lean=1, near=(-5, 3), far=(5, 1), arm=(4, -4), ear_back=1, wag=2),
]
EXTRAS = [   # de frente
    dict(eyes="half"),                                                          # piscar 1
    dict(eyes="blink"),                                                         # piscar 2
    dict(by=-1, eyes="happy", mouth="open", arms=("up", "up"), ear=(-2, -2), wag=2),     # comemorar 1
    dict(by=-3, eyes="happy", mouth="open", arms=("up", "up"), legs=(2, 2), ear=(-3, -3), wag=-2),  # pulinho
    dict(eyes="blink", wag=1),                                                  # respirando de olho fechado 1
    dict(by=1, hy=1, eyes="blink", ear=(1, 1), wag=-1),                         # respirando 2
    dict(hx=1, eyes="happy", mouth="open", legs=(0, 1), note=(36, 8), wag=2),   # cantarolando ♪
]
ROWS = ["frente", "esquerda", "direita", "costas", "extras"]


def render(view, pose):
    s = Sprite(CELL, CELL, palette=PALETTE)
    for ly in LAYERS:
        s.layer(ly)
    {"frente": lambda: front(s, pose), "costas": lambda: front(s, pose, back=True),
     "extras": lambda: front(s, pose), "direita": lambda: side(s, pose)}[view]()
    return s.composite(1)


def left_from_right(img, pose):
    """Esquerda = espelho da direita; o pedaço do '3' é redesenhado no sentido certo."""
    m = ImageOps.mirror(img)
    by, hx = pose.get("by", 0), pose.get("lean", 0)
    px = m.load()
    x0 = 47 - (28 + hx)
    blue = tuple(int(BLUE[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
    for j in range(5):
        for i in range(2):
            if px[x0 + i, 30 + by + j][3]:
                px[x0 + i, 30 + by + j] = blue
    for j, row in enumerate(THREE):
        for n, i in enumerate((0, 1)):
            if row[i] == "#":
                px[x0 + n, 30 + by + j] = (255, 255, 255, 255)
    return m


def build():
    g = {}
    for i in range(7):
        g[("frente", i)] = render("frente", FRONT[i])
        r = render("direita", SIDE[i])
        g[("direita", i)] = r
        g[("esquerda", i)] = left_from_right(r, SIDE[i])
        g[("costas", i)] = render("costas", dict(FRONT[i], wag=[0, 2, 0, -2, 3, 0, -3][i]))
        g[("extras", i)] = render("extras", EXTRAS[i])
    return g


ANIMS = {"walk": [1, 2, 3, 2], "run": [4, 5, 6, 5]}

if __name__ == "__main__":
    os.chdir(HERE)
    g = build()
    sheet = Image.new("RGBA", (CELL * 7, CELL * len(ROWS)), (0, 0, 0, 0))
    for (r, i), im in g.items():
        sheet.alpha_composite(im, (i * CELL, ROWS.index(r) * CELL))
    sheet.save("chaz_folha_1x.png")
    Z = 6
    prev = Image.new("RGBA", sheet.size, (250, 250, 250, 255)); prev.alpha_composite(sheet)
    prev.resize((sheet.width * Z, sheet.height * Z), Image.NEAREST).save("preview_folha.png")

    def gif(name, frames, ms):
        fr = []
        for im in frames:
            bg = Image.new("RGBA", (CELL, CELL), (42, 38, 51, 255)); bg.alpha_composite(im)
            fr.append(bg.resize((CELL * Z, CELL * Z), Image.NEAREST).convert("P", palette=Image.ADAPTIVE))
        fr[0].save(name, save_all=True, append_images=fr[1:], duration=ms, loop=0, disposal=2)

    for r in ("frente", "esquerda", "direita", "costas"):
        gif(f"gif_andar_{r}.gif", [g[(r, i)] for i in ANIMS["walk"]], 150)
        gif(f"gif_correr_{r}.gif", [g[(r, i)] for i in ANIMS["run"]], 100)
    idle = [g[("frente", 0)]] * 6 + [g[("extras", 0)], g[("extras", 1)], g[("extras", 0)]] + [g[("frente", 0)]] * 3
    gif("gif_parado_piscando.gif", idle, 160)
    gif("gif_comemorar.gif", [g[("extras", 2)], g[("extras", 3)]], 180)
    gif("gif_cantarolar.gif", [g[("frente", 0)], g[("extras", 6)]], 300)
    used = sorted({"#%02x%02x%02x" % c[:3] for c in sheet.getdata() if c[3] == 255})
    print("cores:", used)
