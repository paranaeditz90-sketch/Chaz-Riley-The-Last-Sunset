import Phaser from "phaser";
import { CenaJogo, NOMES, UI, irPara, tocarAmbiente, tocarMusica } from "../base.js";
import { CONVERSAS, CONVERSAS_NOITE } from "../dialogo.js";

// Campo de testes: os três soltos no trigal, pra testar andar, vida, conversa, escolha, esconder e a noite.

const MUNDO_W = 6400;
const MUNDO_H = 3200;

export default class Teste extends CenaJogo {
  constructor() {
    super("Teste");
  }

  config() {
    return {
      personagens: [
        { nome: "chaz", x: 3200, y: 1600 },
        { nome: "riley", x: 2960, y: 1650 },
        { nome: "nevoa", x: 3440, y: 1660 },
      ],
      mundo: { w: MUNDO_W, h: MUNDO_H },
      piso: "grama",
      luz: true,
    };
  }

  criarCenario() {
    const rnd = new Phaser.Math.RandomDataGenerator(["por-do-sol"]);
    this.chao = this.add.tileSprite(0, 0, MUNDO_W, MUNDO_H, "chao").setOrigin(0).setDepth(-1e6);
    this.trigos = [];
    const livre = [[2960, 1650], [3200, 1600], [3440, 1660]];
    for (let i = 0; i < 760; i++) {
      const x = rnd.between(40, MUNDO_W - 40);
      const y = rnd.between(120, MUNDO_H - 10);
      if (livre.some(([lx, ly]) => Math.hypot(lx - x, ly - y) < 320)) continue;
      this.trigos.push(this.add.image(x, y, "trigo").setOrigin(0.5, 1).setDepth(y).setFlipX(rnd.frac() < 0.5).setScale(rnd.realInRange(0.9, 1.25)));
    }
  }

  conversas() {
    return this.noite ? CONVERSAS_NOITE : CONVERSAS;
  }

  aoEntrar() {
    this.noite = false;
    tocarMusica(this, "musica_entardecer", 0.3);
    tocarAmbiente(this, "vento_loop", 0.2);
    this.criarHud();
    this.botao(120, 960, 70, "NOITE", () => this.alternarNoite());
    this.botao(300, 960, 70, "SAIR", () => irPara(this, "Titulo"));
    this.input.keyboard.on("keydown-N", () => this.alternarNoite());
    this.input.keyboard.on("keydown-ESC", () => irPara(this, "Titulo"));
  }

  aoTrocar(c) {
    this.hudNome.setText(NOMES[c.nome]);
  }

  aoAndar(c, nx) {
    this.balancarTrigo(c, nx);
  }

  alternarNoite() {
    this.noite = !this.noite;
    this.luz.ligarNoite(this.noite);
    const frio = 0x8a96c4; // luar: tira o dourado do chão e do trigo
    if (this.noite) {
      this.chao.setTint(frio);
      this.trigos.forEach((w) => w.setTint(frio));
      tocarMusica(this, "musica_noite", 0.34, 2400);
      tocarAmbiente(this, "grilos_loop", 0.22, 2000);
    } else {
      this.chao.clearTint();
      this.trigos.forEach((w) => w.clearTint());
      tocarMusica(this, "musica_entardecer", 0.3, 2400);
      tocarAmbiente(this, "vento_loop", 0.2, 2000);
    }
    this.hudNoite.setText(this.noite ? "Noite: a lanterna aponta pra onde você anda" : "");
  }

  // trigo balança quando alguém passa (e volta com mola)
  balancarTrigo(c, nx) {
    for (const w of this.trigos) {
      if (w.balancando) continue;
      const dx = w.x - c.s.x;
      const dy = w.y - c.s.y;
      if (Math.abs(dx) < 46 && dy > -26 && dy < 22) {
        w.balancando = true;
        this.som("folhas", 0.14, Phaser.Math.FloatBetween(0.9, 1.15), 350);
        const lado = Math.sign(dx || nx || 1);
        this.tweens.chain({
          targets: w,
          tweens: [
            { angle: lado * Phaser.Math.Between(10, 16), duration: 110, ease: "Sine.easeOut" },
            { angle: 0, duration: 900, ease: "Elastic.easeOut", easeParams: [1.2, 0.35] },
          ],
          onComplete: () => {
            w.balancando = false;
          },
        });
      }
    }
  }

  criarHud() {
    const toque = this.sys.game.device.input.touch;
    const estilo = { fontFamily: "Trebuchet MS, Verdana, sans-serif", color: "#fff3d6", stroke: "#000000" };
    this.hudNome = this.add.text(48, 36, NOMES[this.chars[this.ativo].nome], { ...estilo, fontSize: "64px", strokeThickness: 9 })
      .setScrollFactor(0).setDepth(UI);
    const dica = toque
      ? "Arraste à esquerda pra andar (até o fim = correr) · AÇÃO perto de alguém · segure ESCONDER"
      : "WASD/setas: andar · Shift: correr · E: falar · C: esconder · Tab/1/2/3: trocar · N: noite · Esc: sair";
    this.hudNoite = this.add.text(50, 170, "", { ...estilo, fontSize: "34px", strokeThickness: 6, color: "#cfd6ff" }).setScrollFactor(0).setDepth(UI);
    this.hud = [this.hudNome, this.add.text(50, 118, dica, { ...estilo, fontSize: "38px", strokeThickness: 7 }).setScrollFactor(0).setDepth(UI), this.hudNoite];
  }
}
