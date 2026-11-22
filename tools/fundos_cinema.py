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


def main():
    os.makedirs(SAIDA, exist_ok=True)
    src = Image.open(os.path.join(RAIZ, "pixel-art", "cenarios", "fonte", "quarto_chaz_chatgpt.png")).convert("RGB")
    quarto(src).save(os.path.join(SAIDA, "quarto.jpg"), quality=86, optimize=True)
    ceu(src).save(os.path.join(SAIDA, "ceu_tarde.jpg"), quality=86, optimize=True)
    for f in sorted(os.listdir(SAIDA)):
        print(f, os.path.getsize(os.path.join(SAIDA, f)) // 1024, "KB")


if __name__ == "__main__":
    main()
