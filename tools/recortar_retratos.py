"""Recorta as folhas de expressões (arte em alta das cutscenes) em uma imagem por expressão, com fundo transparente.

Não redesenha nada: só tira o fundo e corta. Bordas suaves sem halo: na faixa de borda, o alfa sai da distância
até a cor do fundo e a cor é "despremultiplicada" (tira a mistura com o fundo).

Uso: python3 -P tools/recortar_retratos.py <folha> <nome> <linhas> <colunas> <pasta_saida>
     python3 -P tools/recortar_retratos.py --js <pasta_saida> game/src/retratos_dados.js
Saída: <pasta>/<nome>_<linha><coluna>.png (ex.: chaz_11.png) + <pasta>/<nome>_ancoras.json (pé, topo, centro).
"""
import json
import os
import sys
from collections import deque

import numpy as np
from PIL import Image
from scipy import ndimage


def fundo_e_alfa(path, tol=None, faixa=None):
    im = Image.open(path)
    if im.mode == "RGBA" and (np.asarray(im)[..., 3] < 10).mean() > 0.2:
        a = np.asarray(im).astype(np.float32)
        return a[..., :3], a[..., 3] / 255.0
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    H, W, _ = rgb.shape
    borda = np.concatenate([rgb[:6].reshape(-1, 3), rgb[-6:].reshape(-1, 3), rgb[:, :6].reshape(-1, 3), rgb[:, -6:].reshape(-1, 3)])
    bg = np.median(borda, 0)
    dist = np.sqrt(((rgb - bg) ** 2).sum(-1))
    claro = bg.mean() > 128
    tol = tol or (38 if claro else 16)
    faixa = faixa or (160 if claro else 38)
    # fundo = região parecida com o fundo, ligada à borda da imagem (o contorno preto fecha o personagem)
    perto = dist < tol
    lab, _ = ndimage.label(perto)
    ids = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fundo = np.isin(lab, list(ids))
    alfa = np.where(fundo, 0.0, 1.0)
    # faixa de borda (3 px pra dentro): alfa pela distância do fundo + cor sem a mistura
    perto_fundo = ndimage.binary_dilation(fundo, iterations=3) & ~fundo
    a = np.clip(dist / faixa, 0, 1)
    alfa[perto_fundo] = a[perto_fundo]
    cor = rgb.copy()
    m = perto_fundo & (alfa > 0.02)
    cor[m] = np.clip((rgb[m] - (1 - alfa[m, None]) * bg) / alfa[m, None], 0, 255)
    return cor, alfa


def main(path, nome, linhas, colunas, saida):
    """Cada personagem é o desenho inteiro dele (pedaço conectado grande), não uma coluna fixa: orelha larga
    passando da divisão não corta nem invade o vizinho. Pedaços pequenos (marcas "!", "?", lágrimas) vão pro
    personagem mais perto. Ordem: linhas por altura, depois esquerda → direita."""
    os.makedirs(saida, exist_ok=True)
    cor, alfa = fundo_e_alfa(path)
    lab, n = ndimage.label(alfa > 0.5)
    idx = np.arange(1, n + 1)
    tam = ndimage.sum(np.ones_like(alfa), lab, idx)
    grandes = [int(i) for i, t in zip(idx, tam) if t > tam.max() * 0.15]
    assert len(grandes) == linhas * colunas, f"{nome}: achei {len(grandes)} personagens, esperava {linhas * colunas}"
    centro = {i: ndimage.center_of_mass(lab == i) for i in grandes}
    caixas = ndimage.find_objects(lab)
    # pedaço pequeno -> personagem cuja caixa está mais perto (até 140 px)
    dono = {i: i for i in grandes}
    for i, t in zip(idx, tam):
        i = int(i)
        if i in dono or t < 15:
            continue
        sy, sx = caixas[i - 1]
        cy, cx = (sy.start + sy.stop) / 2, (sx.start + sx.stop) / 2
        melhor, dmin = None, 140
        for g in grandes:
            gy, gx = caixas[g - 1]
            dy = max(gy.start - cy, 0, cy - gy.stop)
            dx = max(gx.start - cx, 0, cx - gx.stop)
            d = (dx * dx + dy * dy) ** 0.5
            if d < dmin:
                melhor, dmin = g, d
        if melhor:
            dono[i] = melhor
    por_y = sorted(grandes, key=lambda g: centro[g][0])
    ordem = []
    for r in range(linhas):
        fila = por_y[r * colunas:(r + 1) * colunas]
        ordem += [(r, c, g) for c, g in enumerate(sorted(fila, key=lambda g: centro[g][1]))]
    ancoras = {}
    for r, c, g in ordem:
        pedacos = [i for i, d in dono.items() if d == g]
        manter = ndimage.binary_dilation(np.isin(lab, pedacos), iterations=3)
        a = np.where(manter, alfa, 0)
        yy, xx = np.nonzero(a > 0.02)
        by0, by1, bx0, bx1 = yy.min(), yy.max() + 1, xx.min(), xx.max() + 1
        rgba = np.zeros((by1 - by0, bx1 - bx0, 4), np.uint8)
        rgba[..., :3] = cor[by0:by1, bx0:bx1].round().astype(np.uint8)
        rgba[..., 3] = (a[by0:by1, bx0:bx1] * 255).round().astype(np.uint8)
        chave = f"{nome}_{r + 1}{c + 1}"
        Image.fromarray(rgba, "RGBA").save(os.path.join(saida, chave + ".png"), optimize=True)
        corpo = (lab == g)[by0:by1, bx0:bx1]
        cy, _ = np.nonzero(corpo)
        base = corpo[max(0, cy.max() - 40):cy.max() + 1]
        bxs = np.nonzero(base.any(0))[0]
        ancoras[chave] = {"w": int(bx1 - bx0), "h": int(by1 - by0), "pe": int(cy.max() + 1),
                          "cx": float((bxs.min() + bxs.max()) / 2), "topo": int(cy.min())}
    json.dump(ancoras, open(os.path.join(saida, f"{nome}_ancoras.json"), "w"), indent=1)
    print(nome, len(ancoras), "expressões")





def gerar_js(pasta, destino):
    """Junta as âncoras de todos os personagens num módulo JS (o jogo não busca arquivo nenhum na rede)."""
    tudo = {}
    for f in sorted(os.listdir(pasta)):
        if f.endswith("_ancoras.json"):
            tudo.update(json.load(open(os.path.join(pasta, f))))
    with open(destino, "w") as fh:
        fh.write("// Gerado por tools/recortar_retratos.py (--js). Não editar à mão.\n")
        fh.write("// Por expressão: w/h do recorte, pe = altura do pé, cx = centro do corpo no pé, topo = alto da cabeça.\n")
        fh.write("export const ANCORAS = " + json.dumps(tudo, indent=1) + ";\n")
    print("ok", destino, len(tudo))


if __name__ == "__main__":
    if sys.argv[1] == "--js":
        gerar_js(sys.argv[2], sys.argv[3])
    else:
        main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
