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


# ------------------------------------------------------------------ conserto autorizado pelo diretor
def _olho(f):
    """Centro do branco do olho (creme no alto da cabeça; o "3" fica mais embaixo)."""
    c = f[..., :3].astype(int)
    p = (f[..., 3] > 0) & (c[..., 0] > 200) & (c[..., 1] > 170)
    p[int(f.shape[0] * 0.55):] = False
    ys, xs = np.nonzero(p)
    return xs.mean(), ys.mean()


def trocar_cabeca(run, walk, abaixo_do_olho=20):
    """Riley de perfil correndo: o Gemini pôs uma orelha caída de cachorro a mais.
    Troca a cabeça pela do quadro de andar da mesma direção (pixels do próprio Gemini), alinhada pelo olho.
    Na emenda, liga nuca e costas em linha reta e refaz o contorno só onde abriu borda nova."""
    from scipy.ndimage import distance_transform_edt

    ex_r, ey_r = _olho(run)
    ex_w, ey_w = _olho(walk)
    dx, dy = int(round(ex_r - ex_w)), int(round(ey_r - ey_w))
    cut = int(round(ey_r)) + abaixo_do_olho
    H, W = run.shape[:2]
    pad = 40
    out = np.zeros((H + pad, W + 2 * pad, 4), np.uint8)
    out[pad:pad + H, pad:pad + W] = run
    out[:pad + cut, :, 3] = 0                                   # some a cabeça antiga (com a orelha extra)
    m = (walk[..., 3] > 0) & ((np.arange(walk.shape[0])[:, None] + dy) < cut)
    ys, xs = np.nonzero(m)
    out[ys + dy + pad, xs + dx + pad] = walk[ys, xs]           # cabeça do quadro de andar

    costas_dir = ex_r < W / 2                                   # olho à esquerda = costas à direita
    cc = out[..., :3].astype(int)
    tres = (out[..., 3] > 0) & (cc[..., 0] > 200) & (cc[..., 1] > 170)
    tres[:pad + int(H * 0.55)] = False
    xc = int(np.nonzero(tres)[1].mean())                        # centro do corpo = centro do "3"
    passo = 1 if costas_dir else -1

    def borda(y):                                               # fim do corpo nessa linha (rabo separado não conta)
        x = xc
        while 0 <= x + passo < out.shape[1] and out[y, x + passo, 3] > 0:
            x += passo
        return x

    y0, y1 = pad + cut - 6, pad + cut + 8
    e0, e1 = borda(y0), borda(y1)
    if abs(e1 - e0) > 25:
        e1 = e0
    corpo = (run[..., 3] > 0) & (run[..., 0].astype(int) > run[..., 1].astype(int) + 40)
    cor = np.median(run[corpo][:, :3], 0).astype(np.uint8)
    for y in range(y0, y1 + 1):
        e = int(round(e0 + (e1 - e0) * (y - y0) / (y1 - y0)))
        row, s1 = out[y], borda(y)
        if costas_dir:
            if e < s1:
                row[e + 1:s1 + 1, 3] = 0
            else:
                for x in range(s1 + 1, e + 1):
                    if row[x, 3]:
                        break
                    row[x, :3], row[x, 3] = cor, 255
        else:
            if e > s1:
                row[s1:e, 3] = 0
            else:
                for x in range(s1 - 1, e - 1, -1):
                    if row[x, 3]:
                        break
                    row[x, :3], row[x, 3] = cor, 255

    op = out[..., 3] > 0
    dist = distance_transform_edt(op)
    zona = np.zeros_like(op)
    zona[pad + cut - 8:pad + cut + 12] = True
    c = out[..., :3].astype(int)
    pele = op & (c.max(-1) >= 70) & (c[..., 0] > c[..., 1] + 40) & (c[..., 0] < 200)
    out[zona & pele & (dist <= 3), :3] = (5, 2, 1)
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def trocar_rosto(alvo, fonte, cor_corpo):
    """Chaz de frente: o Gemini fez andar/correr de olho fechado. Copia o rosto (olhos, nariz, boca)
    de um quadro de olho aberto da MESMA folha pro quadro alvo, alinhado pelo contorno da cabeça.
    Também serve ao contrário (rosto de olho fechado num quadro parado = piscada)."""
    def mask_cabeca(f, h):
        return f[:h, :, 3] > 0
    c = fonte[..., :3].astype(int)
    olho = (fonte[..., 3] > 0) & (((c.min(-1) > 190)) | ((c[..., 2] > 150) & (c[..., 0] > 100) & (c[..., 1] < 130)))
    olho[int(fonte.shape[0] * 0.5):] = False
    if olho.sum() < 20:                                         # fonte de olho fechado: usa a faixa dos olhos do alvo
        c2 = alvo[..., :3].astype(int)
        olho = (alvo[..., 3] > 0) & (((c2.min(-1) > 190)) | ((c2[..., 2] > 150) & (c2[..., 0] > 100) & (c2[..., 1] < 130)))
        olho[int(alvo.shape[0] * 0.5):] = False
    ys, xs = np.nonzero(olho)
    y0, y1, x0, x1 = ys.min() - 6, ys.max() + 13, xs.min() - 3, xs.max() + 3
    # alinhamento: deslocamento que mais sobrepõe a silhueta da cabeça
    h = y1 + 4
    best = None
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            a = np.zeros((h + 20, max(alvo.shape[1], fonte.shape[1]) + 20), bool)
            b = a.copy()
            ma = mask_cabeca(alvo, min(h, alvo.shape[0]))
            mf = mask_cabeca(fonte, min(h, fonte.shape[0]))
            a[10:10 + ma.shape[0], 10:10 + ma.shape[1]] = ma
            yy, xx = np.nonzero(mf)
            yy, xx = yy + 10 + dy, xx + 10 + dx
            ok = (yy >= 0) & (yy < b.shape[0]) & (xx >= 0) & (xx < b.shape[1])
            b[yy[ok], xx[ok]] = True
            s = (a & b).sum() / max(1, (a | b).sum())
            if best is None or s > best[0]:
                best = (s, dx, dy)
    _, dx, dy = best
    out = alvo.copy()
    cor = np.array(cor_corpo, np.uint8)
    # área trocada = olhos da fonte (já no lugar do alvo) UNIÃO olhos do alvo: não sobra branco do olho velho
    c2 = alvo[..., :3].astype(int)
    olho_alvo = (alvo[..., 3] > 0) & (((c2.min(-1) > 190)) | ((c2[..., 2] > 150) & (c2[..., 0] > 100) & (c2[..., 1] < 130)))
    olho_alvo[int(alvo.shape[0] * 0.5):] = False
    ty0, ty1, tx0, tx1 = y0 + dy, y1 + dy, x0 + dx, x1 + dx
    if olho_alvo.sum() >= 20:
        ays, axs = np.nonzero(olho_alvo)
        ty0, ty1 = min(ty0, ays.min() - 6), max(ty1, ays.max() + 13)
        tx0, tx1 = min(tx0, axs.min() - 3), max(tx1, axs.max() + 3)
    # branco do olho com a cor do alvo (a folha nova às vezes vem creme) e brilho solto fora do olho vira corpo
    from scipy.ndimage import binary_dilation
    branco_alvo = None
    if olho_alvo.sum() >= 20:
        bw = alvo[olho_alvo & (c2.min(-1) > 190)][:, :3]
        if len(bw):
            branco_alvo = np.median(bw, 0).astype(np.uint8)
    cf = fonte[..., :3].astype(int)
    olho_f = (fonte[..., 3] > 0) & (((cf.min(-1) > 170)) | ((cf[..., 2] > 150) & (cf[..., 0] > 100) & (cf[..., 1] < 130)))
    olho_f[int(fonte.shape[0] * 0.5):] = False
    if olho_f.sum() >= 20:
        from scipy.ndimage import label as _label
        lab, n = _label(olho_f)
        tam = np.bincount(lab.ravel())[1:]
        olho_f = np.isin(lab, np.nonzero(tam >= 0.3 * tam.max())[0] + 1)   # só os olhos; risco fino de brilho fica de fora
        fys = np.nonzero(olho_f)[0]
        lab_olho = binary_dilation(olho_f, iterations=3)
        fundo_olho = fys.max()
    else:
        lab_olho, fundo_olho = None, None
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            y, x = ty - dy, tx - dx
            if not (0 <= ty < out.shape[0] and 0 <= tx < out.shape[1]) or not out[ty, tx, 3]:
                continue
            if not (0 <= y < fonte.shape[0] and 0 <= x < fonte.shape[1]):
                out[ty, tx, :3] = cor
                continue
            if fonte[y, x, 3]:
                out[ty, tx] = fonte[y, x]
                px = fonte[y, x, :3].astype(int)
                # resto de JPEG quase da cor do corpo (risquinho fantasma onde era o olho) vira corpo
                if np.abs(px - cor.astype(int)).sum() < 70:
                    out[ty, tx, :3] = cor
                elif px.min() > 150 and lab_olho is not None:
                    if lab_olho[y, x]:
                        if branco_alvo is not None and (px.max() - px.min()) < 60:
                            out[ty, tx, :3] = branco_alvo
                    elif y < fundo_olho:
                        out[ty, tx, :3] = cor          # brilho/risco claro na orelha, fora do olho
                elif (lab_olho is not None and not lab_olho[y, x] and y < fundo_olho
                      and px.min() > int(cor.min()) + 60 and px.sum() > int(cor.astype(int).sum()) + 150):
                    out[ty, tx, :3] = cor              # risco azul-claro de brilho (estilo da folha nova)
            else:
                out[ty, tx, :3] = cor
    return out



# ------------------------------------------------------------------ imagens de outras IAs (ChatGPT etc.)
def tem_alfa(path):
    """PNG com transparência de verdade (o ChatGPT costuma entregar assim)."""
    im = Image.open(path)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        return (np.asarray(im.convert("RGBA"))[..., 3] < 128).mean() > 0.1
    return False


def key_alpha(path, scale=1.0):
    """Usa a transparência do próprio arquivo, com alfa duro (sem borda meio transparente)."""
    im = Image.open(path).convert("RGBA")
    if scale != 1.0:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.BOX)
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0).astype(np.uint8)
    return a


def fundo_verde(a):
    """Cantos da imagem são verde chapado?"""
    h, w = a.shape[:2]
    cantos = np.concatenate([a[:10, :10].reshape(-1, 3), a[:10, -10:].reshape(-1, 3), a[-10:, :10].reshape(-1, 3), a[-10:, -10:].reshape(-1, 3)])
    r, g, b = cantos[:, 0].astype(int), cantos[:, 1].astype(int), cantos[:, 2].astype(int)
    return ((g > r + 40) & (g > b + 40)).mean() > 0.8
