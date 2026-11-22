"""Olhos animados pras cutscenes, a partir da arte em alta do diretor (sem redesenhar o personagem).

Pra cada expressão de olho aberto:
  - acha a abertura do olho (esclera + íris) e a íris (com pupila e brilho);
  - gera "remendos" do olho com a íris em várias direções (o personagem olha pra quem fala com ele);
  - gera pálpebras em 3 estágios (40%, 75%, fechado): pele na cor do pelo descendo + a linha da pálpebra,
    na cor e na grossura do contorno do próprio desenho. Fechado = só a curva de baixo do olho, como no
    desenho de olho fechado do próprio diretor.
O jogo põe o remendo exatamente em cima do olho original; se algo falhar, aparece o desenho original.

Uso: python3 -P tools/olhos_retratos.py            (gera atlas + dados)
     python3 -P tools/olhos_retratos.py --ver DIR  (só desenha a detecção pra conferir)
Saída: game/public/assets/retratos/olhos_<nome>.png + game/src/olhos_dados.js
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RET = os.path.join(RAIZ, "game", "public", "assets", "retratos")

# por personagem: como reconhecer esclera, íris e contorno; grossura da linha da pálpebra (px da arte)
PARAM = {
    "chaz": dict(esclera=lambda r, g, b: (r > 200) & (g > 185) & (b > 120) & (r - b > 12), iris=lambda r, g, b: (b - g > 45) & (r - g > 12) & (b > 120),
                 contorno=55, linha=5),
    "riley": dict(esclera=lambda r, g, b: (r > 200) & (g > 180) & (b > 140) & (r - b > 8), iris=lambda r, g, b: (b - g > 45) & (r - g > 12) & (b > 110),
                  contorno=45, linha=6),
    # medido na arte: esclera ~(173,131,143), íris ~(120,80,110), pelo ~(60,37,47)
    "nevoa": dict(esclera=lambda r, g, b: (r > 140) & (g > 100) & (b > 110) & (r - g > 20) & (r - g < 70), iris=lambda r, g, b: (b - g > 20) & (r - g > 25) & (b > 80) & (g < 105) & (r < 160),
                  contorno=28, linha=5),
}
OLHARES = {  # direção -> (x, y) em fração do curso disponível
    "natural": None, "centro": (0, 0), "esquerda": (-1, 0), "direita": (1, 0), "cima": (0, -1), "baixo": (0, 1),
    "cima_esquerda": (-1, -1), "cima_direita": (1, -1), "baixo_esquerda": (-1, 1), "baixo_direita": (1, 1),
}
ESTAGIOS = (0.4, 0.75, 1.0)
PERFIL = {"nevoa_16"}  # vista de lado: um olho só é o certo
PRETO = 60  # pedido do diretor: nada de pontinho preto no olho (pupila quase preta vira a cor da íris)


def detectar(nome, chave, an):
    p = PARAM[nome]
    im = np.asarray(Image.open(os.path.join(RET, chave + ".png")).convert("RGBA")).astype(np.int32)
    r, g, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    dentro = a > 200
    cab = np.zeros_like(dentro)
    alto = an["pe"] - an["topo"]
    deitado = an["w"] > 1.4 * alto  # deitado: a cabeça não fica em cima
    cab[an["topo"]:an["topo"] + (alto if deitado else int(alto * 0.5))] = True
    escl = p["esclera"](r, g, b) & dentro & cab
    iris = p["iris"](r, g, b) & dentro & cab
    brilho = (r > 235) & (g > 235) & (b > 235) & dentro & cab
    olho = ndimage.binary_closing(escl | iris | brilho, iterations=2)
    lab, n = ndimage.label(olho)
    olhos = []
    for i in range(1, n + 1):
        m = lab == i
        area = m.sum()
        if area < 120 or escl[m].mean() < 0.15 or iris[m].mean() < 0.04:
            continue
        olhos.append(ndimage.binary_fill_holes(m))
    olhos = sorted(olhos, key=lambda m: -m.sum())[:2]
    olhos = sorted(olhos, key=lambda m: np.nonzero(m)[1].mean())
    out = []
    for abertura in olhos:
        ir = ndimage.binary_fill_holes(ndimage.binary_closing((iris | brilho) & ndimage.binary_dilation(abertura, iterations=1), iterations=2)) & abertura
        # só o maior pedaço de íris (brilhos soltos na esclera não contam)
        li, ni = ndimage.label(ir)
        if ni == 0:
            continue
        tam = ndimage.sum(np.ones_like(ir), li, range(1, ni + 1))
        ir = li == (int(np.argmax(tam)) + 1)
        if ir.sum() < 25:
            continue
        cor_escl = np.median(im[escl & abertura][:, :3], 0)
        anel = ndimage.binary_dilation(abertura, iterations=p["linha"] + 3) & ~abertura
        escuro = anel & (im[..., :3].max(-1) < p["contorno"] + 30)
        longe = ndimage.binary_dilation(abertura, iterations=p["linha"] + 16) & ~ndimage.binary_dilation(abertura, iterations=p["linha"] + 8) & dentro
        pele = longe & (im[..., :3].max(-1) > p["contorno"] + 15) & ~escl & ~iris & ~brilho
        cor_pele = np.median(im[pele][:, :3], 0) if pele.sum() > 20 else np.array([0, 0, 0])
        cor_linha = np.median(im[escuro][:, :3], 0) if escuro.sum() > 10 else np.array([10, 8, 12])
        out.append(dict(abertura=abertura, iris=ir, anel=escuro, cor_escl=cor_escl, cor_pele=cor_pele, cor_linha=cor_linha))
    # de frente com um olho só achado: piscaria um olho (piscadela). Melhor não animar essa expressão.
    if len(out) == 1 and chave not in PERFIL:
        out = []
    return im, out


def remendos(nome, chave, an):
    """Remendos de um retrato: [{x, y, olhar: {dir: img}, palpebra: [img x3]}]"""
    im, olhos = detectar(nome, chave, an)
    lin = PARAM[nome]["linha"]
    res = []
    for o in olhos:
        ab, ir = o["abertura"], o["iris"]
        ys, xs = np.nonzero(ab)
        m = lin + 6
        y0, y1, x0, x1 = max(0, ys.min() - m), min(im.shape[0], ys.max() + m + 1), max(0, xs.min() - m), min(im.shape[1], xs.max() + m + 1)
        base = im[y0:y1, x0:x1].copy()
        abc = ab[y0:y1, x0:x1]
        irc = ir[y0:y1, x0:x1]
        # olho sem íris (esclera no lugar): apaga com 2 px de folga pra não sobrar fiozinho da borda suavizada
        sem = base.copy()
        apagar = ndimage.binary_dilation(irc, iterations=2) & abc
        sem[apagar, :3] = o["cor_escl"]
        irc = ndimage.binary_dilation(irc, iterations=1) & abc
        iy, ix = np.nonzero(irc)
        icx, icy = ix.mean(), iy.mean()
        rx = (ix.max() - ix.min() + 1) / 2
        ry = (iy.max() - iy.min() + 1) / 2
        ay, ax = np.nonzero(abc)
        ocx = (ax.min() + ax.max()) / 2
        livre_x = max(0.0, (ax.max() - ax.min() + 1) / 2 - rx * 0.55)
        livre_y = max(0.0, ((ay.max() - ay.min() + 1) / 2 - ry * 0.6) * 0.6)
        move = irc.sum() / max(1, abc.sum()) >= 0.2  # íris quase escondida (choro, sono pesado): não mexe
        pix = base[irc].copy()
        # tira pontinho preto (pupila quase preta) de dentro da íris: vira a cor da própria íris
        escuro = pix[:, :3].max(-1) < PRETO
        if escuro.any() and (~escuro).sum() > 10:
            normal = pix[~escuro, :3]
            normal = normal[normal.max(-1) < 230]  # sem os brilhos brancos
            if len(normal):
                pix[escuro, :3] = np.median(normal, 0)
        olhar = {}
        for nomeo, d in OLHARES.items():
            if d is None or not move:
                dx, dy = 0, 0
            else:
                dx = int(round(ocx + d[0] * livre_x - icx))
                dy = int(round(d[1] * livre_y))
            if dx == 0 and dy == 0:
                # íris no lugar original: o desenho original, só sem o pontinho preto
                img = base.copy()
                img[irc] = pix
                olhar[nomeo] = img.astype(np.uint8)
                continue
            img = sem.copy()
            ty, tx = iy + dy, ix + dx
            ok = (ty >= 0) & (ty < img.shape[0]) & (tx >= 0) & (tx < img.shape[1])
            ty, tx, pp = ty[ok], tx[ok], pix[ok]
            dentro = abc[ty, tx]
            img[ty[dentro], tx[dentro]] = pp[dentro]
            olhar[nomeo] = img.astype(np.uint8)
        # pálpebras: pele descendo do contorno de cima até a curva de baixo
        cols = np.arange(abc.shape[1])
        topo = np.full(len(cols), -1)
        fundo = np.full(len(cols), -1)
        for c in cols:
            rr = np.nonzero(abc[:, c])[0]
            if len(rr):
                topo[c], fundo[c] = rr.min(), rr.max()
        validas = np.nonzero(topo >= 0)[0]
        cmin, cmax = validas.min(), validas.max()
        anel = o["anel"][y0:y1, x0:x1]
        palpebras = []
        # olho fechado = arco suave de canto a canto (seguir a curva de baixo fazia gancho nos cantos do olho
        # amendoado do Névoa); nunca abaixo do fundo do olho
        yL = (topo[cmin] + fundo[cmin]) / 2
        yR = (topo[cmax] + fundo[cmax]) / 2
        reta = {c: yL + (yR - yL) * (c - cmin) / max(1, cmax - cmin) for c in validas}
        fundo_util = np.array([fundo[c] - reta[c] for c in validas])
        prof = max(2.0, float(np.percentile(fundo_util, 90)) * 0.8)
        arco = {}
        for c in validas:
            u = (c - cmin) / max(1, cmax - cmin)
            arco[c] = min(fundo[c], reta[c] + prof * (1 - (2 * u - 1) ** 2))
        for t in ESTAGIOS:
            p = np.zeros_like(base)
            lid = np.full(len(cols), np.nan)
            for c in validas:
                lid[c] = topo[c] + t * (max(arco[c], topo[c]) - topo[c])
            # cantos: continua a curva até o contorno
            if t < 1:  # aberto em parte: estica a pálpebra até o contorno dos cantos (fechado já cobre tudo)
                for c in range(max(0, cmin - lin - 3), cmin):
                    lid[c] = lid[cmin]
                for c in range(cmax + 1, min(len(cols), cmax + lin + 4)):
                    lid[c] = lid[cmax]
            area = (abc | anel | ndimage.binary_dilation(abc, iterations=lin + 3)) & (base[..., 3] > 0)
            yy = np.arange(abc.shape[0])[:, None]
            acima = (yy < np.nan_to_num(lid, nan=-1)[None, :] - lin * 0.3) & area
            if t >= 1:
                acima = area.copy()  # fechado: o olho inteiro vira pele, só fica a linha do arco
            p[acima, :3] = o["cor_pele"]
            p[acima, 3] = 255
            pi = Image.fromarray(p.astype(np.uint8), "RGBA")
            dr = ImageDraw.Draw(pi)
            pts = [(c, lid[c]) for c in range(len(cols)) if not np.isnan(lid[c])]
            cor = tuple(int(v) for v in o["cor_linha"]) + (255,)
            dr.line(pts, fill=cor, width=lin, joint="curve")
            for (cx, cy) in (pts[0], pts[-1]):
                dr.ellipse((cx - lin / 2, cy - lin / 2, cx + lin / 2, cy + lin / 2), fill=cor)
            palpebras.append(np.asarray(pi))
        res.append(dict(x=int(x0), y=int(y0), olhar=olhar, palpebra=palpebras))
    return res


def atlas(nome, chaves, ancoras):
    """Empacota os remendos de um personagem numa imagem só (prateleiras) + dados por expressão."""
    itens = []
    dados = {}
    for k in chaves:
        rs = remendos(nome, k, ancoras[k])
        dados[k] = []
        for e, r in enumerate(rs):
            ent = {"x": r["x"], "y": r["y"], "olhar": {}, "palpebra": []}
            for d, img in r["olhar"].items():
                fr = f"{k}_o{e}_{d}"
                itens.append((fr, img))
                ent["olhar"][d] = fr
            for s, img in enumerate(r["palpebra"]):
                fr = f"{k}_o{e}_p{s}"
                itens.append((fr, img))
                ent["palpebra"].append(fr)
            dados[k].append(ent)
    larg = 2048
    x = y = alt_fila = 0
    pos = {}
    for fr, img in sorted(itens, key=lambda t: -t[1].shape[0]):
        h, w = img.shape[:2]
        if x + w + 2 > larg:
            x, y = 0, y + alt_fila + 2
            alt_fila = 0
        pos[fr] = (x, y, w, h)
        x += w + 2
        alt_fila = max(alt_fila, h)
    tela = np.zeros((y + alt_fila + 2, larg, 4), np.uint8)
    for fr, img in itens:
        x, y, w, h = pos[fr]
        tela[y:y + h, x:x + w] = img
    Image.fromarray(tela, "RGBA").save(os.path.join(RET, f"olhos_{nome}.png"), optimize=True)
    frames = {fr: {"frame": {"x": x, "y": y, "w": w, "h": h}} for fr, (x, y, w, h) in pos.items()}
    return dados, {"frames": frames, "meta": {"image": f"olhos_{nome}.png", "size": {"w": larg, "h": tela.shape[0]}, "scale": 1}}


def main():
    ancoras = {}
    for n in PARAM:
        ancoras.update(json.load(open(os.path.join(RET, f"{n}_ancoras.json"))))
    todos, atlases = {}, {}
    for n in PARAM:
        chaves = sorted(k for k in ancoras if k.startswith(n + "_"))
        dados, at = atlas(n, chaves, ancoras)
        todos.update(dados)
        atlases[n] = at
        print(n, sum(len(v) for v in dados.values()), "olhos em", sum(1 for v in dados.values() if v), "expressões")
    with open(os.path.join(RAIZ, "game", "src", "olhos_dados.js"), "w") as fh:
        fh.write("// Gerado por tools/olhos_retratos.py. Não editar à mão.\n")
        fh.write("// Por expressão: olhos [{x, y (canto do remendo na arte), olhar: {direção: quadro}, palpebra: [40%, 75%, fechado]}]\n")
        fh.write("export const OLHOS = " + json.dumps(todos) + ";\n")
        fh.write("export const ATLAS_OLHOS = " + json.dumps(atlases) + ";\n")


def ver(pasta):
    os.makedirs(pasta, exist_ok=True)
    ancoras = {}
    for n in PARAM:
        ancoras.update(json.load(open(os.path.join(RET, f"{n}_ancoras.json"))))
    for n in PARAM:
        chaves = sorted(k for k in ancoras if k.startswith(n + "_"))
        tiles = []
        for k in chaves:
            im, olhos = detectar(n, k, ancoras[k])
            v = Image.fromarray(im.astype(np.uint8), "RGBA")
            bg = Image.new("RGBA", v.size, (60, 150, 90, 255))
            bg.alpha_composite(v)
            px = np.asarray(bg).copy()
            for o in olhos:
                px[o["abertura"] & ~o["iris"]] = [255, 255, 0, 255]
                px[o["iris"]] = [255, 0, 255, 255]
                px[o["anel"]] = [0, 255, 255, 255]
            t = Image.fromarray(px).crop((0, 0, v.width, int(v.height * 0.55)))
            dr = ImageDraw.Draw(t)
            dr.text((4, 4), f"{k} olhos={len(olhos)}", fill=(255, 255, 255, 255))
            tiles.append(t)
        cols = 6
        cw = max(t.width for t in tiles)
        ch = max(t.height for t in tiles)
        rows = (len(tiles) + cols - 1) // cols
        out = Image.new("RGB", (cw * cols, ch * rows))
        for i, t in enumerate(tiles):
            out.paste(t.convert("RGB"), ((i % cols) * cw, (i // cols) * ch))
        out.save(os.path.join(pasta, f"deteccao_{n}.png"))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--ver":
        ver(sys.argv[2])
    else:
        main()
