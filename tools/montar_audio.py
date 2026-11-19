"""Monta os sons do jogo a partir das fontes baixadas (tools/baixar_audio.sh).

Só som com licença confirmada: CC0 (domínio público) ou CC BY 4.0 (com crédito). Ver game/CREDITOS.md.
Voz = som do bicho (decisão do diretor): cachorro late, gato mia. Cada personagem tem 2-3 variações; o jogo
ainda varia o tom um pouco a cada fala.

Uso: python3 -P tools/montar_audio.py <pasta_das_fontes>
"""
import os
import subprocess
import sys

import numpy as np

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game", "public", "assets", "audio")
SR = 44100


def load(rel, ch=1):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", os.path.join(SRC, rel), "-f", "f32le", "-ac", str(ch),
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).copy()
    assert len(a), rel
    return a if ch == 1 else a.reshape(-1, ch)


def trim(a, thr_db=-40, pad=0.01):
    """Corta silêncio do começo e do fim (envelope de 10 ms)."""
    env = np.sqrt(np.convolve(a * a, np.ones(441) / 441, "same"))
    on = np.nonzero(20 * np.log10(env + 1e-9) > thr_db + 20 * np.log10(env.max() + 1e-9))[0]
    i, j = max(0, on[0] - int(pad * SR)), min(len(a), on[-1] + int(pad * SR))
    return a[i:j]


def fades(a, fin=0.004, fout=0.03):
    a = a.copy()
    n1, n2 = int(fin * SR), int(fout * SR)
    a[:n1] *= np.linspace(0, 1, n1)
    a[-n2:] *= np.linspace(1, 0, n2)
    return a


def norm(a, peak=0.7):
    return a * (peak / (np.abs(a).max() + 1e-9))


def save(a, name, kbps=96, ch=1):
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, name + ".mp3")
    p = subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-f", "f32le", "-ac", str(ch), "-ar", str(SR), "-i", "-",
                        "-c:a", "libmp3lame", "-b:a", f"{kbps}k", dst], input=a.astype(np.float32).tobytes())
    assert p.returncode == 0, name
    return dst


def voz(rel, name, peak=0.7, ate=None):
    a = trim(load(rel))
    if ate:
        a = a[:int(ate * SR)]
    save(norm(fades(a), peak), name)


# ---- vozes (CC0)
DOG = "oga/dog-sounds/dog/Dog/"
voz(DOG + "Dog Bark 2.wav", "voz_chaz_1")
voz(DOG + "Dog Bark 3.wav", "voz_chaz_2")
voz(DOG + "Dog Bark.wav", "voz_chaz_3")
voz(DOG + "Dog Bark 1.wav", "voz_cavalier_1")
voz("oga/baby-animals-sounds-pack/baby-animals_0/Bark.ogg", "voz_andy_1")
voz("oga/dog-grunt/dog-frieda-grunt-96khz-01.flac", "voz_nevoa_1", peak=0.6)
voz(DOG + "Dog Bark 3.wav", "voz_nevoa_2", peak=0.45)      # o jogo toca mais grave e baixo: "wuf" de sono
voz("oga/meow/Meow.ogg", "voz_riley_1")
voz("oga/cat-purr-meow/cat_mewfood.wav", "voz_riley_2", ate=0.45)
voz("oga/cat-purr-meow/cat_softmew.wav", "voz_riley_3", ate=0.6)
voz(DOG + "Sad Dog.wav", "cachorro_triste", peak=0.5)

# ---- passos, papel do balão, folhas (CC0)
K = "kenney_impact-sounds/Audio/"
for i in range(5):
    save(norm(fades(trim(load(f"{K}footstep_grass_00{i}.ogg"), -45), 0.002, 0.02), 0.5), f"passo_grama_{i}", 64)
    save(norm(fades(trim(load(f"{K}footstep_wood_00{i}.ogg"), -45), 0.002, 0.02), 0.5), f"passo_madeira_{i}", 64)
R = "kenney_rpg-audio/Audio/"
for i in (1, 2, 3):
    save(norm(fades(trim(load(f"{R}bookFlip{i}.ogg"), -45), 0.002, 0.04), 0.45), f"papel_{i}", 64)
folhas = load("oga/random-sounds-samples/moving leaves stereo.ogg")
save(norm(fades(trim(folhas, -40), 0.01, 0.15), 0.4), "folhas", 64)

# ---- ambiente em loop (CC0): o fim cruza com o começo pra não dar "pulo"
def loop(rel, segundos, name, peak, cross=1.5):
    a = load(rel)
    L, F = int(segundos * SR), int(cross * SR)
    a = a[:L + F].copy()
    out = a[:L].copy()
    out[:F] = a[:F] * np.linspace(0, 1, F) + a[L:L + F] * np.linspace(1, 0, F)
    save(norm(out, peak), name, 64)


loop("oga/wind1/wind1.wav", 24, "vento_loop", 0.35)
loop("oga/crickets-ambient-noise-loopable/crickets_1.mp3", 10, "grilos_loop", 0.3, cross=1.0)

# ---- música (CC BY 4.0, Kevin MacLeod / incompetech.com)
def musica(rel, name, kbps=96):
    a = load(rel, ch=2)
    save(a.ravel(), name, kbps, ch=2)


musica("musica/Evening.mp3", "musica_entardecer")
print("ok", OUT, sorted(os.listdir(OUT)))
