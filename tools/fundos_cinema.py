"""Fundos das cutscenes ("cinema"), feitos a partir do cenário do quarto que o diretor gerou.

Não redesenha o cenário: é a própria imagem com desfoque de lente (como os fundos desfocados dos vídeos do Bruce),
cor quente de fim de tarde e vinheta. O céu visto pela janela usa as cores tiradas do vidro da própria imagem.

Uso: python3 -P tools/fundos_cinema.py   (da raiz do projeto)
Saída: game/public/assets/cinema/*.jpg (2560x1080: cobre de 16:9 a 21:9 sem esticar)
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "game", "public", "assets", "cinema")
W, H = 2560, 1080


def grade_quente(im, quente=(1.06, 0.97, 0.88), luz=1.0):
    a = np.asarray(im.convert("RGB")).astype(np.float32) * np.array(quente) * luz
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def vinheta(im, forca=0.5):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    m = 1 - forca * np.clip((d - 0.35) / 0.65, 0, 1) ** 1.6
    a = np.asarray(im).astype(np.float32) * m[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def quarto(src):
    # interior (chão, tapete, móveis, luz da janela): o que se vê atrás do Chaz quando a câmera está na janela
    crop = src.crop((260, 230, 1420, 730))  # ~2.3:1
    im = crop.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(24))
    return vinheta(grade_quente(im), 0.55)


def ceu(src):
    # céu de fim de tarde com as cores do vidro da janela + sol + morros longe (desfocados)
    a = np.asarray(src.convert("RGB")).astype(np.float32)
    vidro = a[70:250, 725:995]
    topo = np.median(vidro[:30].reshape(-1, 3), 0)
    meio = np.median(vidro[70:110].reshape(-1, 3), 0)
    sol = np.percentile(vidro.reshape(-1, 3), 99, axis=0)
    yy = np.linspace(0, 1, H)[:, None]
    grad = topo * (1 - yy) ** 1.4 + meio * (1 - (1 - yy) ** 1.4)
    img = np.repeat(grad[:, None, :], W, axis=1).reshape(H, W, 3)
    # brilho do sol baixo, à direita
    yy2, xx2 = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx2 - W * 0.68) ** 2 + (yy2 - H * 0.66) ** 2)
    halo = np.clip(1 - d / 700, 0, 1) ** 2
    img = img * (1 - halo[..., None] * 0.7) + sol * halo[..., None] * 0.7
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(im)
    dr.ellipse((W * 0.68 - 150, H * 0.66 - 150, W * 0.68 + 150, H * 0.66 + 150), fill=tuple(int(v) for v in sol))
    # morros e trigo longe (silhueta roxa, igual à da janela)
    base = tuple(int(v) for v in np.median(a[230:262, 730:990].reshape(-1, 3), 0) * 0.85)
    pts = [(0, H)] + [(x, H * 0.78 + 40 * np.sin(x / 260) + 25 * np.sin(x / 97)) for x in range(0, W + 40, 40)] + [(W, H)]
    dr.polygon(pts, fill=base)
    im = im.filter(ImageFilter.GaussianBlur(18))
    return vinheta(im, 0.4)


def pintar(formas, ceu=None):
    """Fundo provisório pintado por formas simples e muito desfocado (fica como lente fora de foco)."""
    im = Image.new("RGB", (W, H), ceu[0] if ceu else (40, 30, 40))
    dr = ImageDraw.Draw(im)
    if ceu:
        for i, c in enumerate(ceu):
            dr.rectangle((0, H * i / len(ceu), W, H * (i + 1) / len(ceu) + 2), fill=c)
    for tipo, cor, pts in formas:
        if tipo == "ret":
            dr.rectangle(pts, fill=cor)
        elif tipo == "poli":
            dr.polygon(pts, fill=cor)
        elif tipo == "elipse":
            dr.ellipse(pts, fill=cor)
    return im


def rua():
    # rua de cidadezinha no fim de tarde de outono: casas de madeira, árvores laranja, céu quente
    ceu = [(250, 196, 120), (246, 170, 98), (238, 140, 84), (226, 116, 76)]
    f = []
    rng = np.random.default_rng(7)
    for x0, w, h, cor, tel in [(80, 520, 420, (236, 226, 212), (120, 70, 60)), (700, 460, 360, (196, 120, 90), (90, 50, 50)),
                               (1280, 560, 460, (230, 222, 205), (110, 62, 58)), (1960, 480, 380, (170, 120, 150), (80, 50, 70))]:
        base = H * 0.74
        f.append(("ret", cor, (x0, base - h, x0 + w, base)))
        f.append(("poli", tel, [(x0 - 30, base - h), (x0 + w / 2, base - h - 150), (x0 + w + 30, base - h)]))
        for j in range(2):
            f.append(("ret", (255, 214, 140), (x0 + 70 + j * (w - 220), base - h + 90, x0 + 150 + j * (w - 220), base - h + 190)))
    for x in rng.uniform(0, W, 9):  # árvores de outono
        r = rng.uniform(150, 230)
        f.append(("ret", (70, 40, 30), (x - 14, H * 0.5, x + 14, H * 0.8)))
        f.append(("elipse", tuple(int(v) for v in rng.choice([(232, 120, 40), (214, 90, 34), (245, 160, 60)])), (x - r, H * 0.5 - r * 1.1, x + r, H * 0.5 + r * 0.4)))
    f.append(("ret", (150, 110, 80), (0, H * 0.74, W, H)))  # rua de terra
    f.append(("ret", (180, 140, 100), (0, H * 0.74, W, H * 0.8)))  # calçada
    for x in rng.uniform(0, W, 60):  # folhas no chão
        y = rng.uniform(H * 0.8, H)
        f.append(("elipse", (226, 110, 40), (x, y, x + 26, y + 14)))
    im = pintar(f, ceu).filter(ImageFilter.GaussianBlur(26))
    return vinheta(grade_quente(im), 0.5)


def varanda():
    # varanda de madeira na luz baixa: tábuas, balanço, porta de tela escura, trigo lá fora
    ceu = [(238, 150, 88), (226, 120, 76)]
    f = [("ret", (120, 78, 52), (0, 0, W, H * 0.62)),  # parede de madeira da casa
         ("ret", (28, 18, 22), (W * 0.06, H * 0.12, W * 0.24, H * 0.62)),  # porta de tela (escuro lá dentro)
         ("ret", (212, 160, 96), (W * 0.62, H * 0.16, W * 0.98, H * 0.5)),  # janela pro trigal
         ("ret", (226, 186, 110), (W * 0.62, H * 0.38, W * 0.98, H * 0.5)),
         ("ret", (96, 60, 40), (0, H * 0.62, W, H)),  # tábuas
         ("ret", (70, 44, 30), (W * 0.32, H * 0.36, W * 0.58, H * 0.4)),  # balanço
         ("ret", (70, 44, 30), (W * 0.33, H * 0.0, W * 0.335, H * 0.38)), ("ret", (70, 44, 30), (W * 0.565, H * 0.0, W * 0.57, H * 0.38))]
    for i in range(9):
        f.append(("ret", (84, 52, 36), (0, H * 0.62 + i * 50, W, H * 0.62 + i * 50 + 6)))
    im = pintar(f, ceu).filter(ImageFilter.GaussianBlur(24))
    return vinheta(grade_quente(im, (1.05, 0.96, 0.86)), 0.6)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    src = Image.open(os.path.join(RAIZ, "pixel-art", "cenarios", "fonte", "quarto_chaz_chatgpt.png")).convert("RGB")
    quarto(src).save(os.path.join(SAIDA, "quarto.jpg"), quality=86, optimize=True)
    ceu(src).save(os.path.join(SAIDA, "ceu_tarde.jpg"), quality=86, optimize=True)
    # provisórios (até chegar a arte do diretor): rua e varanda do Vô Tobias
    rua().save(os.path.join(SAIDA, "rua_tarde.jpg"), quality=84, optimize=True)
    varanda().save(os.path.join(SAIDA, "varanda.jpg"), quality=84, optimize=True)
    for f in sorted(os.listdir(SAIDA)):
        print(f, os.path.getsize(os.path.join(SAIDA, f)) // 1024, "KB")


if __name__ == "__main__":
    main()
