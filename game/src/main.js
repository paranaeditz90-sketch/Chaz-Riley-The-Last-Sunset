import Phaser from "phaser";
import Abertura, { Cartela } from "./scenes/Abertura.js";
import Aviso from "./scenes/Aviso.js";
import Boot from "./scenes/Boot.js";
import Cozinha from "./scenes/Cozinha.js";
import Final, { Fluxo } from "./scenes/Final.js";
import Morro from "./scenes/Morro.js";
import Quarto from "./scenes/Quarto.js";
import Rua from "./scenes/Rua.js";
import Teste from "./scenes/Teste.js";
import Titulo from "./scenes/Titulo.js";
import Trigal from "./scenes/Trigal.js";

// as letras de mão dos bilhetes precisam estar carregadas antes do primeiro texto
const FONTES = ["Caveat Brush", "Patrick Hand", "Permanent Marker"];

function iniciar() {
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent: "game",
    backgroundColor: "#0d0b10",
    pixelArt: true,
    // EXPAND: altura fixa 1080 e a largura acompanha a tela (celular 20:9 sem faixa preta dos lados)
    scale: { mode: Phaser.Scale.EXPAND, autoCenter: Phaser.Scale.CENTER_BOTH, width: 1920, height: 1080 },
    input: { activePointers: 3 },
    scene: [Boot, Titulo, Aviso, Abertura, Cartela, Quarto, Rua, Morro, Trigal, Cozinha, Final, Fluxo, Teste],
  });
  window.__game = game; // usado nos testes automáticos
}

Promise.all(FONTES.map((f) => document.fonts.load(`40px "${f}"`)))
  .catch(() => {})
  .finally(iniciar);
