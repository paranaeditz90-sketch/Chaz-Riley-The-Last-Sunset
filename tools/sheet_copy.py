"""Cópia fiel das folhas do Gemini pro jogo (decisão do diretor: "só copiar esses sprites").

Não redesenha nada: olho, boca, marca do peito e traço ficam exatamente como o Gemini fez.
O que este módulo faz é só o necessário pra virar sprite de jogo:
  1. tira o fundo (verde chapado ou xadrez) com alfa duro, sem franja verde/cinza;
  2. recorta os quadros da grade;
  3. (opcional) ajusta escala e cor de uma folha avulsa pra casar com a principal.
"""
from collections import deque

import numpy as np
from PIL import Image


def load(path, scale=1.0):
    im = Image.open(path).convert("RGB")
    if scale != 1.0:
        # redução por média de área ANTES de tirar o fundo: a borda fica limpa depois do recorte
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.BOX)
    return np.asarray(im).astype(np.int16)


def key_green(a):
    """Fundo verde chapado -> transparente. Franja preto+verde vira preto (despill)."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (g > r + 40) & (g > b + 40)
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    rgb = a.copy()
    rgb[..., 1] = np.minimum(g, np.maximum(r, b))      # nenhuma cor dos personagens tem verde dominante
    out[..., :3] = np.clip(rgb, 0, 255)
    out[..., 3] = np.where(bg, 0, 255)
    return out


def key_checker(a, hole_max=300):
    """Fundo xadrez branco/cinza -> transparente. Branco fechado dentro do contorno (olho, "3") fica;
    vão grande fechado (entre rabo e corpo) vira transparente."""
    mx, mn = a.max(-1), a.min(-1)
    light = (mn > 150) & ((mx - mn) < 40)
    H, W = light.shape
    bg = np.zeros_like(light)
    q = deque()
    for y in range(H):
        for x in (0, W - 1):
            if light[y, x] and not bg[y, x]:
                bg[y, x] = True; q.append((y, x))
    for x in range(W):
        for y in (0, H - 1):
            if light[y, x] and not bg[y, x]:
                bg[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and light[yy, xx] and not bg[yy, xx]:
                bg[yy, xx] = True; q.append((yy, xx))
    # componentes claros fechados: pequeno e branco = detalhe do desenho; grande ou com cinza do xadrez = vão
    seen = bg.copy()
    for y0 in range(H):
        for x0 in range(W):
            if light[y0, x0] and not seen[y0, x0]:
                comp = []; dq = deque([(y0, x0)]); seen[y0, x0] = True
                while dq:
                    y, x = dq.popleft(); comp.append((y, x))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < H and 0 <= xx < W and light[yy, xx] and not seen[yy, xx]:
                            seen[yy, xx] = True; dq.append((yy, xx))
                ys, xs = np.array(comp).T
                # medido na folha v2: olho/"3" têm no máx. 12% de cinza (borda); o vão do rabo tem 22%
                gray = ((mn[ys, xs] > 180) & (mn[ys, xs] < 212)).mean()
                if len(comp) > hole_max or gray > 0.18:
                    bg[ys, xs] = True
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    out[..., :3] = np.clip(a, 0, 255)
    out[..., 3] = np.where(bg, 0, 255)
    # franja (mistura contorno + xadrez, cinza sem saturação) encostada no fundo
    for _ in range(2):
        op = out[..., 3] > 0
        near = np.zeros_like(op)
        near[1:] |= ~op[:-1]; near[:-1] |= ~op[1:]; near[:, 1:] |= ~op[:, :-1]; near[:, :-1] |= ~op[:, 1:]
        c = out[..., :3].astype(np.int16)
        sat = c.max(-1) - c.min(-1)
        lum = c.mean(-1)
        fr = op & near & (sat < 35) & (lum > 60)
        out[fr & (lum > 120), 3] = 0
        out[fr & (lum <= 120), :3] = 0
    return out


def despeckle(rgba, min_px=12):
    """Ruído de JPEG: some com ilhas opacas minúsculas e tapa furinhos transparentes de 1-4 px."""
    op = rgba[..., 3] > 0
    H, W = op.shape
    for want in (True, False):
        seen = np.zeros_like(op)
        for y0 in range(H):
            for x0 in range(W):
                if op[y0, x0] == want and not seen[y0, x0]:
                    comp = []; dq = deque([(y0, x0)]); seen[y0, x0] = True; edge = False
                    while dq:
                        y, x = dq.popleft(); comp.append((y, x))
                        if y in (0, H - 1) or x in (0, W - 1):
                            edge = True
                        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            yy, xx = y + dy, x + dx
                            if 0 <= yy < H and 0 <= xx < W and op[yy, xx] == want and not seen[yy, xx]:
                                seen[yy, xx] = True; dq.append((yy, xx))
                    if want and len(comp) < min_px:
                        for y, x in comp:
                            rgba[y, x, 3] = 0
                    if not want and not edge and len(comp) <= 4:
                        for y, x in comp:
                            nb = [rgba[yy, xx, :3] for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1))
                                  if 0 <= yy < H and 0 <= xx < W and rgba[yy, xx, 3]]
                            if nb:
                                rgba[y, x, :3] = np.median(np.array(nb), 0)
                                rgba[y, x, 3] = 255
    return rgba


def runs(v, minlen):
    out, s = [], None
    for i, x in enumerate(v):
        if x and s is None:
            s = i
        if not x and s is not None:
            out.append((s, i - 1)); s = None
    if s is not None:
        out.append((s, len(v) - 1))
    return [q for q in out if q[1] - q[0] > minlen]


def grid(rgba, nrows, ncols, minlen=30):
    """Recorta os quadros pela projeção (colunas e linhas separadas por fundo)."""
    op = rgba[..., 3] > 0
    rows = runs(op.any(axis=1), minlen)
    assert len(rows) == nrows, f"linhas achadas: {rows}"
    frames = {}
    for r, (y0, y1) in enumerate(rows):
        band = op[y0:y1 + 1]
        cols = runs(band.any(axis=0), minlen)
        assert len(cols) == ncols, f"linha {r}: colunas achadas {cols}"
        for c, (x0, x1) in enumerate(cols):
            crop = rgba[y0:y1 + 1, x0:x1 + 1].copy()
            o = crop[..., 3] > 0
            ys, xs = np.nonzero(o.any(1))[0], np.nonzero(o.any(0))[0]
            frames[(r, c)] = crop[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return frames


def color_match(rgba, pairs):
    """Casa a cor de uma folha avulsa com a principal: mapa linear por canal a partir de pares (origem, destino)."""
    src = np.array([p[0] for p in pairs], float)
    dst = np.array([p[1] for p in pairs], float)
    out = rgba.copy()
    for ch in range(3):
        k, b = np.polyfit(src[:, ch], dst[:, ch], 1)
        out[..., ch] = np.clip(rgba[..., ch] * k + b, 0, 255).astype(np.uint8)
    return out


def head_cx(fr):
    """Âncora horizontal: mediana do x dos pixels opacos no topo (cabeça), estável no ciclo de passo."""
    o = fr[..., 3] > 0
    h = o.shape[0]
    ys, xs = np.nonzero(o[: int(h * 0.45)])
    return float(np.median(xs))


def place(fr, cell_w, cell_h, ground, cx):
    """Põe o quadro na célula: pé no chão (ground) e cabeça no centro (cx)."""
    out = np.zeros((cell_h, cell_w, 4), np.uint8)
    h, w = fr.shape[:2]
    dx = int(round(cx - head_cx(fr)))
    dy = ground - h
    ys0, xs0 = max(0, -dy), max(0, -dx)
    ys1, xs1 = min(h, cell_h - dy), min(w, cell_w - dx)
    assert ys0 == 0 and xs0 == 0 and ys1 == h and xs1 == w, f"quadro {w}x{h} não cabe na célula (dx={dx}, dy={dy})"
    region = out[dy:dy + h, dx:dx + w]
    m = fr[..., 3] > 0
    region[m] = fr[m]
    return out
