// Gera a versão "página única" do teste pra abrir no celular sem instalar nada:
// Phaser vem do cdnjs, o código do jogo vai embutido e os sprites vão como arquivos ao lado.
// Uso: node tools/build_artifact.mjs <pasta_saida>
import { readFileSync, writeFileSync, mkdirSync, copyFileSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
const saida = process.argv[2];
if (!saida) throw new Error("informe a pasta de saída");

const semModulo = (txt) =>
  txt
    .replace(/^import .*$/gm, "")
    .replace(/^export default class /m, "class ")
    .trim();
const cena = semModulo(readFileSync(join(raiz, "src/scenes/Teste.js"), "utf8"));
const main = semModulo(readFileSync(join(raiz, "src/main.js"), "utf8"));
if (/\bimport\b|\bexport\b/.test(cena + main)) throw new Error("sobrou import/export no código embutido");

const html = `<title>The Last Sunset</title>
<style>
  :root { color-scheme: dark; --fundo: #0d0b10; --texto: #fff3d6; }
  html, body { height: 100%; margin: 0; background: var(--fundo); color: var(--texto); overflow: hidden;
               touch-action: none; user-select: none; -webkit-user-select: none; }
  #game { position: fixed; inset: 0; }
  #girar { display: none; position: fixed; inset: 0; z-index: 9; align-items: center; justify-content: center;
           background: var(--fundo); color: var(--texto); font: 600 22px "Trebuchet MS", Verdana, sans-serif;
           text-align: center; padding: 16px; }
  @media (orientation: portrait) and (pointer: coarse) { #girar { display: flex; } }
</style>
<div id="game"></div>
<div id="girar">Vire o celular na horizontal ↻</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/phaser/3.90.0/phaser.min.js"></script>
<script>
(() => {
${cena}

${main}
})();
</script>
`;
mkdirSync(join(saida, "assets/sprites"), { recursive: true });
writeFileSync(join(saida, "index.html"), html);
const spr = join(raiz, "public/assets/sprites");
for (const f of readdirSync(spr)) copyFileSync(join(spr, f), join(saida, "assets/sprites", f));
console.log("ok", saida);
