"""Arte provisória do capítulo 1 (feita por código, até chegar arte do diretor onde ele quiser).

A ameaça e os objetos que contam a história NÃO vão pra gerador de imagem (regra do roteiro): são feitos aqui.
Fundos de cinema seguem o jeito dos outros (formas simples + desfoque de lente + vinheta).
Objetos do jogo seguem o traço dos personagens: cor chapada, contorno preto grosso, desenhado em 4x e reduzido.

Uso: python3 -P tools/arte_cap1.py
Saída: game/public/assets/cinema/*.jpg e game/public/assets/cenarios/*.png
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CINE = os.path.join(RAIZ, "game", "public", "assets", "cinema")
CEN = os.path.join(RAIZ, "game", "public", "assets", "cenarios")
W, H = 2560, 1080
PRETO = (14, 10, 16, 255)


def vinheta(im, forca=0.5):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    m = 1 - forca * np.clip((d - 0.35) / 0.65, 0, 1) ** 1.6
    a = np.asarray(im.convert("RGB")).astype(np.float32) * m[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def degrade(cores, h=H, w=W):
    """céu em faixas suaves: cores de cima pra baixo"""
    ys = np.linspace(0, 1, h)
    pos = np.linspace(0, 1, len(cores))
    c = np.array(cores, np.float32)
    col = np.stack([np.interp(ys, pos, c[:, k]) for k in range(3)], -1)
    return Image.fromarray(np.repeat(col[:, None, :], w, 1).astype(np.uint8))


def morros(dr, base_y, amp, cor, fase, passo=40):
    pts = [(0, H)] + [(x, base_y + amp * np.sin(x / 300 + fase) + amp * 0.5 * np.sin(x / 113 + fase * 2)) for x in range(0, W + passo, passo)] + [(W, H)]
    dr.polygon(pts, fill=cor)


def trigo_faixa(im, y0, cor_a, cor_b, n=900, seed=3, alt=(30, 70)):
    """trigo no primeiro plano: muitos traços verticais com espiga"""
    rng = np.random.default_rng(seed)
    dr = ImageDraw.Draw(im)
    for _ in range(n):
        x = rng.uniform(0, W)
        y = rng.uniform(y0, H + 40)
        h = rng.uniform(*alt) * (0.6 + (y - y0) / (H - y0 + 1))
        c = cor_a if rng.random() < 0.5 else cor_b
        dr.line((x, y, x + rng.uniform(-6, 6), y - h), fill=c, width=4)
        dr.ellipse((x - 5, y - h - 16, x + 5, y - h + 4), fill=c)


# ------------------------------------------------------------------ morro (cinema)
def morro(noite=False):
    if not noite:
        # paleta do roteiro: prólogo laranja -> morro rosa/roxo
        ceu = [(92, 60, 128), (176, 92, 140), (236, 128, 120), (252, 176, 110)]
    else:
        ceu = [(6, 6, 14), (12, 12, 26), (20, 18, 34), (26, 22, 36)]
    im = degrade(ceu)
    dr = ImageDraw.Draw(im)
    longe = (120, 70, 120) if not noite else (14, 12, 22)
    meio = (88, 50, 92) if not noite else (10, 9, 16)
    morros(dr, H * 0.62, 26, longe, 0.4)
    # cidade lá embaixo, entre os morros (as luzes acendem/apagam no jogo, por cima)
    morros(dr, H * 0.70, 18, meio, 2.1)
    # trigal descendo
    trigal = (214, 150, 82) if not noite else (20, 18, 24)
    morros(dr, H * 0.78, 10, trigal, 4.0)
    trigo_faixa(im, H * 0.78, (196, 132, 66) if not noite else (26, 22, 30), (230, 172, 96) if not noite else (16, 14, 20))
    im = im.filter(ImageFilter.GaussianBlur(10))
    return vinheta(im, 0.45 if not noite else 0.7)


# ------------------------------------------------------------------ interiores escuros (cinema)
def pintar(formas, fundo):
    im = Image.new("RGB", (W, H), fundo)
    dr = ImageDraw.Draw(im)
    for tipo, cor, pts in formas:
        getattr(dr, {"ret": "rectangle", "poli": "polygon", "elipse": "ellipse"}[tipo])(pts, fill=cor)
    return im


def cozinha():
    # cozinha da casa da fazenda, sem luz: luar azul pela janela, porta da frente ABERTA (retângulo de noite lá fora)
    f = [("ret", (30, 24, 30), (0, H * 0.66, W, H)),  # chão de tábuas
         ("ret", (44, 34, 40), (0, 0, W, H * 0.66)),  # parede
         ("ret", (70, 84, 120), (W * 0.12, H * 0.16, W * 0.3, H * 0.46)),  # janela (luar)
         ("ret", (44, 34, 40), (W * 0.205, H * 0.16, W * 0.215, H * 0.46)),
         ("ret", (44, 34, 40), (W * 0.12, H * 0.305, W * 0.3, H * 0.315)),
         ("ret", (8, 8, 14), (W * 0.66, H * 0.1, W * 0.82, H * 0.66)),  # porta aberta: lá fora, breu
         ("ret", (54, 40, 40), (W * 0.82, H * 0.1, W * 0.86, H * 0.66)),  # folha da porta
         ("ret", (36, 26, 28), (W * 0.36, H * 0.5, W * 0.6, H * 0.56)),  # mesa
         ("ret", (36, 26, 28), (W * 0.38, H * 0.56, W * 0.39, H * 0.72)), ("ret", (36, 26, 28), (W * 0.57, H * 0.56, W * 0.58, H * 0.72)),
         ("poli", (70, 84, 120), [(W * 0.12, H * 0.66), (W * 0.3, H * 0.66), (W * 0.42, H), (W * 0.02, H)])]  # luar no chão
    im = pintar(f, (40, 30, 36))
    rng = np.random.default_rng(11)
    dr = ImageDraw.Draw(im)
    for _ in range(70):  # palha no chão
        x, y = rng.uniform(W * 0.2, W * 0.8), rng.uniform(H * 0.72, H)
        a = rng.uniform(0, np.pi)
        dr.line((x, y, x + 40 * np.cos(a), y + 12 * np.sin(a)), fill=(150, 118, 60), width=5)
    im = im.filter(ImageFilter.GaussianBlur(14))
    return vinheta(im, 0.7)


def quarto_amos():
    # quarto escuro: cama, uma silhueta deitada de costas pra câmera, um braço caído pra fora, mancha escura no
    # lençol e no chão. Sem gore: só forma, sombra e a cor escura. A janela dá a única luz.
    f = [("ret", (26, 20, 26), (0, 0, W, H)),
         ("ret", (60, 70, 104), (W * 0.62, H * 0.12, W * 0.78, H * 0.42)),  # janela
         ("ret", (20, 16, 22), (0, H * 0.7, W, H)),
         ("ret", (70, 64, 70), (W * 0.18, H * 0.52, W * 0.7, H * 0.7)),  # cama (lençol na luz fraca)
         ("ret", (40, 30, 30), (W * 0.16, H * 0.36, W * 0.2, H * 0.74)),  # cabeceira
         ("elipse", (16, 12, 16), (W * 0.24, H * 0.44, W * 0.52, H * 0.6)),  # silhueta deitada
         ("elipse", (16, 12, 16), (W * 0.22, H * 0.42, W * 0.3, H * 0.54)),  # cabeça
         ("poli", (16, 12, 16), [(W * 0.5, H * 0.56), (W * 0.53, H * 0.58), (W * 0.55, H * 0.86), (W * 0.52, H * 0.86)]),  # braço caído
         ("elipse", (52, 10, 16), (W * 0.36, H * 0.6, W * 0.6, H * 0.7)),  # mancha no lençol
         ("elipse", (44, 8, 14), (W * 0.48, H * 0.86, W * 0.66, H * 0.94))]  # poça no chão
    im = pintar(f, (26, 20, 26)).filter(ImageFilter.GaussianBlur(12))
    return vinheta(im, 0.75)


def fazenda(luz=False):
    # varanda da casa da fazenda de noite, vista do trigal: casa escura, porta, lâmpada da varanda
    ceu = [(6, 6, 14), (14, 14, 26)]
    im = degrade(ceu)
    dr = ImageDraw.Draw(im)
    parede = (34, 28, 34) if not luz else (120, 86, 56)
    dr.rectangle((W * 0.18, H * 0.18, W * 0.82, H * 0.72), fill=parede)
    dr.polygon([(W * 0.12, H * 0.2), (W * 0.5, H * 0.02), (W * 0.88, H * 0.2)], fill=(20, 16, 22) if not luz else (60, 40, 30))
    dr.rectangle((W * 0.44, H * 0.34, W * 0.56, H * 0.72), fill=(10, 8, 12))  # porta
    for x in (0.26, 0.66):
        dr.rectangle((W * x, H * 0.34, W * (x + 0.08), H * 0.5), fill=(12, 12, 20) if not luz else (230, 170, 90))
    dr.rectangle((0, H * 0.72, W, H), fill=(18, 16, 20) if not luz else (60, 46, 34))
    if luz:  # lâmpada da varanda: um poço de luz quente
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt((xx - W * 0.5) ** 2 + ((yy - H * 0.3) * 1.4) ** 2)
        g = np.clip(1 - d / 900, 0, 1) ** 2
        a = np.asarray(im).astype(np.float32)
        a = a * (0.55 + 0.45 * g[..., None]) + np.array([255, 190, 110]) * g[..., None] * 0.35
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    trigo_faixa(im, H * 0.8, (24, 22, 28) if not luz else (120, 90, 50), (14, 12, 18) if not luz else (90, 66, 40), n=700, seed=5)
    im = im.filter(ImageFilter.GaussianBlur(9))
    return vinheta(im, 0.7)


def janela_andy():
    # a janela do quarto do Andy, na casa do Chaz, de noite: moldura de madeira, vidro escuro, uma silhueta pequena
    # de criança olhando pra fora (pro trigal). A única coisa viva da imagem é o contorno dela no vidro.
    im = Image.new("RGB", (W, H), (22, 18, 26))
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, W, H), fill=(40, 34, 40))  # parede de madeira clara da casa branca, no escuro
    for i in range(0, H, 60):
        dr.line((0, i, W, i), fill=(34, 28, 34), width=6)
    dr.rectangle((W * 0.34, H * 0.14, W * 0.66, H * 0.86), fill=(24, 20, 24))  # moldura
    dr.rectangle((W * 0.36, H * 0.18, W * 0.64, H * 0.82), fill=(16, 18, 30))  # vidro
    # criança: cabeça redonda com orelhas caídas (cachorro, como o Chaz), ombros
    cx, cy = W * 0.5, H * 0.52
    dr.ellipse((cx - 110, cy - 120, cx + 110, cy + 90), fill=(8, 8, 12))
    dr.ellipse((cx - 170, cy - 70, cx - 70, cy + 110), fill=(8, 8, 12))
    dr.ellipse((cx + 70, cy - 70, cx + 170, cy + 110), fill=(8, 8, 12))
    dr.rectangle((cx - 150, cy + 80, cx + 150, H * 0.82), fill=(8, 8, 12))
    dr.rectangle((W * 0.495, H * 0.18, W * 0.505, H * 0.82), fill=(24, 20, 24))  # travessa do vidro (na frente)
    dr.rectangle((W * 0.36, H * 0.495, W * 0.64, H * 0.505), fill=(24, 20, 24))
    im = im.filter(ImageFilter.GaussianBlur(5))
    return vinheta(im, 0.65)


# ------------------------------------------------------------------ objetos do jogo (traço dos personagens)
S = 4


def desenho(w, h, f):
    """f(dr, s) desenha em 4x; devolve RGBA reduzido (borda suave)"""
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    f(ImageDraw.Draw(im), S)
    return im.resize((w, h), Image.LANCZOS)


def com_contorno(dr, tipo, pts, cor, t, s):
    """forma com contorno preto: desenha a forma inchada em preto e a forma por cima"""
    if tipo == "poli":
        dr.polygon([(x * s, y * s) for x, y in pts], fill=PRETO, outline=PRETO, width=int(t * 2 * s))
        dr.polygon([(x * s, y * s) for x, y in pts], fill=cor)
    elif tipo == "elipse":
        x0, y0, x1, y1 = pts
        dr.ellipse(((x0 - t) * s, (y0 - t) * s, (x1 + t) * s, (y1 + t) * s), fill=PRETO)
        dr.ellipse((x0 * s, y0 * s, x1 * s, y1 * s), fill=cor)
    elif tipo == "ret":
        x0, y0, x1, y1 = pts
        dr.rectangle(((x0 - t) * s, (y0 - t) * s, (x1 + t) * s, (y1 + t) * s), fill=PRETO)
        dr.rectangle((x0 * s, y0 * s, x1 * s, y1 * s), fill=cor)


def espantalho(w=300, h=480):
    """O espantalho (revisto pela crítica de animação: o primeiro era simétrico e fofo).
    Alto e torto: estaca inclinada, cabeça tombada pro lado, ombros caídos. Juta encardida, casaco cor de lama.
    Olhos = dois furos pretos desiguais, com um pontinho de brilho frio (o contrário dos olhos grandes dos
    personagens). Boca costurada comprida e torta. Palha escorrendo das mangas como dedos compridos.
    Margem larga no desenho: nada de palha cortada na borda."""
    def f(dr, s):
        t = 6
        madeira = (64, 50, 40, 255)
        # estaca inclinada (torta)
        com_contorno(dr, "poli", [(w * 0.50, h * 0.22), (w * 0.555, h * 0.22), (w * 0.53, h * 0.995), (w * 0.475, h * 0.995)], madeira, t, s)
        # travessa caída pra direita
        com_contorno(dr, "poli", [(w * 0.10, h * 0.33), (w * 0.92, h * 0.38), (w * 0.92, h * 0.41), (w * 0.10, h * 0.36)], madeira, t, s)
        palha = (150, 124, 70, 255)
        palha_esc = (104, 84, 48, 255)
        # palha escorrendo das mangas: fios compridos, caídos, como dedos
        for lado, bx, by in ((-1, w * 0.13, h * 0.37), (1, w * 0.88, h * 0.42)):
            for k in range(7):
                comp = h * (0.10 + 0.035 * (k % 4))
                x1 = bx + lado * (k - 3) * 4
                pts = [(bx * s, by * s), ((bx + x1) / 2 * s + lado * 6 * s, (by + comp * 0.5) * s), (x1 * s, (by + comp) * s)]
                dr.line(pts, fill=PRETO, width=int(7 * s), joint="curve")
                dr.line(pts, fill=palha if k % 2 else palha_esc, width=int(3 * s), joint="curve")
        # casaco cor de lama, comprido e rasgado embaixo, ombros caídos
        casaco = (62, 56, 48, 255)
        com_contorno(dr, "poli", [(w * 0.14, h * 0.34), (w * 0.88, h * 0.39), (w * 0.80, h * 0.47), (w * 0.74, h * 0.86), (w * 0.66, h * 0.80),
                                   (w * 0.58, h * 0.88), (w * 0.50, h * 0.81), (w * 0.42, h * 0.89), (w * 0.34, h * 0.82), (w * 0.27, h * 0.85),
                                   (w * 0.24, h * 0.45)], casaco, t, s)
        dr.line((w * 0.52 * s, h * 0.38 * s, w * 0.50 * s, h * 0.82 * s), fill=PRETO, width=int(3 * s))
        for x, y in ((0.35, 0.55), (0.64, 0.64), (0.42, 0.72)):  # remendos escuros
            dr.polygon([((w * x - 11) * s, (h * y - 8) * s), ((w * x + 12) * s, (h * y - 6) * s), ((w * x + 10) * s, (h * y + 9) * s), ((w * x - 9) * s, (h * y + 7) * s)],
                       fill=(44, 40, 36, 255), outline=PRETO, width=int(2 * s))
        for k in range(6):  # palha saindo da gola
            x = w * (0.40 + k * 0.045)
            dr.line((x * s, h * 0.36 * s, (x + (k - 2.5) * 5) * s, h * 0.45 * s), fill=palha_esc, width=int(3 * s))
        # cabeça: desenhada à parte e tombada ~16 graus
        cab = Image.new("RGBA", (int(w * 0.62 * s), int(h * 0.36 * s)), (0, 0, 0, 0))
        dc = ImageDraw.Draw(cab)
        cw, ch = cab.width / s, cab.height / s
        juta = (118, 104, 82, 255)
        com_contorno(dc, "elipse", (cw * 0.18, ch * 0.30, cw * 0.82, ch * 0.98), juta, t, s)
        for k in range(5):  # fiapos/manchas da juta encardida
            yk = ch * (0.45 + k * 0.1)
            dc.line((cw * 0.24 * s, yk * s, cw * 0.76 * s, (yk + 2) * s), fill=(98, 86, 68, 255), width=int(2 * s))
        # olhos: furos pretos desiguais, com pontinho de brilho frio
        for ex, ey, r in ((0.38, 0.56, 0.075), (0.62, 0.53, 0.06)):
            dc.ellipse(((cw * ex - cw * r) * s, (ch * ey - cw * r * 1.15) * s, (cw * ex + cw * r) * s, (ch * ey + cw * r * 1.15) * s), fill=(6, 4, 8, 255))
            dc.ellipse(((cw * ex - 2) * s, (ch * ey - 3) * s, (cw * ex + 1) * s, (ch * ey) * s), fill=(190, 210, 235, 255))
        # boca costurada comprida e torta
        pts = [(cw * (0.30 + i * 0.07), ch * (0.78 + (0.02 if i % 2 else -0.015) + i * 0.006)) for i in range(7)]
        dc.line([(x * s, y * s) for x, y in pts], fill=PRETO, width=int(3 * s))
        for x, y in pts[1:-1]:
            dc.line((x * s, (y - 7) * s, (x + 1) * s, (y + 7) * s), fill=PRETO, width=int(3 * s))
        # chapéu escuro e mole, aba rasgada caída de um lado
        chapeu = (58, 46, 34, 255)
        com_contorno(dc, "poli", [(cw * 0.04, ch * 0.36), (cw * 0.50, ch * 0.28), (cw * 0.96, ch * 0.30), (cw * 0.90, ch * 0.42),
                                   (cw * 0.62, ch * 0.38), (cw * 0.30, ch * 0.42), (cw * 0.10, ch * 0.50)], chapeu, t, s)
        com_contorno(dc, "poli", [(cw * 0.30, ch * 0.33), (cw * 0.36, ch * 0.06), (cw * 0.60, ch * 0.02), (cw * 0.70, ch * 0.31)], chapeu, t, s)
        cab = cab.rotate(-16, resample=Image.BICUBIC, expand=False)
        return cab

    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    cab = f(dr, S)
    im.alpha_composite(cab, (int(w * 0.22 * S), int(h * 0.02 * S)))
    return im.resize((w, h), Image.LANCZOS)


def fardo(w=200, h=130):
    def f(dr, s):
        palha = (210, 172, 92, 255)
        com_contorno(dr, "ret", (8, 16, w - 8, h - 8), palha, 5, s)
        for y in (0.35, 0.7):
            dr.line((8 * s, h * y * s, (w - 8) * s, h * y * s), fill=(150, 118, 60, 255), width=int(3 * s))
        for x in (0.3, 0.7):
            dr.line((w * x * s, 16 * s, w * x * s, (h - 8) * s), fill=PRETO, width=int(4 * s))  # cordas
        rng = np.random.default_rng(2)
        for _ in range(30):
            x, y = rng.uniform(14, w - 14), rng.uniform(20, h - 14)
            dr.line((x * s, y * s, (x + rng.uniform(-10, 10)) * s, (y + rng.uniform(-4, 4)) * s), fill=(176, 140, 70, 255), width=int(2 * s))
    return desenho(w, h, f)


def casa_fazenda(w=900, h=620):
    """a casa do Amos, de frente, vista de cima do trigal: madeira escura, varanda com lâmpada apagada, porta"""
    def f(dr, s):
        t = 6
        com_contorno(dr, "poli", [(40, 200), (w / 2, 30), (w - 40, 200)], (64, 46, 40, 255), t, s)  # telhado
        com_contorno(dr, "ret", (80, 200, w - 80, h - 90), (104, 80, 66, 255), t, s)  # parede
        for i in range(8):
            y = 220 + i * 38
            dr.line((86 * s, y * s, (w - 86) * s, y * s), fill=(84, 64, 54, 255), width=int(3 * s))
        com_contorno(dr, "ret", (w / 2 - 70, h - 330, w / 2 + 70, h - 90), (26, 20, 22, 255), t, s)  # porta
        for x in (170, w - 330):
            com_contorno(dr, "ret", (x, 260, x + 160, 380), (30, 32, 44, 255), t, s)  # janelas apagadas
            dr.line(((x + 80) * s, 260 * s, (x + 80) * s, 380 * s), fill=PRETO, width=int(4 * s))
        com_contorno(dr, "ret", (40, h - 100, w - 40, h - 70), (90, 68, 52, 255), t, s)  # assoalho da varanda
        for x in (70, w / 2 - 160, w / 2 + 150, w - 80):
            com_contorno(dr, "ret", (x - 8, h - 300, x + 8, h - 100), (90, 68, 52, 255), 4, s)  # pilares
        com_contorno(dr, "ret", (40, h - 310, w - 40, h - 296), (64, 46, 40, 255), t, s)  # beiral da varanda
        com_contorno(dr, "elipse", (w / 2 - 14, h - 296, w / 2 + 14, h - 268), (200, 196, 180, 255), 4, s)  # lâmpada
        for i in range(4):  # degraus
            com_contorno(dr, "ret", (w / 2 - 110 + i * 6, h - 70 + i * 16, w / 2 + 110 - i * 6, h - 56 + i * 16), (84, 62, 48, 255), 3, s)
    return desenho(w, h, f)


def gerador(w=230, h=170):
    """gerador a gasolina de fazenda: armação de cano, tanque vermelho em cima, motor cinza, rodinhas,
    escapamento e o puxador da cordinha (o primeiro parecia um rádio)"""
    def f(dr, s):
        t = 5
        cano = (40, 40, 44, 255)
        com_contorno(dr, "ret", (20, 40, w - 20, 48), cano, 3, s)  # armação
        com_contorno(dr, "ret", (20, 40, 28, h - 34), cano, 3, s)
        com_contorno(dr, "ret", (w - 28, 40, w - 20, h - 34), cano, 3, s)
        com_contorno(dr, "ret", (20, h - 42, w - 20, h - 34), cano, 3, s)
        com_contorno(dr, "ret", (40, 14, w - 60, 46), (170, 44, 34, 255), t, s)  # tanque
        com_contorno(dr, "elipse", (w - 92, 4, w - 72, 20), (60, 60, 64, 255), 3, s)  # tampa
        com_contorno(dr, "ret", (44, 60, w * 0.58, h - 46), (92, 94, 100, 255), t, s)  # motor
        for i in range(4):  # aletas
            dr.line((52 * s, (70 + i * 12) * s, (w * 0.58 - 8) * s, (70 + i * 12) * s), fill=PRETO, width=int(2 * s))
        com_contorno(dr, "elipse", (w * 0.62, 62, w * 0.62 + 46, 108), (70, 70, 76, 255), t, s)  # alternador
        com_contorno(dr, "ret", (w - 70, 104, w - 34, 118), (30, 30, 32, 255), 3, s)  # escapamento
        dr.line(((w * 0.58 + 4) * s, 80 * s, (w * 0.58 + 22) * s, 70 * s), fill=PRETO, width=int(4 * s))  # cordinha
        com_contorno(dr, "ret", (w * 0.58 + 20, 64, w * 0.58 + 34, 72), (200, 170, 60, 255), 2, s)
        for x in (52, w - 60):  # rodinhas
            com_contorno(dr, "elipse", (x - 16, h - 40, x + 16, h - 8), (28, 28, 30, 255), 4, s)
            dr.ellipse(((x - 5) * s, (h - 29) * s, (x + 5) * s, (h - 19) * s), fill=(120, 120, 126, 255))
    return desenho(w, h, f)


def main():
    os.makedirs(CINE, exist_ok=True)
    saidas = {
        "morro_tarde.jpg": morro(False), "morro_noite.jpg": morro(True), "cozinha.jpg": cozinha(),
        "quarto_amos.jpg": quarto_amos(), "fazenda_noite.jpg": fazenda(False), "fazenda_luz.jpg": fazenda(True),
        "janela_andy.jpg": janela_andy(),
    }
    for nome, im in saidas.items():
        im.save(os.path.join(CINE, nome), quality=84, optimize=True)
    for nome, im in {"espantalho.png": espantalho(), "fardo.png": fardo(), "casa_fazenda.png": casa_fazenda(), "gerador.png": gerador()}.items():
        im.save(os.path.join(CEN, nome), optimize=True)
    for d in (CINE, CEN):
        for f in sorted(os.listdir(d)):
            print(d[-8:], f, os.path.getsize(os.path.join(d, f)) // 1024, "KB")


if __name__ == "__main__":
    main()
