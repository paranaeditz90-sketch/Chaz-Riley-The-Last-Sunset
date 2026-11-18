"""Esqueleto comum + definição de cada personagem (de perfil, olhando pra DIREITA).

A esquerda é o mesmo sprite espelhado na engine (flipX), como no jogo de referência.
Grade do frame: 32x40, chão em y=38. Coordenadas CONTÍNUAS (pixel i cobre [i, i+1)).
"""
from pixelkit import *

THREE = ["###", "..#", ".##", "..#", "###"]  # a marca "3" no peito (3x5)


# ----------------------------------------------------------------------------
# partes comuns
# ----------------------------------------------------------------------------
def leg(cv, c, lx, lift, bd, far=False):
    shaft = R(lx, 32.4 + bd, lx + 3.2, 35.8 - lift)
    paw = E(lx + 2.4, 36.5 - lift, 3.9, 1.6)
    base = c["shade"] if far else c["base"]
    paint(cv, shaft | paw, base, c["ol"], shade=None if far else c["shade"], outline="all")


def torso(cv, c, bd):
    m = E(15.8, 28.4 + bd, 4.8, 5.2)
    paint(cv, m, c["base"], c["ol"], shade=c["shade"], outline="outer")


def arm(cv, c, adx, bd):
    path = bez((14.2, 25.2 + bd), (14.2, 27 + bd), (13.8 + adx * 0.6, 29 + bd), (13.6 + adx * 1.4, 31 + bd), 16)
    m = TS(path, 1.8, 1.7)
    paint(cv, m, c["base"], c["ol"], shade=c["shade"], outline="all")


def head_base(cv, c, hd):
    m = E(16.6, 13.2 + hd, 10.6, 9)
    paint(cv, m, c["base"], c["ol"], shade=c["shade"], hi=c["hi"], outline="all")


# ----------------------------------------------------------------------------
# CHAZ — cão azul, orelha caída, tufo no topo e "asinha" de pelo atrás da cabeça
# ----------------------------------------------------------------------------
def chaz_tail(cv, c, p, bd):
    t = p["tdx"]
    path = bez((11.2, 32 + bd), (6, 33 + bd), (2.5 + t, 28 + bd), (4.6 + t, 23.5 + bd))
    body = TS(path, 1.7, 2.7)  # termina numa "clava" peluda
    paint(cv, body, c["base"], c["ol"], shade=c["shade"], outline="all")


def chaz_behind_head(cv, c, hd):
    wing = P([(10, 9 + hd), (4.2, 8 + hd), (6.8, 11 + hd), (3.4, 13.6 + hd), (10, 15 + hd)])
    paint(cv, wing, c["base"], c["ol"], shade=c["shade"], outline="all")
    nub = E(16.8, 3.3 + hd, 1.7, 1.7)
    paint(cv, nub, c["base"], c["ol"], outline="all")


def chaz_ear(cv, c, hd, ed):
    path = bez((14, 6.6 + hd + ed), (15, 12 + hd + ed), (11, 14.5 + hd + ed), (10.2, 20.4 + hd + ed))
    m = TS(path, 3.0, 2.0)
    paint(cv, m, c["ear"], c["ol"], shade=c["ear_shade"], outline="all")
    for (x, y) in ((12, 8), (12, 9)):  # brilho do pelo
        cv.put(x, y + hd + ed, c["shine"])


def chaz_face(cv, c, hd, mood="open"):
    # focinho de cachorro (sem contorno por cima do rosto) + nariz
    muz = E(25.6, 16.2 + hd, 2.9, 2.3)
    paint(cv, muz, c["base"], c["ol"], shade=c["shade"], outline="outer")
    for (x, y) in ((27, 15), (28, 15), (27, 16), (28, 16)):
        cv.put(x, y + hd, c["nose"])
    # olho grande, esclera creme, íris roxa olhando pra frente
    paint(cv, E(20.4, 11.8 + hd, 3.0, 3.6), c["sclera"], None, outline="all")
    paint(cv, E(21.5, 12.4 + hd, 1.9, 2.6), c["iris"], None, outline="all")
    cv.put(22, 12 + hd, c["pupil"]); cv.put(22, 13 + hd, c["pupil"])
    cv.put(20, 10 + hd, c["shine"])
    if mood == "smile":
        cv.put(24, 19 + hd, c["ol"]); cv.put(25, 19 + hd, c["ol"])


CHAZ = dict(
    name="chaz",
    c=dict(base="#1434f0", shade="#0e25b8", hi="#3b5dff", ol="#04040c",
           ear="#1029d4", ear_shade="#0b1c98", shine="#cfd8ff",
           sclera="#f4e8c0", iris="#7a4fd0", pupil="#2a1458", nose="#04040c",
           mark="#f2f2ff"),
    tail=chaz_tail, behind=chaz_behind_head, ear=chaz_ear, face=chaz_face,
)


# ----------------------------------------------------------------------------
# render genérico
# ----------------------------------------------------------------------------
def render(spec, p):
    c = spec["c"]
    cv = Canvas()
    bd, hd, ed = p.get("bd", 0), p.get("hd", 0), p.get("ed", 0)
    spec["tail"](cv, c, p, bd)
    leg(cv, c, 12.6 + p.get("far_dx", 0), p.get("far_lift", 0), bd, far=True)
    leg(cv, c, 14.8 + p.get("near_dx", 0), p.get("near_lift", 0), bd)
    torso(cv, c, bd)
    stamp(cv, THREE, 17, 25 + bd, c["mark"])
    arm(cv, c, p.get("adx", 0), bd)
    spec["behind"](cv, c, hd)
    head_base(cv, c, hd)
    spec["ear"](cv, c, hd, ed)
    spec["face"](cv, c, hd, p.get("mood", "open"))
    return cv


# poses
WALK = [
    dict(bd=0,  hd=0,  ed=0, near_dx=2,  far_dx=-2, adx=-1, tdx=0),
    dict(bd=-1, hd=-1, ed=1, near_dx=0,  far_dx=0,  far_lift=1, adx=0, tdx=-1),
    dict(bd=0,  hd=0,  ed=0, near_dx=-2, far_dx=2,  adx=1,  tdx=0),
    dict(bd=-1, hd=-1, ed=1, near_dx=0,  far_dx=0,  near_lift=1, adx=0, tdx=1),
]
IDLE = [
    dict(bd=0, hd=0, ed=0, tdx=0),
    dict(bd=0, hd=1, ed=0, tdx=1),
]
