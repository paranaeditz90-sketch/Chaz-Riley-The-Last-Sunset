"""Restaura uma folha de pixel art gerada (Gemini) pro grid real, sem borrar.

Não é conversor de desenho -> pixel art: a imagem já É pixel art, só veio ampliada (escala
não inteira) e em JPEG com fundo xadrez. Aqui cada bloco volta a ser 1 pixel com a cor dominante,
travada numa paleta curta. Fundo xadrez sai por inundação a partir da borda; branco cercado de
cor (olho, "3") fica.

Uso: python3 -P tools/restore_gemini.py <entrada.jpg> <saida.png> [largura_nativa=256]
"""
import sys
from collections import deque

import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
NW = int(sys.argv[3]) if len(sys.argv) > 3 else 256
DARK = float(sys.argv[4]) if len(sys.argv) > 4 else 0.35   # fração escura que vira linha
DARKV = int(sys.argv[5]) if len(sys.argv) > 5 else 75       # brilho máx. pra contar como linha

a = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
H, W, _ = a.shape
s = W / NW
NH = int(round(H / s))

# classes: 0 fundo-claro (neutro claro), 1 azul, 2 preto, 4 roxo, 5 rosa
PAL = {1: (42, 59, 232), 2: (0, 0, 0), 3: (255, 255, 255), 4: (138, 79, 216), 5: (255, 111, 145)}


def classify(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    c = np.full(r.shape, 1, np.int8)
    c[mx < DARKV] = 2          # inclui linha azul-escura (orelha/braço), não só preto
    neutral_light = (mn > 160) & ((mx - mn) < 40)
    c[neutral_light] = 0
    purple = (r > 110) & (b > 150) & (g < 140) & (r - g > 40) & ~neutral_light
    c[purple] = 4
    pink = (r > 200) & (g < 160) & (b < 190) & (r - b > 30)
    c[pink] = 5
    return c


cls_full = classify(a)


def sample(ox, oy):
    """Classe de cada bloco por prioridade: escuro >=35% vira contorno (preserva linha fina);
    claro >=50% vira claro; roxo >=30% vira roxo; senão azul. Também devolve a pureza."""
    out = np.zeros((NH, NW), np.int8)
    pur = np.zeros((NH, NW), np.float32)
    for j in range(NH):
        y0, y1 = int(oy + j * s), int(oy + (j + 1) * s)
        for i in range(NW):
            x0, x1 = int(ox + i * s), int(ox + (i + 1) * s)
            blk = cls_full[max(0, y0):min(H, y1), max(0, x0):min(W, x1)].ravel()
            if blk.size == 0:
                continue
            cnt = np.bincount(blk, minlength=6) / blk.size
            if cnt[2] >= DARK:
                out[j, i] = 2
            elif cnt[0] >= 0.5:
                out[j, i] = 0
            elif cnt[4] >= 0.3:
                out[j, i] = 4
            elif cnt[5] >= 0.3:
                out[j, i] = 5
            else:
                out[j, i] = 1
            pur[j, i] = cnt.max()
    return out, pur


# deslocamento de grade: o que deixa os blocos mais "puros"
best = None
for oy in np.arange(-s / 2, s / 2, s / 4):
    for ox in np.arange(-s / 2, s / 2, s / 4):
        g, pur = sample(ox, oy)
        score = pur.mean()
        if best is None or score > best[0]:
            best = (score, ox, oy, g)
score, ox, oy, g = best
print(f"escala {s:.4f}  grade nativa {NW}x{NH}  deslocamento ({ox:.2f},{oy:.2f})  pureza {score:.3f}")

# fundo: inunda a partir da borda pelas células claras
bg = np.zeros_like(g, bool)
q = deque((j, i) for j in range(NH) for i in range(NW) if (j in (0, NH - 1) or i in (0, NW - 1)) and g[j, i] == 0)
for j, i in q:
    bg[j, i] = True
while q:
    j, i = q.popleft()
    for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        y, x = j + dj, i + di
        if 0 <= y < NH and 0 <= x < NW and not bg[y, x] and g[y, x] == 0:
            bg[y, x] = True
            q.append((y, x))

# regiões claras fechadas que encostam em cor = olho/"3" no original: registra posição, mas NÃO pinta
import json
whites = []
seen = np.zeros_like(bg)
for j in range(NH):
    for i in range(NW):
        if g[j, i] == 0 and not bg[j, i] and not seen[j, i]:
            comp, touch = [], False
            dq = deque([(j, i)]); seen[j, i] = True
            while dq:
                y, x = dq.popleft(); comp.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < NH and 0 <= xx < NW:
                        if g[yy, xx] == 0 and not bg[yy, xx] and not seen[yy, xx]:
                            seen[yy, xx] = True; dq.append((yy, xx))
                        elif g[yy, xx] in (1, 4):
                            touch = True
            ys, xs = zip(*comp)
            if touch and len(comp) <= 12 * (NW / 256) ** 2:
                whites.append(dict(x0=min(xs), y0=min(ys), x1=max(xs), y1=max(ys), n=len(comp)))
            small = len(comp) <= 12 * (NW / 256) ** 2   # olho/"3" são pequenos; vão entre rabo e corpo é grande
            for y, x in comp:
                g[y, x] = 1 if (touch and small) else 0   # olho/"3" vira azul (carimbo depois); buraco vira fundo
                if not (touch and small):
                    bg[y, x] = True
# roxo também é do olho: vira azul (o carimbo do olho repõe)
pur_cells = [(int(y), int(x)) for y, x in zip(*np.nonzero(g == 4))]
g[g == 4] = 1
json.dump(dict(whites=whites, purple=pur_cells), open(dst.replace(".png", "_detalhes.json"), "w"))

# pixels soltos: componentes opacos de até 3 px viram fundo
opq = ~bg
seen2 = np.zeros_like(opq)
for j in range(NH):
    for i in range(NW):
        if opq[j, i] and not seen2[j, i]:
            comp = []; dq = deque([(j, i)]); seen2[j, i] = True
            while dq:
                y, x = dq.popleft(); comp.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < NH and 0 <= xx < NW and opq[yy, xx] and not seen2[yy, xx]:
                        seen2[yy, xx] = True; dq.append((yy, xx))
            if len(comp) <= 3 * (NW // 256):
                for y, x in comp:
                    bg[y, x] = True
img = np.zeros((NH, NW, 4), np.uint8)
for k, rgb in PAL.items():
    m = (g == k) & ~bg
    img[m, :3] = rgb
    img[m, 3] = 255
Image.fromarray(img, "RGBA").save(dst)
print("salvo", dst, f"{NW}x{NH}")
