"""Monta o jogo inteiro num .html só, em Python puro (sem npm, sem Vite, sem internet).

Serve pra continuar o projeto em qualquer lugar que rode Python (inclusive o ChatGPT):
edite os arquivos de game/src/ e rode este script. O resultado abre direto no navegador do celular.

- Phaser vem de game/vendor/phaser-3.90.0.min.js (licença MIT em game/vendor/PHASER_LICENSE.md).
- O código de game/src/ é juntado num script só (tira import/export; ordem em ORDEM).
- Sprites, sons e letras de mão vão em base64 dentro do arquivo.

Uso (da raiz do projeto):  python3 tools/montar_html.py saida.html
"""
import base64
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join(RAIZ, "game")
# ordem importa: quem é usado vem antes de quem usa
ORDEM = ["src/estado.js", "src/dialogo.js", "src/luz.js", "src/base.js", "src/scenes/Boot.js", "src/scenes/Titulo.js",
         "src/scenes/Aviso.js", "src/scenes/Abertura.js", "src/scenes/Quarto.js", "src/scenes/Teste.js", "src/main.js"]


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()


def sem_modulo(txt):
    txt = re.sub(r"^import .*?;\s*$", "", txt, flags=re.M)
    txt = re.sub(r"^export default class ", "class ", txt, flags=re.M)
    txt = re.sub(r"^export (const|let|class|function) ", r"\1 ", txt, flags=re.M)
    if re.search(r"^\s*(import|export)\b", txt, flags=re.M):
        raise SystemExit("sobrou import/export que este montador não entende")
    return txt.strip()


def main(saida):
    codigo = "\n\n".join(f"// ---- {p}\n" + sem_modulo(open(os.path.join(G, p), encoding="utf-8").read()) for p in ORDEM)
    phaser = open(os.path.join(G, "vendor", "phaser-3.90.0.min.js"), encoding="utf-8").read()

    spr = os.path.join(G, "public", "assets", "sprites")
    meta = json.load(open(os.path.join(spr, "sprites.json"), encoding="utf-8"))
    images = {n: "data:image/png;base64," + b64(os.path.join(spr, f"{n}.png")) for n in meta["characters"]}
    aud = os.path.join(G, "public", "assets", "audio")
    audio = {f[:-4]: "data:audio/mpeg;base64," + b64(os.path.join(aud, f)) for f in sorted(os.listdir(aud)) if f.endswith(".mp3")}

    cen = os.path.join(G, "public", "assets", "cenarios")
    imagens = {f[:-4]: "data:image/png;base64," + b64(os.path.join(cen, f)) for f in sorted(os.listdir(cen)) if f.endswith(".png")}

    html = open(os.path.join(G, "index.html"), encoding="utf-8").read()
    html = re.sub(r"url\(assets/fonts/([^)]+\.ttf)\)",
                  lambda m: f"url(data:font/ttf;base64,{b64(os.path.join(G, 'public', 'assets', 'fonts', m.group(1)))})", html)
    tag = re.search(r'<script type="module" src="[^"]+"></script>', html)
    if not tag:
        raise SystemExit("não achei o <script type=\"module\"> do index.html")
    seguro = lambda s: s.replace("</script", "<\\/script")
    embutido = (
        f"<script>{seguro(phaser)}</script>\n"
        f"<script>window.__SPRITES__ = {json.dumps({'meta': meta, 'images': images})};</script>\n"
        f"<script>window.__AUDIO__ = {json.dumps(audio)};</script>\n"
        f"<script>window.__IMAGENS__ = {json.dumps(imagens)};</script>\n"
        f"<script>\n(() => {{\n{seguro(codigo)}\n}})();\n</script>\n"
    )
    html = html.replace(tag.group(0), "")
    html = html.replace("</body>", embutido + "</body>")
    open(saida, "w", encoding="utf-8").write(html)
    print("ok", saida, f"{len(html.encode()) / 1e6:.1f} MB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "the_last_sunset.html")
