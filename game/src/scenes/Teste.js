import Phaser from "phaser";
import { CONVERSAS, CONVERSAS_NOITE, Dialogo } from "../dialogo.js";
import { Luz } from "../luz.js";

// Cena de teste: os três personagens no jogo, andando/correndo nas 4 direções e trocando de ponto de vista.
// Cenário provisório (chão e trigo de mentira). Lanterna, luz e sombra entram na próxima etapa.

const NOMES = { chaz: "Chaz", riley: "Riley", nevoa: "Névoa" };
// mundo maior que qualquer tela: com a largura acompanhando a tela (EXPAND), 3600 sobrava faixa preta em tela muito larga
const MUNDO_W = 6400;
const MUNDO_H = 3200;
// velocidade casada com o passo do sprite (andar: ~44 px por passo; correr: ~63), senão o pé "patina"
const VEL_ANDAR = 175;
const VEL_CORRER = 380;
const CAM_OFFSET_Y = 80; // câmera mira no corpo, não no pé
const UI = 1e7;
// sons carregados no teste (os arquivos saem de tools/montar_audio.py; créditos em game/CREDITOS.md)
const AUDIO = [
  "voz_chaz_1", "voz_chaz_2", "voz_chaz_3", "voz_riley_1", "voz_riley_2", "voz_riley_3", "voz_nevoa_1", "voz_nevoa_2",
  "papel_1", "papel_2", "papel_3", "passo_grama_0", "passo_grama_1", "passo_grama_2", "passo_grama_3", "passo_grama_4",
  "folhas", "vento_loop", "musica_entardecer", "musica_noite", "grilos_loop",
];

export default class Teste extends Phaser.Scene {
  constructor() {
    super("Teste");
  }

  preload() {
    // versão arquivo único (HTML): sprites e JSON já vêm embutidos na página, sem buscar arquivo nenhum
    const aud = window.__AUDIO__;
    for (const k of AUDIO) this.load.audio(k, aud ? aud[k] : `assets/audio/${k}.mp3`);
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
    for (const c of this.chars) this.agendarVida(c, 0);

    const pg = this.make.graphics({ x: 0, y: 0 }, false);
    pg.fillStyle(0xd8c08a);
    pg.fillCircle(6, 6, 6);
    pg.generateTexture("poeira", 12, 12);
    pg.destroy();
    this.poeira = this.add.particles(0, 0, "poeira", {
      lifespan: 420,
      speed: { min: 18, max: 55 },
      angle: { min: 200, max: 340 },
      scale: { start: 0.9, end: 0.1 },
      alpha: { start: 0.55, end: 0 },
      gravityY: -20,
      emitting: false,
    });

    const cam = this.cameras.main;
    cam.setBounds(0, 0, MUNDO_W, MUNDO_H);
    cam.setFollowOffset(0, CAM_OFFSET_Y);
    cam.startFollow(this.chars[0].s, true, 0.12, 0.12);

    this.keys = this.input.keyboard.addKeys("W,A,S,D,UP,DOWN,LEFT,RIGHT,SHIFT,TAB,ONE,TWO,THREE,C,E,SPACE");
    this.input.keyboard.on("keydown-TAB", () => this.trocar((this.ativo + 1) % this.chars.length));
    // 1/2/3: na escolha, escolhe; fora dela, troca de personagem
    ["ONE", "TWO", "THREE"].forEach((k, n) =>
      this.input.keyboard.on(`keydown-${k}`, () => (this.dialogo.ativo ? this.dialogo.tecla(n) : this.trocar(n))));

    this.criarHud();
    this.criarToque();
    this.dialogo = new Dialogo(this);
    this.criarSom();
    this.luz = new Luz(this, this.chars);
    this.noite = false;
    this.mov = { x: 0, y: 0 };
    this.input.keyboard.on("keydown-N", () => this.alternarNoite());
  }

  // ---------------------------------------------------------------- pôr do sol <-> noite (teste)
  alternarNoite() {
    this.noite = !this.noite;
    this.luz.ligarNoite(this.noite);
    const frio = 0x8a96c4; // luar: tira o dourado do chão e do trigo
    if (this.noite) {
      this.chao.setTint(frio);
      this.trigos.forEach((w) => w.setTint(frio));
    } else {
      this.chao.clearTint();
      this.trigos.forEach((w) => w.clearTint());
    }
    // troca de música e ambiente com cruzamento suave
    const sai = this.noite ? this.musica : this.musicaNoite;
    const entra = this.noite ? this.musicaNoite : this.musica;
    if (sai && entra) {
      this.tweens.add({ targets: sai, volume: 0, duration: 1800, onComplete: () => sai.pause() });
      if (entra.isPaused) entra.resume();
      else if (!entra.isPlaying) entra.play();
      entra.setVolume(0);
      this.tweens.add({ targets: entra, volume: this.noite ? 0.34 : 0.3, duration: 2400 });
      this.tweens.add({ targets: this.vento, volume: this.noite ? 0.1 : 0.2, duration: 1500 });
      if (this.noite) {
        if (!this.grilos.isPlaying) this.grilos.play();
        this.tweens.add({ targets: this.grilos, volume: 0.22, duration: 2000 });
      } else {
        this.tweens.add({ targets: this.grilos, volume: 0, duration: 1500 });
      }
    }
    this.hudNoite.setText(this.noite ? "Noite: a lanterna aponta pra onde você anda" : "");
  }

  // ---------------------------------------------------------------- som
  criarSom() {
    this.somEm = {};
    const comecar = () => {
      this.musica = this.sound.add("musica_entardecer", { loop: true, volume: 0.3 });
      this.musicaNoite = this.sound.add("musica_noite", { loop: true, volume: 0 });
      this.grilos = this.sound.add("grilos_loop", { loop: true, volume: 0 });
      this.vento = this.sound.add("vento_loop", { loop: true, volume: 0.2 });
      this.musica.play();
      this.vento.play();
    };
    if (this.sound.locked) this.sound.once("unlocked", comecar);
    else comecar();
    for (const c of this.chars) {
      // passo quando o pé encosta no chão (quadros 1 e 3 do ciclo de andar/correr)
      c.s.on("animationupdate", (anim, frame) => {
        if (c !== this.chars[this.ativo] || !/_(andar|correr)$/.test(anim.key)) return;
        if (frame.index === 1 || frame.index === 3) this.passo(anim.key.endsWith("correr"));
      });
    }
  }

  som(chave, vol, rate = 1, intervalo = 0) {
    const agora = this.time.now;
    if (intervalo && agora < (this.somEm[chave] || 0)) return;
    this.somEm[chave] = agora + intervalo;
    if (this.cache.audio.exists(chave)) this.sound.play(chave, { volume: vol, rate });
  }

  passo(correndo) {
    const k = `passo_grama_${Phaser.Math.Between(0, 4)}`;
    this.som(k, correndo ? 0.38 : 0.26, Phaser.Math.FloatBetween(0.9, 1.1));
  }

  // ---------------------------------------------------------------- conversa (bilhete + voz do bicho)
  conversar() {
    if (this.dialogo.ativo || this.trocando) return;
    const c = this.chars[this.ativo];
    let alvo = null;
    let melhor = 300;
    for (const o of this.chars) {
      if (o === c) continue;
      const d = Phaser.Math.Distance.Between(c.s.x, c.s.y, o.s.x, o.s.y);
      if (d < melhor) {
        melhor = d;
        alvo = o;
      }
    }
    if (!alvo) return;
    const falas = (this.noite ? CONVERSAS_NOITE : CONVERSAS)[`${c.nome}>${alvo.nome}`];
    this.parceiro = alvo;
    if (!falas) return;
    // um olha pro outro
    for (const [a, b] of [[c, alvo], [alvo, c]]) {
      a.moving = false;
      a.agachado = 0;
      a.extraAte = 0;
      a.facing = b.s.x < a.s.x ? "esquerda" : "direita";
      this.parar(a);
    }
    const cam = this.cameras.main;
    cam.stopFollow();
    cam.pan((c.s.x + alvo.s.x) / 2, (c.s.y + alvo.s.y) / 2 - CAM_OFFSET_Y - 40, 600, "Sine.easeInOut");
    this.hud.forEach((h) => h.setVisible(false));
    const atores = {};
    for (const o of this.chars) atores[o.nome] = o.s;
    this.dialogo.iniciar(falas, atores, () => {
      cam.pan(c.s.x, c.s.y - CAM_OFFSET_Y, 400, "Sine.easeInOut", false, (_c, p) => {
        if (p === 1) cam.startFollow(c.s, true, 0.12, 0.12);
      });
      this.hud.forEach((h) => h.setVisible(true));
      for (const o of this.chars) this.agendarVida(o, this.time.now);
    });
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
    if (i === this.ativo || this.trocando || i >= this.chars.length || (this.dialogo && this.dialogo.ativo)) return;
    const antigo = this.chars[this.ativo];
    antigo.moving = false;
    this.parar(antigo);
    this.agendarVida(antigo, this.time.now);
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
    this.luz.angulo = { frente: Math.PI / 2, costas: -Math.PI / 2, esquerda: Math.PI, direita: 0 }[c.facing];
  }

  update() {
    // tempo real do quadro (o delta suavizado do Phaser fica em 16 ms mesmo quando o aparelho cai pra 30 fps,
    // e o personagem andaria em câmera lenta); teto de 100 ms pra não teleportar depois de travada
    const dt = Math.min(this.game.loop.rawDelta, 100) / 1000;
    const agora = this.time.now;
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
    if (Phaser.Input.Keyboard.JustDown(k.E) || Phaser.Input.Keyboard.JustDown(k.SPACE)) {
      if (this.dialogo.ativo) this.dialogo.avancar();
      else this.conversar();
    }
    if (this.dialogo.ativo) {
      this.dialogo.update();
      if (c.moving) {
        c.moving = false;
        this.parar(c);
      }
      for (const ch of this.chars) {
        this.vida(ch, agora);
        ch.s.setDepth(ch.s.y);
      }
      // na conversa, a lanterna vira pra quem está falando com você
      const pa = this.parceiro;
      this.luz.update(c, pa ? pa.s.x - c.s.x : 0, pa ? pa.s.y - c.s.y : 0, dt);
      this.desenharJoystick();
      return;
    }
    const len = Math.hypot(vx, vy);
    const esconder = (k.C.isDown || this.esconderSegurado) && len <= 0.01 && !this.trocando;
    if (esconder) {
      this.agachar(c, agora);
    } else if (c.agachado) {
      c.agachado = 0;
      c.prendendo = false;
      this.parar(c);
      this.agendarVida(c, agora);
    }
    if (len > 0.01 && !this.trocando) {
      const nx = vx / len;
      const ny = vy / len;
      const v = correr ? VEL_CORRER : VEL_ANDAR;
      c.s.x = Phaser.Math.Clamp(c.s.x + nx * v * dt, 90, MUNDO_W - 90);
      c.s.y = Phaser.Math.Clamp(c.s.y + ny * v * dt, 220, MUNDO_H - 20);
      c.facing = this.direcao(c, nx, ny);
      c.moving = true;
      c.extraAte = 0;
      this.mov.x = nx;
      this.mov.y = ny;
      c.s.play(`${c.nome}:${c.facing}_${correr ? "correr" : "andar"}`, true);
      this.balancarTrigo(c, nx);
      if (correr && agora >= (c.poeiraEm || 0)) {
        this.poeira.setDepth(c.s.y - 1);
        this.poeira.explode(2, c.s.x - nx * 18, c.s.y - 4);
        c.poeiraEm = agora + 110;
      }
    } else if (c.moving) {
      c.moving = false;
      this.parar(c);
      this.agendarVida(c, agora);
    }

    for (const ch of this.chars) {
      this.vida(ch, agora);
      ch.s.setDepth(ch.s.y);
    }
    this.luz.update(c, c.moving ? this.mov.x : 0, c.moving ? this.mov.y : 0, dt);
    this.desenharJoystick();
  }

  // ---------------------------------------------------------------- vida: parado não é estátua
  // Usa o que existir no sprites.json: {direção}_piscar, frente_olhar_esq/dir, gesto.
  // Personagem sem esses quadros ainda (Riley, Névoa) só fica parado até a folha nova chegar.
  anim(c, nome) {
    return this.meta.characters[c.nome].anims[nome];
  }

  agendarVida(c, agora) {
    c.virarEm = agora + Phaser.Math.Between(4500, 7500);
    c.piscarEm = agora + Phaser.Math.Between(1800, 4800);
    c.olharEm = agora + Phaser.Math.Between(7000, 13000);
    c.gestoEm = agora + Phaser.Math.Between(12000, 20000);
    c.extraAte = 0;
  }

  vida(c, agora) {
    if (c.moving || c.agachado) return;
    if (c.extraAte) {
      if (agora < c.extraAte) return;
      c.extraAte = 0;
      this.parar(c);
    }
    const tocar = (nome, segurar) => {
      const a = this.anim(c, nome);
      c.s.play(`${c.nome}:${nome}`);
      c.extraAte = agora + (a.frames.length * 1000) / a.fps + segurar;
    };
    // parado de lado/de costas por um tempo, vira pra câmera (como gente esperando) e aí pisca, olha, etc.
    if (this.dialogo && this.dialogo.ativo) {
      if (agora >= c.piscarEm && c.facing === "frente" && this.anim(c, "frente_piscar")) {
        c.piscarEm = agora + Phaser.Math.Between(2200, 5200);
        return tocar("frente_piscar", 50);
      }
      return;
    }
    if (c.facing !== "frente" && agora >= c.virarEm) {
      c.facing = "frente";
      this.parar(c);
      c.piscarEm = agora + Phaser.Math.Between(600, 1500);
      return;
    }
    if (agora >= c.piscarEm) {
      // às vezes pisca duas vezes seguidas, como gente
      c.piscarEm = agora + (Math.random() < 0.2 ? 280 : Phaser.Math.Between(2200, 5200));
      if (this.anim(c, `${c.facing}_piscar`)) return tocar(`${c.facing}_piscar`, 50);
    }
    if (c.facing === "frente" && agora >= c.olharEm) {
      c.olharEm = agora + Phaser.Math.Between(8000, 14000);
      const lado = Math.random() < 0.5 ? "frente_olhar_esq" : "frente_olhar_dir";
      if (this.anim(c, lado)) return tocar(lado, Phaser.Math.Between(600, 1100));
    }
    if (agora >= c.gestoEm) {
      c.gestoEm = agora + Phaser.Math.Between(15000, 25000);
      if (this.anim(c, "gesto")) {
        c.facing = "frente";
        return tocar("gesto", 1400);
      }
    }
  }

  // esconder: agacha na direção em que está; segurando mais um pouco, tapa a boca (prende a respiração)
  agachar(c, agora) {
    const pose = (base) => [`${base}_${c.facing}`, `${base}_esquerda`].find((n) => this.anim(c, n));
    if (!c.agachado) {
      c.agachado = agora;
      c.moving = false;
      const a = pose("agachar");
      if (a) c.s.setFrame(this.anim(c, a).frames[0]);
      return;
    }
    if (agora - c.agachado > 900 && !c.prendendo) {
      const t = pose("tapar");
      if (t) c.s.setFrame(this.anim(c, t).frames[0]);
      c.prendendo = true;
    }
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

    this.chao = this.add.tileSprite(0, 0, MUNDO_W, MUNDO_H, "chao").setOrigin(0).setDepth(-1e6);
    this.trigos = [];
    const livre = [[2960, 1650], [3200, 1600], [3440, 1660]];
    for (let i = 0; i < 760; i++) {
      const x = rnd.between(40, MUNDO_W - 40);
      const y = rnd.between(120, MUNDO_H - 10);
      if (livre.some(([lx, ly]) => Math.hypot(lx - x, ly - y) < 320)) continue;
      const w = this.add.image(x, y, "trigo").setOrigin(0.5, 1).setDepth(y).setFlipX(rnd.frac() < 0.5).setScale(rnd.realInRange(0.9, 1.25));
      this.trigos.push(w);
    }
  }

  // ---------------------------------------------------------------- HUD e toque
  criarHud() {
    const toque = this.sys.game.device.input.touch;
    const estilo = { fontFamily: "Trebuchet MS, Verdana, sans-serif", color: "#fff3d6", stroke: "#000000" };
    this.hud = [];
    this.hudNome = this.add
      .text(48, 36, NOMES[this.chars[0].nome], { ...estilo, fontSize: "64px", strokeThickness: 9 })
      .setScrollFactor(0)
      .setDepth(UI);
    const dica = toque
      ? "Arraste à esquerda pra andar (até o fim = correr) · FALAR perto de alguém · segure ESCONDER"
      : "WASD/setas: andar · Shift: correr · E: falar · C: esconder · Tab/1/2/3: trocar · N: noite";
    this.hud.push(this.hudNome, this.add.text(50, 118, dica, { ...estilo, fontSize: "38px", strokeThickness: 7 }).setScrollFactor(0).setDepth(UI));
    this.hudNoite = this.add.text(50, 170, "", { ...estilo, fontSize: "34px", strokeThickness: 6, color: "#cfd6ff" }).setScrollFactor(0).setDepth(UI);
    this.hud.push(this.hudNoite);
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
    this.esconderSegurado = false;
    this.joyG = this.add.graphics().setScrollFactor(0).setDepth(UI);

    const botao = (dx, dy, r, rotulo, aoApertar, aoSoltar) => {
      const c = this.add.circle(0, 0, r, 0xffffff, 0.12).setStrokeStyle(4, 0xffffff, 0.5).setScrollFactor(0).setDepth(UI);
      const t = this.add
        .text(0, 0, rotulo, { fontFamily: "Trebuchet MS, Verdana, sans-serif", fontSize: rotulo.length > 7 ? "28px" : "36px", color: "#ffffff" })
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
    botao(430, 330, 84, "ESCONDER", () => (this.esconderSegurado = true), () => (this.esconderSegurado = false));
    botao(660, 150, 84, "FALAR", () => (this.dialogo.ativo ? this.dialogo.avancar() : this.conversar()));
    botao(120, 960, 70, "NOITE", () => this.alternarNoite());
    this.posicionarBotoes();
    this.scale.on("resize", () => this.posicionarBotoes());

    this.input.on("pointerdown", (p, sobre) => {
      if (this.dialogo && this.dialogo.ativo && !sobre.length) return this.dialogo.avancar();
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
