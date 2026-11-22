// Gera o jogo como UM arquivo .html que abre direto no navegador do celular, sem internet:
// Phaser, código e sprites (em base64) vão todos dentro do arquivo.
// Uso: npm run build && node tools/build_html.mjs <saida.html>
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
const saida = process.argv[2];
if (!saida) throw new Error("informe o arquivo de saída");

const dist = join(raiz, "dist");
const js = readdirSync(join(dist, "assets")).filter((f) => f.endsWith(".js"));
if (js.length !== 1) throw new Error(`esperava 1 .js em dist/assets, achei ${js.length} (rode npm run build)`);
const codigo = readFileSync(join(dist, "assets", js[0]), "utf8").replace(/<\/script/gi, "<\\/script");

const spr = join(raiz, "public/assets/sprites");
const meta = JSON.parse(readFileSync(join(spr, "sprites.json"), "utf8"));
const images = {};
for (const nome of Object.keys(meta.characters)) {
  images[nome] = "data:image/png;base64," + readFileSync(join(spr, `${nome}.png`)).toString("base64");
}

// sons e letras de mão também vão dentro do arquivo
const aud = join(raiz, "public/assets/audio");
const audio = {};
for (const f of readdirSync(aud).filter((f) => f.endsWith(".mp3"))) {
  audio[f.replace(/\.mp3$/, "")] = "data:audio/mpeg;base64," + readFileSync(join(aud, f)).toString("base64");
}

const imagens = {};
for (const pasta of ["cenarios", "retratos", "cinema"]) {
  const d = join(raiz, "public/assets", pasta);
  for (const f of readdirSync(d)) {
    const m = f.match(/^(.*)\.(png|jpg)$/);
    if (!m) continue;
    const mime = m[2] === "png" ? "image/png" : "image/jpeg";
    imagens[`${pasta}/${m[1]}`] = `data:${mime};base64,` + readFileSync(join(d, f)).toString("base64");
  }
}

let html = readFileSync(join(dist, "index.html"), "utf8");
html = html.replace(/url\(assets\/fonts\/([^)]+\.ttf)\)/g, (_m, f) =>
  `url(data:font/ttf;base64,${readFileSync(join(raiz, "public/assets/fonts", f)).toString("base64")})`);
const tag = html.match(/<script type="module" crossorigin src="[^"]+"><\/script>/);
if (!tag) throw new Error("não achei a tag do script no dist/index.html");
html = html.replace(tag[0], "");
const embutido =
  `<script>window.__SPRITES__ = ${JSON.stringify({ meta, images })};</script>\n` +
  `<script>window.__AUDIO__ = ${JSON.stringify(audio)};</script>\n` +
  `<script>window.__IMAGENS__ = ${JSON.stringify(imagens)};</script>\n` +
  `<script type="module">\n${codigo}\n</script>\n`;
html = html.replace("</body>", () => embutido + "</body>");
writeFileSync(saida, html);
console.log("ok", saida, (Buffer.byteLength(html) / 1e6).toFixed(1) + " MB");
