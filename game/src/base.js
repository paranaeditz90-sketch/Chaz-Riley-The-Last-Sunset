import Phaser from "phaser";
import { Dialogo } from "./dialogo.js";
import { Luz } from "./luz.js";

// Base de toda cena jogável: personagens, andar/correr com colisão, vida (piscar, olhar, gesto), esconder,
// conversa em bilhete, objetos com que dá pra interagir, toque e teclado, som de passo, luz opcional.
// Cada cena (Quarto, Rua, Teste...) só diz o cenário, quem está nela e o que acontece.

export const NOMES = { chaz: "Chaz", riley: "Riley", nevoa: "Névoa" };
export const VEL_ANDAR = 175; // casado com o passo do sprite, senão o pé "patina"
export const VEL_CORRER = 380;
export const CAM_OFFSET_Y = 80;
export const UI = 1e7;

// ---------------------------------------------------------------- música e ambiente entre cenas (um de cada por vez)
export function tocarMusica(cena, chave, volume = 0.3, fade = 1500) {
  trocarFaixa(cena, "faixaMusica", chave, volume, fade);
}
export function tocarAmbiente(cena, chave, volume = 0.2, fade = 1500) {
  trocarFaixa(cena, "faixaAmbiente", chave, volume, fade);
}
function trocarFaixa(cena, slot, chave, volume, fade) {
  const reg = cena.game.registry;
  const atual = reg.get(slot);
  if (atual && atual.key === chave) {
    cena.tweens.add({ targets: atual, volume, duration: fade });
    return;
  }
  if (atual && !atual.pendingRemove) {
    cena.tweens.add({ targets: atual, volume: 0, duration: fade, onComplete: () => !atual.pendingRemove && atual.destroy() });
  }
  if (!chave || !cena.cache.audio.exists(chave)) {
    reg.set(slot, null);
    return;
  }
  const s = cena.sound.add(chave, { loop: true, volume: 0 });
  const tocar = () => {
    // pode ter sido trocada/apagada antes do som ser liberado pelo navegador
    if (s.pendingRemove || reg.get(slot) !== s) return;
    s.play();
    cena.tweens.add({ targets: s, volume, duration: fade });
  };
  if (cena.sound.locked) cena.sound.once("unlocked", tocar);
  else tocar();
  reg.set(slot, s);
}

// transição: escurece, troca de cena
export function irPara(cena, chave, dados = {}, ms = 600) {
  cena.cameras.main.fadeOut(ms, 0, 0, 0);
  cena.cameras.main.once("camerafadeoutcomplete", () => cena.scene.start(chave, dados));
}

export class CenaJogo extends Phaser.Scene {
  // ---- a cena filha define:
  // config(): { personagens: [{ nome, x, y, facing }], controla: [nomes], mundo: {w,h}, area: {x0,y0,x1,y1},
  //             obstaculos: [{x,y,w,h}], piso: "grama"|"madeira", luz: bool, cameraFixa: {x,y} | null }
  // criarCenario(), conversas() -> { "a>b": falas }, aoEntrar()
  config() {
    return {};
  }
  criarCenario() {}
  conversas() {
    return {};
  }
  aoEntrar() {}

  create() {
    this.cfg = Object.assign(
      { personagens: [], controla: null, mundo: { w: 1920, h: 1080 }, area: null, obstaculos: [], piso: "grama", luz: false, cameraFixa: null, esconder: true },
      this.config(),
    );
    this.meta = this.cache.json.get("sprites");
    this.interativos = [];
    this.travado = false;
    this.criarCenario();

    this.chars = this.cfg.personagens.map(({ nome, x, y, facing }) => {
      const s = this.add.sprite(x, y, nome).setOrigin(0.5, this.meta.originY);
      const c = { nome, s, facing: facing || "frente", moving: false };
      this.parar(c);
      this.agendarVida(c, 0);
      return c;
    });
    const controla = this.cfg.controla || this.chars.map((c) => c.nome);
    this.jogaveis = this.chars.filter((c) => controla.includes(c.nome));
    this.ativo = this.chars.indexOf(this.jogaveis[0]);
    this.trocando = false;

    this.poeira = this.add.particles(0, 0, "poeira", {
      lifespan: 420, speed: { min: 18, max: 55 }, angle: { min: 200, max: 340 },
      scale: { start: 0.9, end: 0.1 }, alpha: { start: 0.55, end: 0 }, gravityY: -20, emitting: false,
    });

    const cam = this.cameras.main;
    if (this.cfg.cameraFixa) {
      cam.centerOn(this.cfg.cameraFixa.x, this.cfg.cameraFixa.y);
    } else {
      cam.setBounds(0, 0, this.cfg.mundo.w, this.cfg.mundo.h);
      cam.setFollowOffset(0, CAM_OFFSET_Y);
      cam.startFollow(this.chars[this.ativo].s, true, 0.12, 0.12);
    }
    cam.fadeIn(600, 0, 0, 0);

    this.keys = this.input.keyboard.addKeys("W,A,S,D,UP,DOWN,LEFT,RIGHT,SHIFT,TAB,ONE,TWO,THREE,C,E,SPACE,ENTER");
    this.input.keyboard.on("keydown-TAB", () => this.proximoJogavel());
    ["ONE", "TWO", "THREE"].forEach((k, n) =>
      this.input.keyboard.on(`keydown-${k}`, () => {
        if (this.dialogo.ativo) return this.dialogo.tecla(n);
        const alvo = this.jogaveis[n];
        if (alvo) this.trocar(this.chars.indexOf(alvo));
      }));

    this.dialogo = new Dialogo(this);
    this.criarToque();
    this.luz = this.cfg.luz ? new Luz(this, this.chars) : null;
    this.mov = { x: 0, y: 0 };
    this.criarPassos();
    this.criarDestaque();
    this.aoEntrar();
  }

  // ---------------------------------------------------------------- som de passo (pé encosta: quadros 1 e 3)
  criarPassos() {
    this.somEm = {};
    for (const c of this.chars) {
      c.s.on("animationupdate", (anim, frame) => {
        if (c !== this.chars[this.ativo] || !/_(andar|correr)$/.test(anim.key)) return;
        if (frame.index === 1 || frame.index === 3) {
          const k = `passo_${this.cfg.piso}_${Phaser.Math.Between(0, 4)}`;
          this.som(k, anim.key.endsWith("correr") ? 0.38 : 0.26, Phaser.Math.FloatBetween(0.9, 1.1));
        }
      });
    }
  }

  som(chave, vol, rate = 1, intervalo = 0) {
    const agora = this.time.now;
    if (intervalo && agora < (this.somEm[chave] || 0)) return;
    this.somEm[chave] = agora + intervalo;
    if (this.cache.audio.exists(chave)) this.sound.play(chave, { volume: vol, rate });
  }

  // ---------------------------------------------------------------- roteiro: ajudantes com await
  // falas no formato do dialogo.js; atores extras (quem fala de fora da tela) em { nome: {x, y} }
  dizer(falas, atoresExtras = {}) {
    return new Promise((ok) => {
      const atores = { ...atoresExtras };
      for (const o of this.chars) atores[o.nome] = o.s;
      const c = this.chars[this.ativo];
      if (c.moving) {
        c.moving = false;
        this.parar(c);
      }
      this.dialogo.iniciar(falas, atores, () => {
        this.livreEm = this.time.now + 450;
        ok();
      });
    });
  }

  esperar(ms) {
    return new Promise((ok) => this.time.delayedCall(ms, ok));
  }

  // cutscene: anda sozinho até (x, y), com a animação certa; resolve quando chega
  andarAte(c, x, y, correr = false) {
    return new Promise((ok) => {
      const dx = x - c.s.x;
      const dy = y - c.s.y;
      const d = Math.hypot(dx, dy);
      if (d < 4) return ok();
      c.roteiro = true;
      c.extraAte = 0;
      c.moving = true;
      c.facing = this.direcao({ moving: false }, dx / d, dy / d);
      c.s.play(`${c.nome}:${c.facing}_${correr ? "correr" : "andar"}`, true);
      this.tweens.add({
        targets: c.s, x, y, duration: (d / (correr ? VEL_CORRER : VEL_ANDAR)) * 1000, ease: "Linear",
        onComplete: () => {
          c.roteiro = false;
          c.moving = false;
          this.parar(c);
          ok();
        },
      });
    });
  }

  virar(c, facing) {
    c.facing = facing;
    c.moving = false;
    this.parar(c);
  }

  olharPara(c, x) {
    c.facing = x < c.s.x ? "esquerda" : "direita";
    c.moving = false;
    this.parar(c);
  }

  // ---------------------------------------------------------------- objetos com que dá pra interagir
  // { id, x, y, raio, acao: async () => {}, ativo: () => bool }
  interativo(obj) {
    this.interativos.push(Object.assign({ raio: 150, ativo: () => true }, obj));
  }

  maisPerto() {
    const c = this.chars[this.ativo];
    let melhor = null;
    let dist = Infinity;
    for (const o of this.interativos) {
      if (!o.ativo()) continue;
      const d = Phaser.Math.Distance.Between(c.s.x, c.s.y - 60, o.x, o.y);
      if (d < o.raio && d < dist) {
        dist = d;
        melhor = o;
      }
    }
    return melhor;
  }

  criarDestaque() {
    // brilhinho em cima do que dá pra mexer (só quando você está perto)
    this.destaque = this.add.text(0, 0, "✦", { fontFamily: "Trebuchet MS, sans-serif", fontSize: "44px", color: "#fff6c8", stroke: "#000", strokeThickness: 6 })
      .setOrigin(0.5).setDepth(8.9e6).setVisible(false);
    this.tweens.add({ targets: this.destaque, scale: 1.25, alpha: 0.6, duration: 600, yoyo: true, repeat: -1 });
  }

  async acao() {
    if (this.dialogo.ativo) return this.dialogo.avancar();
    // respiro depois de uma fala: o mesmo toque que fechou o bilhete não puxa outra conversa
    if (this.travado || this.trocando || this.time.now < (this.livreEm || 0)) return;
    const o = this.maisPerto();
    if (o) {
      this.travado = true;
      this.destaque.setVisible(false);
      try {
        await o.acao();
      } finally {
        this.travado = false;
      }
      return;
    }
    this.conversar();
  }

  // ---------------------------------------------------------------- conversa com quem está perto
  conversar() {
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
    const falas = this.conversas()[`${c.nome}>${alvo.nome}`];
    if (!falas) return;
    this.parceiro = alvo;
    this.olharPara(c, alvo.s.x);
    this.olharPara(alvo, c.s.x);
    const cam = this.cameras.main;
    const seguia = !this.cfg.cameraFixa;
    if (seguia) {
      cam.stopFollow();
      cam.pan((c.s.x + alvo.s.x) / 2, (c.s.y + alvo.s.y) / 2 - CAM_OFFSET_Y - 40, 600, "Sine.easeInOut");
    }
    this.mostrarHud(false);
    this.dizer(falas).then(() => {
      if (seguia) {
        cam.pan(c.s.x, c.s.y - CAM_OFFSET_Y, 400, "Sine.easeInOut", false, (_c, p) => {
          if (p === 1) cam.startFollow(c.s, true, 0.12, 0.12);
        });
      }
      this.parceiro = null;
      this.mostrarHud(true);
      for (const o of this.chars) this.agendarVida(o, this.time.now);
    });
  }

  mostrarHud(v) {
    (this.hud || []).forEach((h) => h.setVisible(v));
  }

  // ---------------------------------------------------------------- personagens
  anim(c, nome) {
    return this.meta.characters[c.nome].anims[nome];
  }

  parar(c) {
    c.s.stop();
    c.s.setFrame(this.anim(c, `${c.facing}_parado`).frames[0]);
  }

  direcao(c, nx, ny) {
    const ax = Math.abs(nx);
    const ay = Math.abs(ny);
    const nova = ax >= ay ? (nx < 0 ? "esquerda" : "direita") : ny < 0 ? "costas" : "frente";
    if (c.moving && Math.abs(ax - ay) < 0.15) {
      const ok = { esquerda: nx < 0, direita: nx > 0, costas: ny < 0, frente: ny > 0 }[c.facing];
      if (ok) return c.facing;
    }
    return nova;
  }

  proximoJogavel() {
    if (this.jogaveis.length < 2) return;
    const k = this.jogaveis.indexOf(this.chars[this.ativo]);
    this.trocar(this.chars.indexOf(this.jogaveis[(k + 1) % this.jogaveis.length]));
  }

  trocar(i) {
    if (i === this.ativo || this.trocando || i < 0 || this.dialogo.ativo || this.travado) return;
    const antigo = this.chars[this.ativo];
    antigo.moving = false;
    this.parar(antigo);
    this.agendarVida(antigo, this.time.now);
    this.ativo = i;
    const c = this.chars[i];
    if (!this.cfg.cameraFixa) {
      this.trocando = true;
      const cam = this.cameras.main;
      cam.stopFollow();
      cam.pan(c.s.x, c.s.y - CAM_OFFSET_Y, 450, "Sine.easeInOut", false, (_cam, p) => {
        if (p === 1) {
          cam.startFollow(c.s, true, 0.12, 0.12);
          this.trocando = false;
        }
      });
    }
    if (this.luz) this.luz.angulo = { frente: Math.PI / 2, costas: -Math.PI / 2, esquerda: Math.PI, direita: 0 }[c.facing];
    this.aoTrocar(c);
  }

  aoTrocar() {}

  // pé livre? (dentro da área e fora dos obstáculos; o pé é um retângulo de 56x24)
  livre(x, y) {
    const a = this.cfg.area;
    if (a && (x < a.x0 || x > a.x1 || y < a.y0 || y > a.y1)) return false;
    if (!a && (x < 90 || x > this.cfg.mundo.w - 90 || y < 220 || y > this.cfg.mundo.h - 20)) return false;
    for (const o of this.cfg.obstaculos) {
      if (x + 28 > o.x && x - 28 < o.x + o.w && y > o.y && y - 24 < o.y + o.h) return false;
    }
    return true;
  }

  update() {
    // tempo real do quadro (o delta suavizado do Phaser fica em 16 ms mesmo a 30 fps); teto de 100 ms
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
    if (Phaser.Input.Keyboard.JustDown(k.E) || Phaser.Input.Keyboard.JustDown(k.SPACE) || Phaser.Input.Keyboard.JustDown(k.ENTER)) {
      this.acao();
    }
    const c = this.chars[this.ativo];
    const preso = this.dialogo.ativo || this.travado;
    if (preso) {
      this.dialogo.update();
      vx = vy = 0;
    }
    const len = Math.hypot(vx, vy);
    const esconder = this.cfg.esconder && !preso && (k.C.isDown || this.esconderSegurado) && len <= 0.01 && !this.trocando;
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
      // anda separado em x e y: encostou na parede, desliza ao longo dela
      const x2 = c.s.x + nx * v * dt;
      if (this.livre(x2, c.s.y)) c.s.x = x2;
      const y2 = c.s.y + ny * v * dt;
      if (this.livre(c.s.x, y2)) c.s.y = y2;
      c.facing = this.direcao(c, nx, ny);
      c.moving = true;
      c.extraAte = 0;
      this.mov.x = nx;
      this.mov.y = ny;
      c.s.play(`${c.nome}:${c.facing}_${correr ? "correr" : "andar"}`, true);
      this.aoAndar(c, nx, ny);
      if (correr && this.cfg.piso === "grama" && agora >= (c.poeiraEm || 0)) {
        this.poeira.setDepth(c.s.y - 1);
        this.poeira.explode(2, c.s.x - nx * 18, c.s.y - 4);
        c.poeiraEm = agora + 110;
      }
    } else if (c.moving && !c.roteiro) {
      c.moving = false;
      this.parar(c);
      this.agendarVida(c, agora);
    }
    for (const ch of this.chars) {
      this.vida(ch, agora);
      ch.s.setDepth(ch.s.y);
    }
    if (this.luz) {
      const pa = this.parceiro;
      if (this.dialogo.ativo && pa) this.luz.update(c, pa.s.x - c.s.x, pa.s.y - c.s.y, dt);
      else this.luz.update(c, c.moving ? this.mov.x : 0, c.moving ? this.mov.y : 0, dt);
    }
    // brilhinho no objeto mais perto
    const o = !preso && this.maisPerto();
    this.destaque.setVisible(!!o);
    if (o) this.destaque.setPosition(o.x, o.y - 40);
    this.aoAtualizar(dt, agora);
    this.desenharJoystick();
  }

  aoAndar() {}
  aoAtualizar() {}

  // ---------------------------------------------------------------- vida: parado não é estátua
  agendarVida(c, agora) {
    c.virarEm = agora + Phaser.Math.Between(4500, 7500);
    c.piscarEm = agora + Phaser.Math.Between(1800, 4800);
    c.olharEm = agora + Phaser.Math.Between(7000, 13000);
    c.gestoEm = agora + Phaser.Math.Between(12000, 20000);
    c.extraAte = 0;
  }

  vida(c, agora) {
    if (c.moving || c.agachado || c.semVida || c.roteiro) return;
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
    if (this.dialogo.ativo || this.travado) {
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

  // ---------------------------------------------------------------- toque
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

  botao(dx, dy, r, rotulo, aoApertar, aoSoltar) {
    const toque = this.sys.game.device.input.touch;
    const c = this.add.circle(0, 0, r, 0xffffff, 0.12).setStrokeStyle(4, 0xffffff, 0.5).setScrollFactor(0).setDepth(UI);
    const t = this.add.text(0, 0, rotulo, { fontFamily: "Trebuchet MS, Verdana, sans-serif", fontSize: rotulo.length > 7 ? "28px" : "36px", color: "#ffffff" })
      .setOrigin(0.5).setScrollFactor(0).setDepth(UI);
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
    this.posicionarBotoes();
  }

  criarToque() {
    this.botoes = [];
    this.joy = { ativo: false, id: null, bx: 0, by: 0, vx: 0, vy: 0, mag: 0 };
    this.correrSegurado = false;
    this.esconderSegurado = false;
    this.joyG = this.add.graphics().setScrollFactor(0).setDepth(UI);
    this.botao(190, 210, 120, "CORRER", () => (this.correrSegurado = true), () => (this.correrSegurado = false));
    if (this.cfg.esconder) this.botao(430, 330, 84, "ESCONDER", () => (this.esconderSegurado = true), () => (this.esconderSegurado = false));
    this.botao(430, 130, 84, "AÇÃO", () => this.acao());
    if (this.jogaveis.length > 1) this.botao(660, 150, 84, "TROCAR", () => this.proximoJogavel());
    this.scale.on("resize", () => this.posicionarBotoes());

    this.input.on("pointerdown", (p, sobre) => {
      if (this.dialogo.ativo && !sobre.length) return this.dialogo.avancar();
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
