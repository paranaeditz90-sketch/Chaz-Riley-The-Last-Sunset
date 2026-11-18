"""Pequeno kit de pixel art procedural.

Tudo é desenhado em grade inteira (sem antialiasing), parte por parte, de trás
pra frente. Cada parte ganha contorno automático, então o resultado fica
consistente entre frames e entre personagens.
"""
import numpy as np
from PIL import Image, ImageDraw

W, H = 32, 40  # tamanho de um frame (px do jogo)


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


class Canvas:
    def __init__(self):
        self.px = np.zeros((H, W, 4), np.uint8)

    def solid(self):
        return self.px[..., 3] > 0

    def put(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            self.px[y, x] = hexc(color)

    def image(self):
        return Image.fromarray(self.px, "RGBA")


S = 8  # supersampling: as formas são desenhadas em coordenadas contínuas e reduzidas pra grade


def _mk(fn):
    im = Image.new("L", (W * S, H * S), 0)
    fn(ImageDraw.Draw(im))
    a = np.array(im, dtype=np.float32).reshape(H, S, W, S).mean(axis=(1, 3))
    return a >= 127.5  # pixel liga se >= 50% coberto


def _s(pts):
    return [(x * S, y * S) for x, y in pts]


def E(cx, cy, rx, ry):
    return _mk(lambda d: d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S - 1, (cy + ry) * S - 1], fill=255))


def R(x0, y0, x1, y1):
    return _mk(lambda d: d.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], fill=255))


def P(pts):
    return _mk(lambda d: d.polygon(_s(pts), fill=255))


def bez(p0, p1, p2, p3, n=28):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return out


def TS(path, r0, r1):
    """Traço afilado: círculos ao longo de um caminho, raio indo de r0 a r1."""
    def f(d):
        n = len(path)
        for i, (x, y) in enumerate(path):
            r = r0 + (r1 - r0) * i / max(n - 1, 1)
            d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S - 1, (y + r) * S - 1], fill=255)
    return _mk(f)


def sh(m, dx, dy):
    """out[y+dy, x+dx] = m[y, x]"""
    out = np.zeros_like(m)
    ys, yd = slice(max(dy, 0), H + min(dy, 0)), slice(max(-dy, 0), H + min(-dy, 0))
    xs, xd = slice(max(dx, 0), W + min(dx, 0)), slice(max(-dx, 0), W + min(-dx, 0))
    out[ys, xs] = m[yd, xd]
    return out


def dilate4(m):
    return m | sh(m, 1, 0) | sh(m, -1, 0) | sh(m, 0, 1) | sh(m, 0, -1)


def clean(m):
    """Remove pixels sem nenhum vizinho (4-conexo): ruído do supersampling."""
    n = sh(m, 1, 0).astype(int) + sh(m, -1, 0) + sh(m, 0, 1) + sh(m, 0, -1)
    return m & (n > 0)


def paint(cv, m, fill, ol, shade=None, hi=None, outline="all"):
    """Pinta uma parte.

    outline: 'all'   -> contorno completo (separa a parte do que está atrás)
             'outer' -> contorno só onde não há nada pintado ainda
    shade/hi: cor da sombra (borda de baixo/direita) e do brilho (cima/esquerda).
    """
    m = clean(m)
    if not m.any():
        return
    ring = dilate4(m) & ~m
    if outline == "outer":
        ring &= ~cv.solid()
    if ol:
        cv.px[ring] = hexc(ol)
    cv.px[m] = hexc(fill)
    if shade or hi:
        below, right = sh(m, 0, -1), sh(m, -1, 0)
        above, left = sh(m, 0, 1), sh(m, 1, 0)
        sm = m & (~below | ~right)
        hm = m & (~above | ~left) & ~sm
        if hi:
            cv.px[hm] = hexc(hi)
        if shade:
            cv.px[sm] = hexc(shade)


def stamp(cv, rows, x, y, color, key="#"):
    """Carimba um glifo ASCII (ex.: a marca '3' no peito)."""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == key:
                cv.put(x + i, y + j, color)


def upscale(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)
