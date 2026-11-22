import Phaser from "phaser";
import { FALANTES } from "./dialogo.js";
import { ANCORAS } from "./retratos_dados.js";

// Cutscene "de vídeo": a arte em alta que o diretor mandou (uma imagem por expressão, sem redesenho), fundo com
// desfoque de lente, câmera que anda (com paralaxe), luz, poeira no ar, vinheta e corte entre planos.
// Roda por cima da cena de jogo, numa camada fixa na tela. As falas usam o mesmo bilhete do jogo, e a cena
// corta sozinha pro plano de quem fala (plano e contraplano).

export const EXPRESSOES = {
  chaz: {
    alegria: "chaz_11", alegria_olhos_fechados: "chaz_12", curiosidade: "chaz_13", explicando: "chaz_21",
    aceno: "chaz_22", susto: "chaz_23", tristeza: "chaz_31", empolgacao: "chaz_32", olhar_de_lado: "chaz_33",
  },
  riley: {
    tedio: "riley_11", irritacao: "riley_12", suspiro: "riley_13", raiva: "riley_21", mao_na_cara: "riley_22",
    tristeza: "riley_23", desanimo: "riley_31", choro: "riley_32", defensiva: "riley_33",
  },
  nevoa: {
    sono: "nevoa_11", desconfianca: "nevoa_12", suspiro: "nevoa_13", surpresa: "nevoa_14", costas: "nevoa_15",
    perfil: "nevoa_16", sentado: "nevoa_21", sentado_olhos_fechados: "nevoa_22", pensativo: "nevoa_23",
    encolhido: "nevoa_24", deitado: "nevoa_25", dormindo: "nevoa_26", irritacao: "nevoa_31", susto: "nevoa_32",
    nervoso: "nevoa_33", choro: "nevoa_34", duvida: "nevoa_35", calma: "nevoa_36",
  },
};

// piscar: só onde a pose de olho fechado encaixa na de olho aberto (medido pelo pé: 96,5% de sobreposição)
const PISCAR = { chaz_11: { chave: "chaz_12", dx: 6, dy: -1 } };
// altura (px do quadro 1920x1080) da pose de pé de referência; as outras poses do personagem usam a mesma escala
const ALTURA = { chaz: 540, riley: 560, nevoa: 530 };
const REF = { chaz: "chaz_11", riley: "riley_11", nevoa: "nevoa_11" };
const PROF = 7.6e6; // abaixo dos bilhetes (8e6), das faixas de cinema (9e6) e das escolhas (9.5e6)

export class Cinema {
  constructor(cena) {
    this.cena = cena;
    this.aberto = false;
    this.expAtual = {};
    this.planos = {};
    this.atores = {};
  }

  get W() {
    return this.cena.scale.width;
  }

  get H() {
    return this.cena.scale.height;
  }

  // quadro seguro 1920 de largura no centro da tela (a tela pode ser mais larga no celular)
  px(xr) {
    return this.W / 2 + (xr - 0.5) * 1920;
  }

  tween(cfg) {
    return new Promise((ok) => this.cena.tweens.add({ ...cfg, onComplete: () => ok() }));
  }

  esperar(ms) {
    return new Promise((ok) => this.cena.time.delayedCall(ms, ok));
  }

  // ---------------------------------------------------------------- abrir / fechar
  // montar: função que monta o primeiro plano enquanto a tela está preta
  async abrir(montar, { fade = 420 } = {}) {
    const c = this.cena;
    if (this.aberto) {
      if (montar) this.corte(montar);
      return;
    }
    this.aberto = true;
    this.preto = c.add.rectangle(-this.W, -this.H, this.W * 3, this.H * 3, 0x000000).setOrigin(0).setScrollFactor(0)
      .setDepth(PROF + 0.3e6).setAlpha(0);
    await this.tween({ targets: this.preto, alpha: 1, duration: fade });
    this.camFundo = c.add.container(0, 0).setScrollFactor(0).setDepth(PROF);
    this.camAtores = c.add.container(0, 0).setScrollFactor(0).setDepth(PROF + 1);
    this.camFrente = c.add.container(0, 0).setScrollFactor(0).setDepth(PROF + 2);
    this.vinheta = c.add.image(0, 0, "cine_vinheta").setOrigin(0).setScrollFactor(0).setDepth(PROF + 3)
      .setDisplaySize(this.W, this.H);
    this.cam = { z: 1, fx: 0.5, fy: 0.5 };
    this.atores = {};
    const d = c.dialogo;
    d.faixasFixas = true;
    c.tweens.add({ targets: [d.faixaCima, d.faixaBaixo], scaleY: 1, duration: 300 });
    c.modoCinema?.(true); // some HUD, dicas e botões de toque (tocar em qualquer lugar avança a fala)
    d.antesDaFala = (quem, linha) => this.antesDaFala(quem, linha);
    d.antesDaEscolha = (item) => this.antesDaFala(item.quem, null);
    d.aoEscolher = (op) => op && op.exp && Object.entries(op.exp).forEach(([n, e]) => this.expressao(n, e));
    this.ouvinte = () => this.atualizar();
    c.events.on("update", this.ouvinte);
    c.scale.on("resize", this.aoRedimensionar, this);
    if (montar) this.corte(montar);
    await this.tween({ targets: this.preto, alpha: 0, duration: fade });
  }

  async fechar({ fade = 420 } = {}) {
    if (!this.aberto) return;
    const c = this.cena;
    const d = c.dialogo;
    await this.tween({ targets: this.preto, alpha: 1, duration: fade });
    this.limpar();
    [this.camFundo, this.camAtores, this.camFrente, this.vinheta].forEach((o) => o.destroy());
    d.faixasFixas = false;
    d.antesDaFala = d.antesDaEscolha = d.aoEscolher = null;
    c.modoCinema?.(false);
    c.tweens.add({ targets: [d.faixaCima, d.faixaBaixo], scaleY: 0, duration: 300 });
    c.events.off("update", this.ouvinte);
    c.scale.off("resize", this.aoRedimensionar, this);
    this.aberto = false;
    this.planos = {};
    this.planoAtual = null;
    await this.tween({ targets: this.preto, alpha: 0, duration: fade });
    this.preto.destroy();
  }

  // ---------------------------------------------------------------- planos (corte seco entre eles)
  // planos com nome: { nome: { quem: ["riley"], montar: (cine) => {...} } } -> a fala de "riley" corta pra lá sozinha
  corte(qual) {
    const montar = typeof qual === "function" ? qual : this.planos[qual]?.montar;
    if (!montar) return;
    this.limpar();
    this.planoAtual = typeof qual === "function" ? null : qual;
    this.montarAtual = montar;
    this.cam = { z: 1, fx: 0.5, fy: 0.5 };
    montar(this);
    this.aplicarCamera();
  }

  limpar() {
    const t = this.cena.tweens;
    for (const L of [this.camFundo, this.camAtores, this.camFrente]) {
      if (!L) continue;
      L.each((o) => {
        t.killTweensOf(o);
        if (o.list) o.list.forEach((f) => t.killTweensOf(f));
      });
      L.removeAll(true);
    }
    if (this.camTween) this.camTween.stop();
    this.camTween = null;
    if (this.emissor) this.emissor.destroy();
    this.emissor = null;
    this.atores = {};
  }

  aoRedimensionar() {
    if (!this.aberto) return;
    this.vinheta.setDisplaySize(this.W, this.H);
    if (this.montarAtual) this.corte(this.planoAtual || this.montarAtual);
  }

  // ---------------------------------------------------------------- câmera (zoom e foco em fração do quadro)
  camera({ z, fx, fy, ms = 0, ease = "Sine.easeInOut" } = {}) {
    const alvo = { z: z ?? this.cam.z, fx: fx ?? this.cam.fx, fy: fy ?? this.cam.fy };
    if (this.camTween) this.camTween.stop();
    this.camTween = null;
    if (!ms) {
      Object.assign(this.cam, alvo);
      this.aplicarCamera();
      return Promise.resolve();
    }
    return new Promise((ok) => {
      this.camTween = this.cena.tweens.add({ targets: this.cam, ...alvo, duration: ms, ease, onComplete: () => ok() });
    });
  }

  aplicarCamera() {
    const { z, fx, fy } = this.cam;
    const Fx = this.px(fx);
    const Fy = fy * this.H;
    // paralaxe: o fundo anda menos que os atores; o que está na frente (janela, poeira) anda um pouco mais
    for (const [L, p] of [[this.camFundo, 0.45], [this.camAtores, 1], [this.camFrente, 1.12]]) {
      if (!L) continue;
      const zl = 1 + (z - 1) * p;
      const lx = this.W / 2 + (Fx - this.W / 2) * p;
      const ly = this.H / 2 + (Fy - this.H / 2) * p;
      L.setScale(zl);
      L.setPosition(this.W / 2 - lx * zl, this.H / 2 - ly * zl);
    }
    if (this.tremor) {
      const f = this.tremor;
      this.camAtores.x += Phaser.Math.FloatBetween(-f, f) * this.W;
      this.camAtores.y += Phaser.Math.FloatBetween(-f, f) * this.H;
    }
  }

  tremer(forca = 0.004, ms = 220) {
    this.tremor = forca;
    this.cena.time.delayedCall(ms, () => (this.tremor = 0));
  }

  // ---------------------------------------------------------------- fundo e elementos de cena
  fundo(chave) {
    const img = this.cena.add.image(this.W / 2, this.H / 2, chave).setScrollFactor(0);
    img.setScale(Math.max(this.W / img.width, this.H / img.height) * 1.12);
    this.camFundo.add(img);
    // a câmera "respira": o fundo deriva devagar
    this.cena.tweens.add({ targets: img, x: img.x - 28, y: img.y - 8, duration: 15000, yoyo: true, repeat: -1, ease: "Sine.easeInOut" });
    return img;
  }

  // poeira dourada flutuando na luz da janela
  poeira(qtd = 26) {
    const emissor = this.cena.add.particles(0, 0, "cine_brilho", {
      x: { min: this.px(0.05), max: this.px(0.95) }, y: { min: this.H * 0.1, max: this.H * 0.9 },
      lifespan: { min: 5000, max: 9000 }, speedX: { min: -8, max: 8 }, speedY: { min: -14, max: -4 },
      scale: { min: 0.25, max: 0.7 }, alpha: { values: [0, 0.55, 0], interpolation: "linear" },
      frequency: 260, quantity: 1, tint: 0xffd9a0, blendMode: "ADD",
    }).setScrollFactor(0);
    emissor.fastForward(6000);
    this.camFrente.add(emissor);
    this.emissor = emissor;
  }

  // a janela do quarto vista de dentro: parede roxa, cortinas azuis e moldura de madeira (cores do cenário)
  janela() {
    const g = this.cena.add.graphics().setScrollFactor(0);
    const x0 = this.px(0.24);
    const x1 = this.px(0.76);
    const y0 = this.H * 0.1;
    const y1 = this.H * 0.76;
    const borda = 44;
    g.fillStyle(0x5b3c9c);
    g.fillRect(-this.W, -this.H, this.W * 3, y0 - borda + this.H);
    g.fillRect(-this.W, y1 + borda, this.W * 3, this.H * 2);
    g.fillRect(-this.W, y0 - borda, x0 - borda + this.W, y1 - y0 + 2 * borda);
    g.fillRect(x1 + borda, y0 - borda, this.W * 2, y1 - y0 + 2 * borda);
    // reflexo no vidro
    g.fillStyle(0xffffff, 0.06);
    g.fillPoints([new Phaser.Math.Vector2(x0 + 60, y1), new Phaser.Math.Vector2(x0 + 220, y0), new Phaser.Math.Vector2(x0 + 300, y0), new Phaser.Math.Vector2(x0 + 140, y1)], true);
    g.fillPoints([new Phaser.Math.Vector2(x1 - 330, y1), new Phaser.Math.Vector2(x1 - 200, y0), new Phaser.Math.Vector2(x1 - 160, y0), new Phaser.Math.Vector2(x1 - 290, y1)], true);
    // moldura
    g.fillStyle(0x8a4a22);
    g.lineStyle(8, 0x120a12);
    const barra = (x, y, w, h) => {
      g.fillRect(x, y, w, h);
      g.strokeRect(x, y, w, h);
    };
    barra(x0 - borda, y0 - borda, x1 - x0 + 2 * borda, borda);
    barra(x0 - borda, y0, borda, y1 - y0);
    barra(x1, y0, borda, y1 - y0);
    barra(x0 - borda * 1.6, y1, x1 - x0 + borda * 3.2, borda * 1.5); // peitoril
    // cortinas
    g.fillStyle(0x3348b8);
    g.lineStyle(8, 0x120a12);
    for (const [cx, sent] of [[x0 - borda - 90, -1], [x1 + borda + 90, 1]]) {
      g.fillRect(cx - 120, y0 - borda - 40, 240, y1 - y0 + borda * 2.6);
      g.strokeRect(cx - 120, y0 - borda - 40, 240, y1 - y0 + borda * 2.6);
      g.lineStyle(5, 0x1f2c7a);
      for (let i = 1; i < 4; i++) g.lineBetween(cx - 120 + i * 60, y0, cx - 120 + i * 60 + sent * 10, y1 + borda);
      g.lineStyle(8, 0x120a12);
    }
    this.camFrente.add(g);
  }

  // close de objeto: papel com texto (carta, caderno). Desenhado por código, fiel ao cenário do quarto.
  objeto(tipo) {
    const c = this.cena;
    const L = this.camFrente;
    const cx = this.W / 2;
    const cy = this.H * 0.45;
    const add = (o) => {
      o.setScrollFactor(0);
      L.add(o);
      return o;
    };
    const papel = (w, h) => add(c.add.rectangle(cx + 18, cy + 22, w, h, 0x000000, 0.35)); // sombra embaixo do papel
    if (tipo === "carta") {
      const w = 1000;
      const h = 660;
      papel(w, h);
      add(c.add.rectangle(cx, cy, w, h, 0xf3ecd9).setStrokeStyle(4, 0x9b8c6c));
      add(c.add.rectangle(cx, cy - 10, w - 6, 3, 0xd8ccb0)); // dobra
      add(c.add.circle(cx + w / 2 - 120, cy + h / 2 - 120, 56, 0x8c1c1c).setStrokeStyle(6, 0x5e0f0f)); // selo
      const serif = "Georgia, 'Times New Roman', serif";
      add(c.add.text(cx - w / 2 + 70, cy - h / 2 + 60, "CONSERVATÓRIO ESTADUAL DE MÚSICA", { fontFamily: serif, fontSize: "40px", color: "#2a2018", fontStyle: "bold" }));
      add(c.add.text(cx - w / 2 + 70, cy - h / 2 + 112, "Departamento de Admissões", { fontFamily: serif, fontSize: "28px", color: "#5a4c3a", fontStyle: "italic" }));
      add(c.add.text(cx - w / 2 + 70, cy - h / 2 + 200,
        "Prezado Chaz Barkley,\n\nTemos a alegria de informar que você foi aceito\nno Conservatório Estadual de Música.\nAs aulas começam no início do próximo mês.\n\nAtenciosamente,\nCoordenação de Admissões",
        { fontFamily: serif, fontSize: "32px", color: "#2a2018", lineSpacing: 8 }));
    } else if (tipo === "caderno") {
      const w = 920;
      const h = 700;
      papel(w, h);
      add(c.add.rectangle(cx, cy, w, h, 0xfbfaf4).setStrokeStyle(4, 0xb9b3a2));
      const g = add(c.add.graphics());
      g.lineStyle(3, 0x9cc2e6);
      for (let y = cy - h / 2 + 110; y < cy + h / 2 - 20; y += 58) g.lineBetween(cx - w / 2 + 10, y, cx + w / 2 - 10, y);
      g.lineStyle(4, 0xe08a8a);
      g.lineBetween(cx - w / 2 + 110, cy - h / 2 + 10, cx - w / 2 + 110, cy + h / 2 - 10);
      const mao = { fontFamily: '"Patrick Hand", sans-serif', color: "#1a34e1" };
      const x = cx - w / 2 + 140;
      let y = cy - h / 2 + 50;
      const linha = (t, tam = 46, extra = {}) => {
        const o = add(c.add.text(x, y, t, { ...mao, fontSize: `${tam}px`, ...extra }));
        y += 58;
        return o;
      };
      const titulo = linha("THE LAST SUNSET", 54);
      g.lineStyle(4, 0x1a34e1);
      g.lineBetween(x, y - 8, x + titulo.width, y - 6);
      linha("se eu for antes do sol voltar,");
      linha("não me procura no morro");
      const riscada = linha("socorro");
      g.lineStyle(6, 0x1a34e1);
      g.lineBetween(x - 6, riscada.y + 30, x + riscada.width + 8, riscada.y + 24);
      g.lineBetween(x - 6, riscada.y + 24, x + riscada.width + 8, riscada.y + 32);
      linha("se eu for antes do sol voltar...");
      linha("???", 52);
    }
    return L;
  }

  // ---------------------------------------------------------------- atores (arte em alta)
  imagem(chave, base) {
    const a = ANCORAS[chave];
    return this.cena.add.image(0, 0, `ret_${chave}`).setOrigin(a.cx / a.w, a.pe / a.h).setScale(base).setScrollFactor(0);
  }

  // x: fração do quadro seguro; y: onde fica o pé (fração da altura; > 1 = pé abaixo da tela, plano mais fechado)
  entrar(nome, exp, { x = 0.5, y = 0.97, escala = 1, de = null } = {}) {
    exp = exp || this.expAtual[nome] || Object.keys(EXPRESSOES[nome])[0];
    this.expAtual[nome] = exp;
    const chave = EXPRESSOES[nome][exp];
    const base = (ALTURA[nome] / ANCORAS[REF[nome]].h) * escala;
    const cont = this.cena.add.container(this.px(x), y * this.H).setScrollFactor(0);
    const img = this.imagem(chave, base);
    cont.add(img);
    this.camAtores.add(cont);
    const at = { nome, cont, img, chave, base, piscarEm: this.cena.time.now + Phaser.Math.Between(1200, 3500) };
    this.atores[nome] = at;
    // respira e balança de leve, cada um num ritmo
    this.cena.tweens.add({ targets: cont, scaleY: 1.012, scaleX: 0.997, duration: Phaser.Math.Between(1700, 2200), yoyo: true, repeat: -1, ease: "Sine.easeInOut" });
    this.cena.tweens.add({ targets: cont, angle: { from: -0.35, to: 0.35 }, duration: Phaser.Math.Between(2600, 3400), yoyo: true, repeat: -1, ease: "Sine.easeInOut" });
    if (de) {
      const alvo = cont.x;
      cont.x = de === "esquerda" ? alvo - 700 : alvo + 700;
      this.cena.tweens.add({ targets: cont, x: alvo, duration: 520, ease: "Cubic.easeOut" });
    }
    return at;
  }

  async sair(nome, { para = "direita", ms = 480 } = {}) {
    const at = this.atores[nome];
    if (!at) return;
    delete this.atores[nome];
    await this.tween({ targets: at.cont, x: at.cont.x + (para === "esquerda" ? -800 : 800), alpha: 0.2, duration: ms, ease: "Cubic.easeIn" });
    this.cena.tweens.killTweensOf(at.cont);
    at.cont.destroy();
  }

  expressao(nome, exp) {
    if (!exp || !EXPRESSOES[nome]?.[exp]) return;
    this.expAtual[nome] = exp;
    const at = this.atores[nome];
    if (!at) return;
    const chave = EXPRESSOES[nome][exp];
    if (chave === at.chave) return;
    const nova = this.imagem(chave, at.base).setAlpha(0);
    at.cont.add(nova);
    const velha = at.img;
    at.img = nova;
    at.chave = chave;
    nova.setScale(at.base * 1.025, at.base * 0.975);
    this.cena.tweens.add({ targets: nova, alpha: 1, scaleX: at.base, scaleY: at.base, duration: 160, ease: "Back.easeOut" });
    this.cena.tweens.add({ targets: velha, alpha: 0, duration: 120, onComplete: () => velha.destroy() });
  }

  // quem fala dá um pulinho (no ritmo do latido/miado)
  falou(nome) {
    const at = this.atores[nome];
    if (!at) return;
    const y = at.cont.y;
    this.cena.tweens.add({ targets: at.cont, y: y - 12, duration: 85, yoyo: true, repeat: 1, ease: "Sine.easeOut", onComplete: () => (at.cont.y = y) });
  }

  atualizar() {
    this.aplicarCamera();
    const t = this.cena.time.now;
    for (const at of Object.values(this.atores)) {
      const pb = PISCAR[at.chave];
      if (!pb || t < at.piscarEm) continue;
      at.piscarEm = t + (Math.random() < 0.2 ? 260 : Phaser.Math.Between(2200, 5200));
      const img = at.img;
      const volta = at.chave;
      const a = ANCORAS[pb.chave];
      img.setTexture(`ret_${pb.chave}`).setOrigin(a.cx / a.w, a.pe / a.h);
      img.setPosition(pb.dx * at.base, pb.dy * at.base);
      this.cena.time.delayedCall(110, () => {
        if (at.img !== img || at.chave !== volta || !img.active) return;
        const b = ANCORAS[volta];
        img.setTexture(`ret_${volta}`).setOrigin(b.cx / b.w, b.pe / b.h).setPosition(0, 0);
      });
    }
  }

  // ---------------------------------------------------------------- falas
  // posição do bilhete: em cima da cabeça de quem está no quadro; quem não está fala da borda (fora) ou embaixo
  ancoraDe(quem, fora) {
    const self = this;
    const lado = fora[quem];
    return {
      tela: true,
      get x() {
        const at = self.atores[quem];
        if (at) return self.camAtores.x + at.cont.x * self.camAtores.scaleX;
        if (lado === "direita") return self.W - 300;
        if (lado === "esquerda") return 300;
        return self.W / 2;
      },
      get y() {
        const at = self.atores[quem];
        if (at) {
          const a = ANCORAS[at.chave];
          const topo = at.cont.y - (a.pe - a.topo) * at.base;
          return self.camAtores.y + topo * self.camAtores.scaleY;
        }
        return lado ? self.H * 0.5 : self.H * 0.86;
      },
    };
  }

  // falas no formato do dialogo.js; cada linha pode trazer [quem, texto, expressão de quem fala, { reações dos outros }]
  falar(falas, { fora = {} } = {}) {
    const atores = {};
    for (const quem of Object.keys(FALANTES)) atores[quem] = this.ancoraDe(quem, fora);
    return new Promise((ok) => this.cena.dialogo.iniciar(falas, atores, ok));
  }

  antesDaFala(quem, linha) {
    if (!this.atores[quem]) {
      const nome = Object.keys(this.planos).find((k) => this.planos[k].quem.includes(quem));
      if (nome && nome !== this.planoAtual) this.corte(nome);
    }
    if (linha && linha[2]) this.expressao(quem, linha[2]);
    if (linha && linha[3]) Object.entries(linha[3]).forEach(([n, e]) => this.expressao(n, e));
    if (linha) this.falou(quem);
  }
}
