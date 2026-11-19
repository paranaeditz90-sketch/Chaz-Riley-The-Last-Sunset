import Phaser from "phaser";
import { irPara } from "../base.js";

// Aviso de conteúdo (+18) e a promessa do jogo: ele se lembra das suas escolhas.

const LINHAS = [
  ["Este jogo é para maiores de 18 anos.", 46, "#fff3d6"],
  ["Ele fala de violência e morte, luto e culpa, ideação suicida,", 34, "#d9cdb8"],
  ["abuso, medo e paranoia. Nada disso está aqui por acaso.", 34, "#d9cdb8"],
  ["Se você estiver passando por algo parecido, fale com alguém. No Brasil: CVV, ligue 188.", 28, "#9f9486"],
];

export default class Aviso extends Phaser.Scene {
  constructor() {
    super("Aviso");
  }

  create() {
    const W = this.scale.width;
    const H = this.scale.height;
    this.cameras.main.setBackgroundColor("#000000");
    this.cameras.main.fadeIn(800, 0, 0, 0);
    let y = H * 0.3;
    LINHAS.forEach(([t, tam, cor], i) => {
      const txt = this.add.text(W / 2, y, t, { fontFamily: "Trebuchet MS, Verdana, sans-serif", fontSize: `${tam}px`, color: cor, align: "center", wordWrap: { width: W * 0.85 } })
        .setOrigin(0.5).setAlpha(0);
      this.tweens.add({ targets: txt, alpha: 1, duration: 900, delay: 300 + i * 900 });
      y += tam * 1.9 + (i === 0 ? 30 : 0);
    });
    const promessa = this.add.text(W / 2, H * 0.72, "Este jogo se lembra das suas escolhas.", {
      fontFamily: '"Patrick Hand", sans-serif', fontSize: "62px", color: "#ffffff",
    }).setOrigin(0.5).setAlpha(0);
    this.tweens.add({ targets: promessa, alpha: 1, duration: 1400, delay: 300 + LINHAS.length * 900 + 600 });
    const toque = this.add.text(W / 2, H * 0.9, "toque pra continuar", { fontFamily: "Trebuchet MS, sans-serif", fontSize: "28px", color: "#6f675d" })
      .setOrigin(0.5).setAlpha(0);
    const pronto = 300 + LINHAS.length * 900 + 2200;
    this.tweens.add({ targets: toque, alpha: 1, duration: 800, delay: pronto });
    this.time.delayedCall(pronto, () => {
      const seguir = () => {
        if (this.saindo) return;
        this.saindo = true;
        irPara(this, "Abertura", {}, 1000);
      };
      this.input.once("pointerdown", seguir);
      this.input.keyboard.once("keydown", seguir);
    });
  }
}
