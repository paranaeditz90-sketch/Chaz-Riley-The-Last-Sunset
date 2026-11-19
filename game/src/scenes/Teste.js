import Phaser from "phaser";

// Cena de teste: os três personagens no jogo, andando/correndo nas 4 direções e trocando de ponto de vista.
// Cenário provisório (chão e trigo de mentira). Lanterna, luz e sombra entram na próxima etapa.

const NOMES = { chaz: "Chaz", riley: "Riley", nevoa: "Névoa" };
// mundo maior que qualquer tela: com a largura acompanhando a tela (EXPAND), 3600 sobrava faixa preta em tela muito larga
const MUNDO_W = 6400;
const MUNDO_H = 3200;
const VEL_ANDAR = 230;
const VEL_CORRER = 470;
const CAM_OFFSET_Y = 80; // câmera mira no corpo, não no pé
const UI = 1e7;

export default class Teste extends Phaser.Scene {
  constructor() {
    super("Teste");
  }

  preload() {
    // versão arquivo único (HTML): sprites e JSON já vêm embutidos na página, sem buscar arquivo nenhum
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
    this.meta = this.cache.json.get("sprites");
    this.criarChao();

    for (const [nome, c] of Object.entries(this.meta.characters)) {
      for (const [an, a] of Object.entries(c.anims)) {
        this.anims.create({
          key: `${nome}:${an}`,
          frames: this.anims.generateFrameNumbers(nome, { frames: a.frames }),
          frameRate: a.fps,
          repeat: a.repeat,
        });
      }
    }

    const inicio = { riley: [2960, 1650], chaz: [3200, 1600], nevoa: [3440, 1660] };
    this.chars = ["chaz", "riley", "nevoa"].map((nome) => {
      const [x, y] = inicio[nome];
      const s = this.add.sprite(x, y, nome).setOrigin(0.5, this.meta.originY);
      const c = { nome, s, facing: "frente", moving: false };
      this.parar(c);
      return c;
    });
    this.ativo = 0;
    this.trocando = false;

    const cam = this.cameras.main;
    cam.setBounds(0, 0, MUNDO_W, MUNDO_H);
    cam.setFollowOffset(0, CAM_OFFSET_Y);
    cam.startFollow(this.chars[0].s, true, 0.12, 0.12);

    this.keys = this.input.keyboard.addKeys("W,A,S,D,UP,DOWN,LEFT,RIGHT,SHIFT,TAB,ONE,TWO,THREE");
    this.input.keyboard.on("keydown-TAB", () => this.trocar((this.ativo + 1) % this.chars.length));
    this.input.keyboard.on("keydown-ONE", () => this.trocar(0));
    this.input.keyboard.on("keydown-TWO", () => this.trocar(1));
    this.input.keyboard.on("keydown-THREE", () => this.trocar(2));

    this.criarHud();
    this.criarToque();
  }

  // ---------------------------------------------------------------- personagens
  parar(c) {
    c.s.stop();
    c.s.setFrame(this.meta.characters[c.nome].anims[`${c.facing}_parado`].frames[0]);
  }

  direcao(c, nx, ny) {
    const ax = Math.abs(nx);
    const ay = Math.abs(ny);
    const horiz = ax >= ay;
    const nova = horiz ? (nx < 0 ? "esquerda" : "direita") : ny < 0 ? "costas" : "frente";
    // perto da diagonal, mantém a direção atual se ela ainda bate com o movimento (evita piscar entre poses)
    if (c.moving && Math.abs(ax - ay) < 0.15) {
      const ok = { esquerda: nx < 0, direita: nx > 0, costas: ny < 0, frente: ny > 0 }[c.facing];
      if (ok) return c.facing;
    }
    return nova;
  }

  trocar(i) {
    if (i === this.ativo || this.trocando || i >= this.chars.length) return;
    const antigo = this.chars[this.ativo];
    antigo.moving = false;
    this.parar(antigo);
    this.ativo = i;
    const c = this.chars[i];
    this.trocando = true;
    const cam = this.cameras.main;
    cam.stopFollow();
    cam.pan(c.s.x, c.s.y - CAM_OFFSET_Y, 450, "Sine.easeInOut", false, (_cam, p) => {
      if (p === 1) {
        cam.startFollow(c.s, true, 0.12, 0.12);
        this.trocando = false;
      }
    });
    this.hudNome.setText(NOMES[c.nome]);
  }

  update() {
    // tempo real do quadro (o delta suavizado do Phaser fica em 16 ms mesmo quando o aparelho cai pra 30 fps,
    // e o personagem andaria em câmera lenta); teto de 100 ms pra não teleportar depois de travada
    const dt = Math.min(this.game.loop.rawDelta, 100) / 1000;
    const k = this.keys;
    let vx = (k.D.isDown || k.RIGHT.isDown ? 1 : 0) - (k.A.isDown || k.LEFT.isDown ? 1 : 0);
    let vy = (k.S.isDown || k.DOWN.isDown ? 1 : 0) - (k.W.isDown || k.UP.isDown ? 1 : 0);
    let correr = k.SHIFT.isDown || this.correrSegurado;
    if (this.joy.ativo && this.joy.mag > 0.2) {
      vx = this.joy.vx;
      vy = this.joy.vy;
      if (this.joy.mag > 0.92) correr = true;
    }

    const c = this.chars[this.ativo];
    const len = Math.hypot(vx, vy);
    if (len > 0.01 && !this.trocando) {
      const nx = vx / len;
      const ny = vy / len;
      const v = correr ? VEL_CORRER : VEL_ANDAR;
      c.s.x = Phaser.Math.Clamp(c.s.x + nx * v * dt, 90, MUNDO_W - 90);
      c.s.y = Phaser.Math.Clamp(c.s.y + ny * v * dt, 220, MUNDO_H - 20);
      c.facing = this.direcao(c, nx, ny);
      c.moving = true;
      c.s.play(`${c.nome}:${c.facing}_${correr ? "correr" : "andar"}`, true);
    } else if (c.moving) {
      c.moving = false;
      this.parar(c);
    }

    for (const ch of this.chars) ch.s.setDepth(ch.s.y);
    this.desenharJoystick();
  }

  // ---------------------------------------------------------------- cenário provisório
  criarChao() {
    const rnd = new Phaser.Math.RandomDataGenerator(["por-do-sol"]);
    const g = this.make.graphics({ x: 0, y: 0 }, false);
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
    g.destroy();

    this.add.tileSprite(0, 0, MUNDO_W, MUNDO_H, "chao").setOrigin(0).setDepth(-1e6);
    const livre = [[2960, 1650], [3200, 1600], [3440, 1660]];
    for (let i = 0; i < 760; i++) {
      const x = rnd.between(40, MUNDO_W - 40);
      const y = rnd.between(120, MUNDO_H - 10);
      if (livre.some(([lx, ly]) => Math.hypot(lx - x, ly - y) < 320)) continue;
      this.add.image(x, y, "trigo").setOrigin(0.5, 1).setDepth(y).setFlipX(rnd.frac() < 0.5).setScale(rnd.realInRange(0.9, 1.25));
    }
  }

  // ---------------------------------------------------------------- HUD e toque
  criarHud() {
    const toque = this.sys.game.device.input.touch;
    const estilo = { fontFamily: "Trebuchet MS, Verdana, sans-serif", color: "#fff3d6", stroke: "#000000" };
    this.hudNome = this.add
      .text(48, 36, NOMES[this.chars[0].nome], { ...estilo, fontSize: "64px", strokeThickness: 9 })
      .setScrollFactor(0)
      .setDepth(UI);
    const dica = toque
      ? "Arraste do lado esquerdo pra andar (até o fim = correr) · TROCAR muda o personagem"
      : "WASD/setas: andar · Shift: correr · Tab ou 1/2/3: trocar de personagem";
    this.add.text(50, 118, dica, { ...estilo, fontSize: "38px", strokeThickness: 7 }).setScrollFactor(0).setDepth(UI);
  }

  // raio do joystick em pixels do jogo equivalente a ~60 px de tela, seja celular ou tablet
  raioJoy() {
    return Phaser.Math.Clamp(60 * this.scale.displayScale.x, 110, 240);
  }

  posicionarBotoes() {
    const W = this.scale.width;
    const H = this.scale.height;
    for (const b of this.botoes) {
      b.c.setPosition(W - b.dx, H - b.dy);
      b.t.setPosition(W - b.dx, H - b.dy);
    }
  }

  criarToque() {
    const toque = this.sys.game.device.input.touch;
    this.botoes = [];
    this.joy = { ativo: false, id: null, bx: 0, by: 0, vx: 0, vy: 0, mag: 0 };
    this.correrSegurado = false;
    this.joyG = this.add.graphics().setScrollFactor(0).setDepth(UI);

    const botao = (dx, dy, r, rotulo, aoApertar, aoSoltar) => {
      const c = this.add.circle(0, 0, r, 0xffffff, 0.12).setStrokeStyle(4, 0xffffff, 0.5).setScrollFactor(0).setDepth(UI);
      const t = this.add
        .text(0, 0, rotulo, { fontFamily: "Trebuchet MS, Verdana, sans-serif", fontSize: "36px", color: "#ffffff" })
        .setOrigin(0.5)
        .setScrollFactor(0)
        .setDepth(UI);
      c.setInteractive();
      c.on("pointerdown", () => {
        c.setFillStyle(0xffffff, 0.3);
        aoApertar?.();
      });
      const solta = () => {
        c.setFillStyle(0xffffff, 0.12);
        aoSoltar?.();
      };
      c.on("pointerup", solta);
      c.on("pointerout", solta);
      c.setVisible(toque);
      t.setVisible(toque);
      this.botoes.push({ c, t, dx, dy });
    };
    botao(190, 210, 120, "CORRER", () => (this.correrSegurado = true), () => (this.correrSegurado = false));
    botao(430, 130, 84, "TROCAR", () => this.trocar((this.ativo + 1) % this.chars.length));
    this.posicionarBotoes();
    this.scale.on("resize", () => this.posicionarBotoes());

    this.input.on("pointerdown", (p, sobre) => {
      if (sobre.length || this.joy.ativo || p.x > this.scale.width * 0.55) return;
      Object.assign(this.joy, { ativo: true, id: p.id, bx: p.x, by: p.y, vx: 0, vy: 0, mag: 0 });
    });
    this.input.on("pointermove", (p) => {
      if (!this.joy.ativo || p.id !== this.joy.id) return;
      const dx = p.x - this.joy.bx;
      const dy = p.y - this.joy.by;
      const d = Math.hypot(dx, dy);
      const m = Math.min(1, d / this.raioJoy());
      this.joy.mag = m;
      if (d > 0) {
        this.joy.vx = (dx / d) * m;
        this.joy.vy = (dy / d) * m;
      }
    });
    const fim = (p) => {
      if (this.joy.ativo && p.id === this.joy.id) Object.assign(this.joy, { ativo: false, vx: 0, vy: 0, mag: 0 });
    };
    this.input.on("pointerup", fim);
    this.input.on("pointerupoutside", fim);
  }

  desenharJoystick() {
    const g = this.joyG;
    g.clear();
    if (!this.joy.ativo) return;
    const R = this.raioJoy();
    g.fillStyle(0xffffff, 0.12).fillCircle(this.joy.bx, this.joy.by, R);
    g.lineStyle(4, 0xffffff, 0.4).strokeCircle(this.joy.bx, this.joy.by, R);
    g.fillStyle(0xffffff, 0.45).fillCircle(this.joy.bx + this.joy.vx * R, this.joy.by + this.joy.vy * R, R * 0.42);
  }
}
