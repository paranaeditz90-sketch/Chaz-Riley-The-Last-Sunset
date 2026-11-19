import Phaser from "phaser";
import { carregar } from "../estado.js";

// Carrega tudo uma vez só (sprites, sons, cenários), cria as animações e as texturas feitas por código.
// Na versão arquivo único (HTML), tudo já vem embutido na página: nada é buscado na rede.

export const AUDIO = [
  "batida_vidro_0", "batida_vidro_1", "batida_vidro_2", "cachorro_triste", "folhas", "grilos_loop",
  "musica_entardecer", "musica_noite", "papel_1", "papel_2", "papel_3",
  "passo_grama_0", "passo_grama_1", "passo_grama_2", "passo_grama_3", "passo_grama_4",
  "passo_madeira_0", "passo_madeira_1", "passo_madeira_2", "passo_madeira_3", "passo_madeira_4",
  "porta_abre", "vento_loop", "voz_andy_1", "voz_cavalier_1", "voz_chaz_1", "voz_chaz_2", "voz_chaz_3",
  "voz_nevoa_1", "voz_nevoa_2", "voz_riley_1", "voz_riley_2", "voz_riley_3",
];
export const CENARIOS = ["quarto"];

export default class Boot extends Phaser.Scene {
  constructor() {
    super("Boot");
  }

  preload() {
    const W = this.scale.width;
    const H = this.scale.height;
    const barra = this.add.rectangle(W / 2 - 300, H / 2, 0, 6, 0xfff3d6).setOrigin(0, 0.5);
    this.load.on("progress", (p) => (barra.width = 600 * p));

    const aud = window.__AUDIO__;
    for (const k of AUDIO) this.load.audio(k, aud ? aud[k] : `assets/audio/${k}.mp3`);
    const img = window.__IMAGENS__;
    for (const k of CENARIOS) this.load.image(`cenario_${k}`, img ? img[k] : `assets/cenarios/${k}.png`);

    const emb = window.__SPRITES__;
    if (emb) {
      this.cache.json.add("sprites", emb.meta);
      for (const nome of Object.keys(emb.meta.characters)) {
        this.load.spritesheet(nome, emb.images[nome], { frameWidth: emb.meta.frameWidth, frameHeight: emb.meta.frameHeight });
      }
      return;
    }
    this.load.json("sprites", "assets/sprites/sprites.json");
    this.load.once("filecomplete-json-sprites", (_key, _type, data) => {
      for (const [nome, c] of Object.entries(data.characters)) {
        this.load.spritesheet(nome, c.image, { frameWidth: data.frameWidth, frameHeight: data.frameHeight });
      }
    });
  }

  create() {
    carregar();
    const meta = this.cache.json.get("sprites");
    for (const [nome, c] of Object.entries(meta.characters)) {
      for (const [an, a] of Object.entries(c.anims)) {
        if (this.anims.exists(`${nome}:${an}`)) continue;
        this.anims.create({ key: `${nome}:${an}`, frames: this.anims.generateFrameNumbers(nome, { frames: a.frames }), frameRate: a.fps, repeat: a.repeat });
      }
    }
    // cenários pintados (IA) ficam suaves ao ampliar; personagens continuam nítidos
    for (const k of CENARIOS) this.textures.get(`cenario_${k}`).setFilter(Phaser.Textures.FilterMode.LINEAR);
    this.texturasDeCodigo();
    this.scene.start("Titulo");
  }

  texturasDeCodigo() {
    const g = this.make.graphics({ x: 0, y: 0 }, false);
    g.fillStyle(0xd8c08a);
    g.fillCircle(6, 6, 6);
    g.generateTexture("poeira", 12, 12);
    g.clear();
    // chão de terra e trigo provisórios (até chegarem os cenários do morro e do trigal)
    const rnd = new Phaser.Math.RandomDataGenerator(["por-do-sol"]);
    g.fillStyle(0x7a6233);
    g.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 260; i++) {
      g.fillStyle(rnd.pick([0x6a5329, 0x8b7139, 0x846a35, 0x5f4a24]));
      g.fillRect(rnd.between(0, 252), rnd.between(0, 242), 4, rnd.between(6, 14));
    }
    g.generateTexture("chao", 256, 256);
    g.clear();
    for (let i = 0; i < 7; i++) {
      const x = 8 + i * 6 + rnd.between(-2, 2);
      const h = rnd.between(56, 80);
      g.fillStyle(0x9c7a35);
      g.fillRect(x, 96 - h, 3, h);
      g.fillStyle(0xd9b25a);
      g.fillRect(x - 2, 96 - h - 14, 7, 18);
    }
    g.generateTexture("trigo", 64, 96);
    g.clear();
    // grão de filme (abertura)
    g.fillStyle(0x000000, 0);
    g.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 1400; i++) {
      g.fillStyle(rnd.frac() < 0.5 ? 0xffffff : 0x000000, rnd.realInRange(0.05, 0.25));
      g.fillRect(rnd.between(0, 255), rnd.between(0, 255), 2, 2);
    }
    g.generateTexture("grao", 256, 256);
    g.destroy();
  }
}
