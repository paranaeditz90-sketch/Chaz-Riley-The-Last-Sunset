import Phaser from "phaser";
import { irPara, tocarAmbiente, tocarMusica } from "../base.js";
import { continuar, novoJogo, temSalvamento } from "../estado.js";

// Tela de título: o pôr do sol do morro, os três sentados de costas olhando o horizonte (como no fim do
// primeiro vídeo do Bruce), linhas de transmissão e trigo balançando.

export default class Titulo extends Phaser.Scene {
  constructor() {
    super("Titulo");
  }

  create() {
    this.saindo = false; // a cena é reaproveitada ao voltar pro título
    this.confirmandoNovo = false;
    this.desenhar();
    this.scale.on("resize", this.redesenhar, this);
    this.events.once("shutdown", () => this.scale.off("resize", this.redesenhar, this));
    tocarMusica(this, "musica_entardecer", 0.32, 2500);
    tocarAmbiente(this, "vento_loop", 0.16, 2500);
    this.cameras.main.fadeIn(900, 0, 0, 0);

    // Enter/E: ação principal (continuar se houver jogo salvo); N: novo jogo; T: campo de testes
    const k = this.input.keyboard;
    const principal = () => (temSalvamento() ? this.continuar() : this.comecar());
    k.on("keydown-ENTER", principal);
    k.on("keydown-E", principal);
    k.on("keydown-N", () => this.novo());
    k.on("keydown-T", () => this.teste());
  }

  redesenhar() {
    this.children.removeAll(true);
    this.tweens.killAll();
    this.desenhar();
  }

  desenhar() {
    const W = this.scale.width;
    const H = this.scale.height;
    const horiz = H * 0.62;
    // céu em faixas (sem degradê liso, igual à luz do jogo)
    const faixas = [0x2a1b3d, 0x4a2347, 0x7a2f4a, 0xb4463f, 0xe0703a, 0xf5a54a, 0xffd27a];
    const g = this.add.graphics();
    faixas.forEach((c, i) => {
      g.fillStyle(c);
      g.fillRect(0, (horiz * i) / faixas.length, W, horiz / faixas.length + 2);
    });
    // sol baixo, descendo devagar
    const sol = this.add.circle(W * 0.68, horiz - 30, 120, 0xfff0b0);
    this.add.circle(W * 0.68, horiz - 30, 170, 0xffe08a, 0.25);
    this.tweens.add({ targets: sol, y: horiz + 40, duration: 60000, ease: "Linear" });
    // morro e campo
    const m = this.add.graphics();
    m.fillStyle(0x24121f);
    m.fillPoints([
      new Phaser.Math.Vector2(0, H), new Phaser.Math.Vector2(0, horiz + 30), new Phaser.Math.Vector2(W * 0.25, horiz - 20),
      new Phaser.Math.Vector2(W * 0.5, horiz + 10), new Phaser.Math.Vector2(W * 0.8, horiz - 5), new Phaser.Math.Vector2(W, horiz + 25),
      new Phaser.Math.Vector2(W, H),
    ], true);
    // linhas de transmissão
    const torres = [W * 0.08, W * 0.38, W * 0.72, W * 1.02];
    m.lineStyle(6, 0x1a0c16);
    torres.forEach((x) => {
      m.lineBetween(x, horiz - 260, x, horiz + 10);
      m.lineBetween(x - 46, horiz - 230, x + 46, horiz - 230);
      m.lineBetween(x - 34, horiz - 190, x + 34, horiz - 190);
    });
    m.lineStyle(3, 0x1a0c16);
    for (let i = 0; i < torres.length - 1; i++) {
      for (const [dy, dx] of [[-230, -46], [-230, 46], [-190, 0]]) {
        const a = new Phaser.Curves.QuadraticBezier(
          new Phaser.Math.Vector2(torres[i] + dx, horiz + dy),
          new Phaser.Math.Vector2((torres[i] + torres[i + 1]) / 2, horiz + dy + 55),
          new Phaser.Math.Vector2(torres[i + 1] + dx, horiz + dy),
        );
        a.draw(m, 24);
      }
    }
    // trigo em silhueta, balançando
    const rnd = new Phaser.Math.RandomDataGenerator(["titulo"]);
    for (let i = 0; i < 90; i++) {
      const x = rnd.between(0, W);
      const y = rnd.between(horiz + 30, H);
      const t = this.add.image(x, y, "trigo").setOrigin(0.5, 1).setTint(0x1a0c16).setScale(rnd.realInRange(1, 1.8));
      this.tweens.add({ targets: t, angle: rnd.realInRange(3, 6), duration: rnd.between(1600, 2600), yoyo: true, repeat: -1, ease: "Sine.easeInOut", delay: rnd.between(0, 1500) });
    }
    // os três sentados de costas, olhando o horizonte
    const meta = this.cache.json.get("sprites");
    const lugares = [["riley", W * 0.45], ["chaz", W * 0.52], ["nevoa", W * 0.59]];
    for (const [nome, x] of lugares) {
      const a = meta.characters[nome].anims.sentado_costas || meta.characters[nome].anims.costas_parado;
      this.add.sprite(x, horiz + 130, nome, a.frames[0]).setOrigin(0.5, meta.originY).setTint(0x2b1626).setScale(0.9);
    }
    // título
    const tit = this.add.text(W / 2, H * 0.2, "THE LAST SUNSET", {
      fontFamily: '"Permanent Marker", sans-serif', fontSize: "132px", color: "#fff3d6", stroke: "#24121f", strokeThickness: 14,
    }).setOrigin(0.5).setAlpha(0);
    const sub = this.add.text(W / 2, H * 0.2 + 100, "CHAZ & RILEY", {
      fontFamily: '"Patrick Hand", sans-serif', fontSize: "56px", color: "#ffe6b0", stroke: "#24121f", strokeThickness: 8,
    }).setOrigin(0.5).setAlpha(0);
    this.tweens.add({ targets: [tit, sub], alpha: 1, duration: 2000, delay: 400 });

    // menu
    const botao = (y, texto, tam, acao) => {
      const t = this.add.text(W / 2, y, texto, {
        fontFamily: '"Patrick Hand", sans-serif', fontSize: `${tam}px`, color: "#fff3d6", stroke: "#24121f", strokeThickness: 8,
      }).setOrigin(0.5).setAlpha(0).setInteractive({ useHandCursor: true });
      t.on("pointerdown", acao);
      t.on("pointerover", () => t.setColor("#ffd27a"));
      t.on("pointerout", () => t.setColor("#fff3d6"));
      this.tweens.add({ targets: t, alpha: 1, duration: 1200, delay: 1600 });
      return t;
    };
    let principal;
    if (temSalvamento()) {
      principal = botao(H * 0.76, "CONTINUAR", 72, () => this.continuar());
      // novo jogo apaga as escolhas: pede um segundo toque pra confirmar
      this.botaoNovo = botao(H * 0.76 + 84, "novo jogo", 44, () => this.novo());
      botao(H * 0.76 + 150, "campo de testes", 36, () => this.teste());
    } else {
      principal = botao(H * 0.84, "COMEÇAR", 72, () => this.comecar());
      botao(H * 0.84 + 80, "campo de testes", 40, () => this.teste());
    }
    this.tweens.add({ targets: principal, scale: 1.06, duration: 900, yoyo: true, repeat: -1, ease: "Sine.easeInOut", delay: 2800 });
    this.add.text(W - 24, H - 18, "Chaz e Riley: personagens de Bruce Bronze", {
      fontFamily: "Trebuchet MS, sans-serif", fontSize: "24px", color: "#c9a9a6",
    }).setOrigin(1, 1);
  }

  comecar() {
    if (this.saindo) return;
    this.saindo = true;
    novoJogo(); // partida nova: escolhas e flags zeradas (o que vale entre partidas, como já ter visto a abertura, fica)
    tocarMusica(this, null, 0, 1200);
    tocarAmbiente(this, null, 0, 1200);
    irPara(this, "Aviso", {}, 1200);
  }

  novo() {
    if (this.saindo) return;
    if (!temSalvamento()) return this.comecar();
    if (!this.confirmandoNovo) {
      this.confirmandoNovo = true;
      this.botaoNovo?.setText("toque de novo: apaga suas escolhas").setColor("#ffb0a0");
      this.time.delayedCall(4000, () => {
        this.confirmandoNovo = false;
        if (this.botaoNovo?.active) this.botaoNovo.setText("novo jogo").setColor("#fff3d6");
      });
      return;
    }
    this.comecar();
  }

  continuar() {
    if (this.saindo) return;
    this.saindo = true;
    const cena = continuar();
    tocarMusica(this, null, 0, 1000);
    tocarAmbiente(this, null, 0, 1000);
    irPara(this, cena, {}, 1000);
  }

  teste() {
    if (this.saindo) return;
    this.saindo = true;
    irPara(this, "Teste", {}, 600);
  }
}
