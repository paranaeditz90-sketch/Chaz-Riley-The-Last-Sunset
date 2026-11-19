import Phaser from "phaser";
import Teste from "./scenes/Teste.js";

const game = new Phaser.Game({
  type: Phaser.AUTO,
  parent: "game",
  backgroundColor: "#0d0b10",
  pixelArt: true,
  // EXPAND: altura fixa 1080 e a largura acompanha a tela (celular 20:9 sem faixa preta dos lados)
  scale: { mode: Phaser.Scale.EXPAND, autoCenter: Phaser.Scale.CENTER_BOTH, width: 1920, height: 1080 },
  input: { activePointers: 3 },
  scene: [Teste],
});
window.__game = game; // usado nos testes automáticos
