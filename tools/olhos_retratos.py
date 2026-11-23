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
# pedido do diretor: nada de pontinho preto no olho. Só a pupila (mancha escura SOLTA no meio da íris) vira a
# cor da íris; o contorno escuro da íris encosta na borda dela e fica intacto (antes ele também era apagado e
# virava um risco tracejado — crítica de animação A-01/A-02/A-03).
# expressões em que a íris não anda (crítica de animação, seção 2):
#   tudo: a expressão É a direção do olhar (curiosidade, olhar de lado) ou o olho é pequeno/de perfil
#   susto (chaz_23) e tristeza (chaz_31): olhar fixo; a íris pequena de anel grosso andando deixava resto do anel
TRAVA = {"chaz_13": "tudo", "chaz_33": "tudo", "nevoa_12": "tudo", "nevoa_16": "tudo", "chaz_23": "tudo", "chaz_31": "tudo"}


def escorrer(img, alvo, fonte):
    """Preenche `alvo` com a média dos vizinhos já conhecidos, camada por camada a partir de `fonte`
    (uma difusão simples: o gradiente de sombra da esclera continua por dentro do buraco)."""
    img = img.copy()
    conhecido = fonte.copy()
    k = np.ones((3, 3))
    falta = alvo & ~conhecido
    for _ in range(200):
        if not falta.any():
            break
        soma = np.stack([ndimage.convolve(img[..., c] * conhecido, k, mode="nearest") for c in range(3)], -1)
        cont = ndimage.convolve(conhecido.astype(float), k, mode="nearest")
        borda = falta & (cont > 0)
        if not borda.any():
            break
        img[borda] = soma[borda] / cont[borda][:, None]
        conhecido |= borda
        falta &= ~borda
    # alisa um pouco o que foi preenchido (some o desenho de "camadas")
    for _ in range(3):
        suave = np.stack([ndimage.uniform_filter(img[..., c], 3) for c in range(3)], -1)
        img[alvo] = suave[alvo]
    return img.round()


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
        # íris inteira = íris + o contorno escuro em volta dela (o que não é esclera, perto da íris, dentro do olho).
        # Sem o contorno, ao mexer a íris sobrava um anel fantasma no lugar antigo.
        cbase = base[..., :3].astype(int)
        escl_px = np.abs(cbase - o["cor_escl"][None, None, :]).sum(-1) < 70
        # traço escuro: o que encosta no lado de fora da abertura é o contorno do OLHO; o que fica solto lá
        # dentro, perto da íris, é o contorno da ÍRIS (anda junto com ela; senão sobra um anel fantasma)
        # (pela distância à íris, não por ligação: o anel da íris às vezes encosta no contorno do olho)
        escuro_tudo = cbase.max(-1) < PARAM[nome]["contorno"] + 30
        lab_d, _ = ndimage.label(escuro_tudo)
        toca = set(np.unique(lab_d[~ndimage.binary_dilation(abc, iterations=1) & escuro_tudo])) - {0}
        solto = escuro_tudo & ~np.isin(lab_d, list(toca))  # traço escuro que não encosta no contorno do olho
        longe_borda = ndimage.distance_transform_edt(abc) > 2
        anel_iris = escuro_tudo & abc & ndimage.binary_dilation(irc, iterations=8) & (solto | longe_borda)
        contorno_olho = escuro_tudo & ~anel_iris
        perto = ndimage.binary_dilation(irc | anel_iris, iterations=2) & abc
        irc = ndimage.binary_fill_holes(irc | anel_iris | (perto & ~escl_px & ~contorno_olho)) & abc
        # miolo do olho = abertura sem o contorno preto do próprio olho (a abertura "fechada" invade um pouco a
        # linha). A esclera repintada e a íris movida ficam só no miolo: não mordem o contorno (A-02/A-04).
        miolo = abc & ~ndimage.binary_dilation(contorno_olho, iterations=1)
        # pixel quase branco na beirada da íris é emenda com a esclera/contorno, não brilho: não anda junto
        # (andando, virava pontinho branco em volta da íris)
        irc &= ~((cbase.min(-1) > 225) & ~ndimage.binary_erosion(irc, iterations=2))
        # olho sem íris (esclera no lugar): apaga com 2 px de folga pra não sobrar fiozinho da borda suavizada
        # faixa clara entre o miolo e o contorno (emenda suavizada): também é repintada, senão sobra íris velha
        # ou pontinho branco grudado no contorno
        faixa = abc & ~miolo & ~escuro_tudo
        sem = base.copy()
        apagar = ndimage.binary_dilation(irc, iterations=2) & (miolo | faixa)
        # repinta com a esclera em volta escorrendo pra dentro (mantém a sombra do desenho; a cor chapada
        # ficava um remendo claro, principalmente no Névoa)
        fonte = abc & ~apagar & escl_px & ~escuro_tudo
        sem[apagar, :3] = o["cor_escl"]
        if fonte.sum() > 20:
            sem[..., :3] = escorrer(sem[..., :3].astype(float), apagar, fonte)
        iy, ix = np.nonzero(irc)
        icx, icy = ix.mean(), iy.mean()
        rx = (ix.max() - ix.min() + 1) / 2
        ry = (iy.max() - iy.min() + 1) / 2
        ay, ax = np.nonzero(abc)
        ocx = (ax.min() + ax.max()) / 2
        # curso curto (55%): no olho grandão a íris ia até a borda e era cortada
        livre_x = max(0.0, (ax.max() - ax.min() + 1) / 2 - rx * 1.05) * 0.55
        livre_y = max(0.0, (ay.max() - ay.min() + 1) / 2 - ry * 1.05) * 0.5
        # íris cortada pela pálpebra (encosta no topo ou no fundo do olho): só mexe pros lados
        topo_ab = {c: np.nonzero(abc[:, c])[0].min() for c in np.unique(ix)}
        fundo_ab = {c: np.nonzero(abc[:, c])[0].max() for c in np.unique(ix)}
        encosta = any(iy[ix == c].min() <= topo_ab[c] + 2 or iy[ix == c].max() >= fundo_ab[c] - 2 for c in np.unique(ix))
        if encosta:
            livre_y = 0.0
        move = irc.sum() / max(1, abc.sum()) >= 0.2  # íris quase escondida (choro, sono pesado): não mexe
        # pupila: mancha escura que não encosta na borda da íris (o contorno da íris encosta e fica)
        limpo = base.copy()
        borda_iris = irc & ~ndimage.binary_erosion(irc, iterations=2)
        brilho_px = cbase.min(-1) > 225
        normal = irc & ~borda_iris & ~brilho_px
        if normal.sum() > 10:
            cor_iris = np.median(cbase[normal], 0)
            escuro = irc & (cbase.max(-1) < 0.62 * cor_iris.max())
            lab_e, n_e = ndimage.label(escuro)
            pupila = np.zeros_like(irc)
            for i in range(1, n_e + 1):
                m_e = lab_e == i
                if not (m_e & borda_iris).any():
                    pupila |= m_e
            if pupila.any():
                # 2 px de folga: a borda suavizada da pupila não pode sobrar como um "0" oco
                pupila = ndimage.binary_dilation(pupila, iterations=2) & irc & ~ndimage.binary_dilation(borda_iris, iterations=1)
                limpo[pupila, :3] = cor_iris
        # Névoa: olho amendoado, íris encostando nas duas pálpebras e esclera sombreada; mexendo a íris o remendo
        # aparecia (crítica A-03/A-06). O desenho dele já olha de lado/pra baixo (e ele quase não encara): fixo.
        trava = "tudo" if nome == "nevoa" else TRAVA.get(chave)
        mtop = np.array([np.nonzero(miolo[:, c])[0].min() if miolo[:, c].any() else -1 for c in range(miolo.shape[1])])
        mbot = np.array([np.nonzero(miolo[:, c])[0].max() if miolo[:, c].any() else -1 for c in range(miolo.shape[1])])
        # elipse da íris (só pra íris cortada pela pálpebra): ajustada na borda que aparece contra a esclera
        elipse, perto_iris = None, None
        if encosta and move and trava != "tudo":
            # largura vem das pontas da íris (os lados aparecem); altura e centro vertical, da borda que aparece
            # contra a esclera: y² = a·y + b·u + c, com u = 1 - ((x - cx)/rx)²  →  cy = a/2, ry = √b
            ecx = (ix.min() + ix.max()) / 2
            erx = rx
            livre_b = irc & ~ndimage.binary_erosion(irc) & ~ndimage.binary_dilation(~miolo, iterations=2)
            by, bx = np.nonzero(livre_b)
            u = 1 - ((bx - ecx) / erx) ** 2
            k = u > 0.05
            ecy, ery = icy, ry
            if k.sum() > 8:
                M = np.stack([by[k], u[k], np.ones(k.sum())], 1).astype(float)
                a_, b_, _ = np.linalg.lstsq(M, by[k].astype(float) ** 2, rcond=None)[0]
                if b_ > 0 and 0.5 * erx <= np.sqrt(b_) <= 2.0 * erx:
                    ecy, ery = a_ / 2, float(np.sqrt(b_))
            # a elipse tem de cobrir a íris original até a pálpebra (senão fica fresta de esclera embaixo do contorno)
            u2 = 1 - ((ix - ecx) / erx) ** 2
            k2 = u2 > 0.05
            if k2.any():
                ery = max(ery, float(np.percentile(np.abs(iy[k2] - ecy) / np.sqrt(u2[k2]), 98)) + 0.5)
            elipse = (ecx, ecy, erx, ery)
            nucleo = ndimage.binary_erosion(irc, iterations=3) & (cbase.min(-1) <= 225)
            cor_miolo = np.median(limpo[nucleo][:, :3], 0) if nucleo.sum() > 5 else np.median(limpo[irc][:, :3], 0)
        olhar = {}
        for nomeo, d in OLHARES.items():
            if d is None or not move or trava == "tudo":
                dx, dy = 0, 0
            else:
                dx = int(round(ocx + d[0] * livre_x - icx))
                dy = int(round(d[1] * livre_y))
                if trava == "vertical" or (trava == "cima" and dy < 0):
                    dy = 0
                # recua até a íris caber (no máximo 15% dela pra fora do olho)
                for _ in range(12):
                    ty, tx = iy + dy, ix + dx
                    ok = (ty >= 0) & (ty < abc.shape[0]) & (tx >= 0) & (tx < abc.shape[1])
                    fora = 1 - (miolo[ty[ok], tx[ok]].sum() / max(1, len(iy)))
                    # íris solta no meio do olho não pode encostar no contorno andando (sobrava fresta e pontinho)
                    if fora <= (0.15 if encosta else 0.0):
                        break
                    dx, dy = int(dx * 0.8), int(dy * 0.8)
            if dx == 0 and dy == 0:
                # íris no lugar original: o desenho original, só sem a pupila
                olhar[nomeo] = limpo.astype(np.uint8)
                continue
            img = sem.copy()
            if elipse is None:
                # íris solta no meio do olho: só muda de lugar (cabe inteira no miolo)
                ty, tx = iy + dy, ix + dx
                ok = (ty >= 0) & (ty < img.shape[0]) & (tx >= 0) & (tx < img.shape[1])
                ty, tx, sy, sx = ty[ok], tx[ok], iy[ok], ix[ok]
                dentro = miolo[ty, tx]
                img[ty[dentro], tx[dentro]] = limpo[sy[dentro], sx[dentro]]
            else:
                # íris cortada pela pálpebra: a parte escondida não existe no desenho. Ajusto uma elipse na borda
                # visível, ando com ela e recorto pelo miolo (a pálpebra corta a íris na curva certa). A cor vem
                # do pixel de íris mais perto na origem; borda suavizada por cobertura (4x4 amostras por pixel).
                ecx, ecy, erx, ery = elipse
                cob = np.zeros(miolo.shape)
                yy, xx = np.mgrid[0:miolo.shape[0], 0:miolo.shape[1]]
                for sy_ in np.arange(4):
                    for sx_ in np.arange(4):
                        X = xx + (sx_ + 0.5) / 4 - 0.5 - (ecx + dx)
                        Y = yy + (sy_ + 0.5) / 4 - 0.5 - (ecy + dy)
                        cob += ((X / erx) ** 2 + (Y / ery) ** 2 <= 1)
                alvo = miolo | faixa
                qy_raw, qx_raw = yy - dy, xx - dx
                okq = (qy_raw >= 0) & (qy_raw < miolo.shape[0]) & (qx_raw >= 0) & (qx_raw < miolo.shape[1])
                qy = np.clip(qy_raw, 0, miolo.shape[0] - 1)
                qx = np.clip(qx_raw, 0, miolo.shape[1] - 1)
                # 1) o que aparece no desenho anda igual, com a borda suavizada original
                da_iris = alvo & okq & irc[qy, qx]
                img[da_iris] = limpo[qy[da_iris], qx[da_iris]]
                # 2) a parte que estava escondida embaixo da pálpebra (origem acima do topo do olho naquela coluna)
                #    é preenchida com a cor da íris, recortada pela elipse com borda suavizada
                escondida = alvo & okq & ~da_iris & (mtop[qx] >= 0) & (qy < mtop[qx] + 1)
                c = (cob / 16) * escondida
                m = c > 0
                img[m, :3] = (cor_miolo[None, :] * c[m, None] + img[m, :3].astype(float) * (1 - c[m, None])).round()
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
        # olho em triângulo (o de trás, em três quartos): uma ponta bem mais alta que a outra virava "V".
        # Inclinação do arco limitada a 25% da largura.
        lim = 0.25 * (cmax - cmin)
        if abs(yR - yL) > lim:
            meio = (yL + yR) / 2
            sinal = np.sign(yR - yL)
            yL, yR = meio - sinal * lim / 2, meio + sinal * lim / 2
        reta = {c: yL + (yR - yL) * (c - cmin) / max(1, cmax - cmin) for c in validas}
        fundo_util = np.array([fundo[c] - reta[c] for c in validas])
        # curva rasa como a do desenho de olho fechado do diretor (olho pequeno e fundo virava "U"/"V")
        prof = min(max(2.0, float(np.percentile(fundo_util, 90)) * 0.8), 0.16 * (cmax - cmin))
        arco = {}
        for c in validas:
            u = (c - cmin) / max(1, cmax - cmin)
            arco[c] = reta[c] + prof * (1 - (2 * u - 1) ** 2)
        # fechado: o arco liso (no olho pequeno de trás da Riley, prender no fundo do olho fazia um "V"/gancho);
        # entreaberto: nunca abaixo do fundo do olho
        arco_aberto = {c: min(fundo[c], arco[c]) for c in validas}
        for t in ESTAGIOS:
            p = np.zeros_like(base)
            lid = np.full(len(cols), np.nan)
            alvo_arco = arco if t >= 1 else arco_aberto
            for c in validas:
                lid[c] = topo[c] + t * (max(alvo_arco[c], topo[c]) - topo[c])
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
