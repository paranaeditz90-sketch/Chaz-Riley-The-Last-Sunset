import Phaser from "phaser";
import Abertura, { Cartela } from "./scenes/Abertura.js";
import Aviso from "./scenes/Aviso.js";
import Boot from "./scenes/Boot.js";
import Quarto from "./scenes/Quarto.js";
import Teste from "./scenes/Teste.js";
import Titulo from "./scenes/Titulo.js";

// as letras de mão dos bilhetes precisam estar carregadas antes do primeiro texto
const FONTES = ["Patrick Hand", "Permanent Marker", "Shadows Into Light", "Kalam"];

function iniciar() {
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent: "game",
    backgroundColor: "#0d0b10",
    pixelArt: true,
    // EXPAND: altura fixa 1080 e a largura acompanha a tela (celular 20:9 sem faixa preta dos lados)
    scale: { mode: Phaser.Scale.EXPAND, autoCenter: Phaser.Scale.CENTER_BOTH, width: 1920, height: 1080 },
    input: { activePointers: 3 },
    scene: [Boot, Titulo, Aviso, Abertura, Cartela, Quarto, Teste],
  });
  window.__game = game; // usado nos testes automáticos
}

Promise.all(FONTES.map((f) => document.fonts.load(`40px "${f}"`)))
  .catch(() => {})
  .finally(iniciar);
