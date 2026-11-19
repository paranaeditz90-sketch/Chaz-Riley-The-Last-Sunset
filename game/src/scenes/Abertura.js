import Phaser from "phaser";
import { irPara, tocarAmbiente, tocarMusica } from "../base.js";
import { estado, marcar } from "../estado.js";
import { criarTexturas } from "../luz.js";

// Abertura fria: um pedaço de vídeo de celular, de noite, no trigal. Depois, o título e "Seis horas antes."
// (O que é esse vídeo fica pro roteiro.)

const INICIO = 31; // o trecho começa em 00:31
const FIM = 43; //    e corta em 00:43

export default class Abertura extends Phaser.Scene {
  constructor() {
    super("Abertura");
  }

  create() {
    criarTexturas(this);
    tocarMusica(this, null, 0, 300);
    tocarAmbiente(this, "grilos_loop", 0.22, 1500);
    this.vento = this.sound.add("vento_loop", { loop: true, volume: 0.1 });
    this.vento.play();

    // ---- o "vídeo": trigal à noite com um rastro de arrasto no chão
    const MW = 4000;
    const MH = 3200;
    this.add.tileSprite(0, 0, MW, MH, "chao").setOrigin(0).setTint(0x59607e);
    const rnd = new Phaser.Math.RandomDataGenerator(["abertura"]);
    this.caminho = new Phaser.Curves.CubicBezier(
      new Phaser.Math.Vector2(1500, 2900), new Phaser.Math.Vector2(1300, 2100),
      new Phaser.Math.Vector2(2300, 1500), new Phaser.Math.Vector2(2000, 500),
    );
    const marcas = this.add.graphics();
    const pts = this.caminho.getSpacedPoints(160);
    pts.forEach((p, i) => {
      if (i === 0) return;
      const q = pts[i - 1];
      marcas.lineStyle(rnd.between(10, 16), 0x1c1a24, 0.75);
      marcas.lineBetween(q.x + rnd.between(-4, 4), q.y, p.x + rnd.between(-4, 4), p.y);
      if (rnd.frac() < 0.6) {
        marcas.lineStyle(3, 0xc9a25a, 0.9); // fiapo de palha
        const a = rnd.realInRange(0, Math.PI);
        const x = p.x + rnd.between(-40, 40);
        const y = p.y + rnd.between(-20, 20);
        marcas.lineBetween(x, y, x + Math.cos(a) * 18, y + Math.sin(a) * 18);
      }
    });
    for (let i = 0; i < 900; i++) {
      const x = rnd.between(0, MW);
      const y = rnd.between(0, MH);
      const perto = pts.some((p) => Math.abs(p.x - x) < 70 && Math.abs(p.y - y) < 70);
      if (perto) continue;
      this.add.image(x, y, "trigo").setOrigin(0.5, 1).setTint(0x6d7397).setScale(rnd.realInRange(1, 1.5)).setDepth(y);
    }

    // ---- luz do celular apontando pro chão, tremendo na mão
    const { width: W, height: H } = this.scale;
    // breu maior que a tela: a câmera balança (gira) e não pode sobrar fresta clara nas bordas
    this.margem = 0.15;
    this.breu = this.add.renderTexture(-W * this.margem, -H * this.margem, W * (1 + 2 * this.margem), H * (1 + 2 * this.margem))
      .setOrigin(0).setScrollFactor(0).setDepth(1e6);
    this.halo = this.make.image({ key: "luz_halo", add: false }).setScale(2.3);

    // ---- interface de gravação
    const ui = (o) => o.setScrollFactor(0).setDepth(2e6);
    this.grao = ui(this.add.tileSprite(0, 0, W, H, "grao").setOrigin(0).setAlpha(0.5));
    const molduras = ui(this.add.graphics());
    molduras.lineStyle(6, 0xffffff, 0.85);
    const m = 60;
    const L = 70;
    for (const [x, y, sx, sy] of [[m, m, 1, 1], [W - m, m, -1, 1], [m, H - m, 1, -1], [W - m, H - m, -1, -1]]) {
      molduras.lineBetween(x, y, x + sx * L, y);
      molduras.lineBetween(x, y, x, y + sy * L);
    }
    this.rec = ui(this.add.text(m + 30, m + 24, "● REC", { fontFamily: "Trebuchet MS, sans-serif", fontSize: "44px", color: "#ff3b3b" }));
    this.tempo = ui(this.add.text(W - m - 30, m + 24, "00:31", { fontFamily: "Courier New, monospace", fontSize: "44px", color: "#ffffff" }).setOrigin(1, 0));
    ui(this.add.text(W - m - 30, H - m - 70, "▮▮▯", { fontFamily: "Trebuchet MS, sans-serif", fontSize: "34px", color: "#ffffff" }).setOrigin(1, 0));
    this.tweens.add({ targets: this.rec, alpha: 0.15, duration: 520, yoyo: true, repeat: -1 });
    this.flash = ui(this.add.rectangle(0, 0, W * 2, H * 2, 0xffffff).setOrigin(0).setAlpha(0).setDepth(3e6));

    this.cameras.main.setBounds(0, 0, MW, MH);
    this.t0 = this.time.now;
    this.cortou = false;
    this.proxPasso = 0;
    this.proxPalha = 0;

    if (estado.flags.viu_abertura) {
      const pular = () => this.irTitulo();
      this.input.once("pointerdown", pular);
      this.input.keyboard.once("keydown", pular);
    }
  }

  update(time) {
    if (this.cortou) return;
    const seg = (time - this.t0) / 1000;
    const total = FIM - INICIO;
    const t = Phaser.Math.Clamp(seg / total, 0, 1);
    const alvo = this.caminho.getPoint(t);
    const cam = this.cameras.main;
    // mão tremendo + passo
    const tremX = Math.sin(time / 170) * 10 + Math.sin(time / 53) * 4;
    const tremY = Math.cos(time / 210) * 8 + Math.abs(Math.sin(time / 300)) * 10;
    let subir = 0;
    if (seg > total - 0.8) subir = ((seg - (total - 0.8)) / 0.8) ** 2 * 900; // a câmera sobe de repente
    cam.centerOn(alvo.x + tremX, alvo.y + tremY - 120 - subir);
    cam.setRotation(Math.sin(time / 400) * 0.012);

    this.tempo.setText(`00:${String(Math.min(FIM, INICIO + Math.floor(seg))).padStart(2, "0")}`);
    this.grao.tilePositionX = Phaser.Math.Between(0, 256);
    this.grao.tilePositionY = Phaser.Math.Between(0, 256);

    // breu com a luz do celular
    this.breu.clear();
    this.breu.fill(0x020205, 0.985);
    const { width: W, height: H } = this.scale;
    this.halo.setPosition(W * (0.5 + this.margem) + tremX * 0.5, H * (0.58 + this.margem) + tremY * 0.5).setAlpha(0.95);
    this.breu.erase(this.halo);

    // som: passos lentos e algo pesado arrastando
    if (time > this.proxPasso) {
      this.proxPasso = time + 640;
      if (this.cache.audio.exists("passo_grama_0")) this.sound.play(`passo_grama_${Phaser.Math.Between(0, 4)}`, { volume: 0.32, rate: 0.85 });
    }
    if (time > this.proxPalha) {
      this.proxPalha = time + Phaser.Math.Between(900, 1400);
      if (this.cache.audio.exists("folhas")) this.sound.play("folhas", { volume: 0.34, rate: Phaser.Math.FloatBetween(0.45, 0.6) });
    }

    if (seg >= total) this.cortar();
  }

  // 00:43: clarão, corte seco, silêncio
  cortar() {
    this.cortou = true;
    this.flash.setAlpha(1);
    this.sound.stopAll();
    this.game.registry.set("faixaAmbiente", null);
    this.time.delayedCall(90, () => {
      this.cameras.main.setRotation(0);
      this.children.list.filter((o) => o !== this.flash).forEach((o) => o.setVisible(false));
      this.flash.setFillStyle(0x000000).setAlpha(1);
    });
    marcar("viu_abertura");
    this.time.delayedCall(1800, () => this.irTitulo());
  }

  irTitulo() {
    if (this.saindo) return;
    this.saindo = true;
    this.sound.stopAll();
    this.game.registry.set("faixaAmbiente", null);
    this.game.registry.set("faixaMusica", null);
    this.scene.start("Cartela", {
      textos: [
        { texto: "THE LAST SUNSET", fonte: "Permanent Marker", tam: 140, ms: 3200 },
        { texto: "Seis horas antes.", fonte: "Patrick Hand", tam: 64, ms: 2400 },
      ],
      depois: "Quarto",
    });
  }
}

// Cartela preta com texto (título, "Seis horas antes.", "Continua...")
export class Cartela extends Phaser.Scene {
  constructor() {
    super("Cartela");
  }

  create({ textos, depois }) {
    const { width: W, height: H } = this.scale;
    this.cameras.main.setBackgroundColor("#000000");
    let atraso = 400;
    textos.forEach(({ texto, fonte, tam, ms, cor }) => {
      const t = this.add.text(W / 2, H / 2, texto, { fontFamily: `"${fonte}", sans-serif`, fontSize: `${tam}px`, color: cor || "#fff3d6", align: "center", wordWrap: { width: W * 0.8 } })
        .setOrigin(0.5).setAlpha(0);
      this.tweens.add({ targets: t, alpha: 1, duration: 900, delay: atraso, hold: ms - 1800, yoyo: true });
      atraso += ms + 300;
    });
    this.time.delayedCall(atraso + 200, () => irPara(this, depois, {}, 300));
  }
}
