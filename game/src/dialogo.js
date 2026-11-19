import Phaser from "phaser";
import { marcar, registrarEscolha } from "./estado.js";

// Falas no estilo dos vídeos do Bruce: bilhete de papel rasgado, letra de mão na cor de quem fala.
// A "voz" é o som do bicho (decisão do diretor): cachorro late, gato mia. Nada de fala gravada.

// cor do texto = cor do personagem (Chaz azul do sprite, Riley vermelho, Névoa chumbo), um pouco ajustada pra ler no papel
export const FALANTES = {
  chaz: { nome: "Chaz", cor: "#1a34e1", fonte: "Patrick Hand", tam: 50, vozes: ["voz_chaz_1", "voz_chaz_2", "voz_chaz_3"], tom: [1.0, 1.12], vol: 0.55 },
  riley: { nome: "Riley", cor: "#b3122b", fonte: "Permanent Marker", tam: 42, vozes: ["voz_riley_1", "voz_riley_2", "voz_riley_3"], tom: [0.95, 1.06], vol: 0.5 },
  cavalier: { nome: "Cavalier", cor: "#a4431f", fonte: "Kalam", tam: 46, vozes: ["voz_cavalier_1"], tom: [0.95, 1.08], vol: 0.5 },
  nevoa: { nome: "Névoa", cor: "#4e3a46", fonte: "Shadows Into Light", tam: 50, vozes: ["voz_nevoa_1", "voz_nevoa_2"], tom: [0.78, 0.88], vol: 0.45 },
};

// Conversas curtas do teste (sem spoiler). Chave: "quem_fala>com_quem".
export const CONVERSAS = {
  "chaz>riley": [
    ["chaz", "RILEY! OLHA O CÉU. PARECE QUE TÁ PEGANDO FOGO."],
    ["riley", "...É UM PÔR DO SOL, CHAZ."],
    ["chaz", "É O PÔR DO SOL. FICA AQUI SÓ MAIS UM POUCO."],
    ["riley", "EU TÔ AQUI, NÃO TÔ?"],
  ],
  "chaz>nevoa": [
    ["chaz", "NÉVOA! DORMIU EM PÉ DE NOVO?"],
    ["nevoa", "...SÓ PISQUEI DEVAGAR."],
  ],
  "riley>chaz": [
    ["riley", "POR QUE VOCÊ TÁ ME OLHANDO ASSIM?"],
    ["chaz", "TÔ OLHANDO SUAS ORELHAS."],
    {
      id: "teste_orelhas", quem: "riley", tempo: 6,
      opcoes: [
        { texto: "NÃO.", depois: [["chaz", "...TÁ BOM. TÁ BOM."]] },
        { texto: "...TÁ. PODE OLHAR.", depois: [["chaz", "ELAS MEXEM QUANDO VOCÊ FINGE QUE NÃO LIGA."], ["riley", "CALA A BOCA, CHAZ."]] },
      ],
      silencio: [["chaz", "...VOU ENTENDER ESSE SILÊNCIO COMO UM SIM."]],
    },
  ],
  "riley>nevoa": [
    ["riley", "VOCÊ TÁ COM CARA DE QUEM NÃO DORME FAZ DIAS."],
    ["nevoa", "...FAZ."],
    ["riley", "HM."],
  ],
  "nevoa>chaz": [
    ["nevoa", "CHAZ... VOCÊ ACHA QUE O SOL LEMBRA DA GENTE?"],
    ["chaz", "ACHO QUE LEMBRA DE VOCÊ. VOCÊ É O ÚNICO QUE OLHA PRA ELE ATÉ O FIM."],
  ],
  "nevoa>riley": [
    ["nevoa", "...VOCÊ TAMBÉM VEIO VER?"],
    ["riley", "NÃO. VIM GARANTIR QUE O CHAZ NÃO CAIA DO MORRO."],
  ],
};

// Mesmas duplas, de noite (tom de tensão, sem spoiler).
export const CONVERSAS_NOITE = {
  "chaz>riley": [
    ["chaz", "RILEY... VOCÊ TÁ OUVINDO ISSO?"],
    ["riley", "TÔ OUVINDO VOCÊ. SÓ VOCÊ."],
    ["chaz", "ENTÃO FICA PERTO DA LUZ."],
  ],
  "chaz>nevoa": [
    ["chaz", "NÉVOA, FICA PERTO."],
    ["nevoa", "...EU TÔ PERTO."],
  ],
  "riley>chaz": [
    ["riley", "APONTA ESSA LUZ PRA FRENTE, CHAZ."],
    ["chaz", "TÔ APONTANDO PRA VOCÊ."],
    ["riley", "...EU SEI."],
  ],
  "riley>nevoa": [
    ["riley", "NÃO SOME DE VISTA."],
    ["nevoa", "...TÁ."],
  ],
  "nevoa>chaz": [
    ["nevoa", "CHAZ... O ESCURO TÁ MAIS PERTO QUE ANTES?"],
    ["chaz", "É SÓ A NOITE. A NOITE NÃO ANDA."],
  ],
  "nevoa>riley": [
    ["nevoa", "...VOCÊ TÁ COM MEDO?"],
    ["riley", "NÃO."],
    ["riley", "...UM POUCO."],
  ],
};

const LETRAS_POR_SEG = 32;

// Papel rasgado: retângulo com borda serrilhada irregular, levemente torto.
function desenharPapel(g, w, h, rnd) {
  const pts = [];
  const passo = 18;
  const serra = () => rnd.between(-5, 5);
  for (let x = 0; x <= w; x += passo) pts.push([x, serra()]);
  for (let y = passo; y <= h; y += passo) pts.push([w + serra(), y]);
  for (let x = w - passo; x >= 0; x -= passo) pts.push([x, h + serra()]);
  for (let y = h - passo; y > 0; y -= passo) pts.push([serra(), y]);
  g.fillStyle(0x000000, 0.25);
  g.fillPoints(pts.map(([x, y]) => new Phaser.Math.Vector2(x + 6, y + 8)), true);
  g.fillStyle(0xfbf9f2, 1);
  g.fillPoints(pts.map(([x, y]) => new Phaser.Math.Vector2(x, y)), true);
}

export class Dialogo {
  constructor(cena) {
    this.cena = cena;
    this.ativo = false;
    this.rnd = new Phaser.Math.RandomDataGenerator([String(Date.now())]);
    const W = cena.scale.width;
    // faixas de cinema: tamanho fixo, entram e saem pela escala vertical (mudar a altura de um Shape não redesenha)
    this.faixaCima = cena.add.rectangle(0, 0, W * 3, 110, 0x000000).setOrigin(0, 0).setScrollFactor(0).setDepth(9e6).setScale(1, 0);
    this.faixaBaixo = cena.add.rectangle(0, cena.scale.height, W * 3, 110, 0x000000).setOrigin(0, 1).setScrollFactor(0).setDepth(9e6).setScale(1, 0);
    cena.scale.on("resize", (g) => this.faixaBaixo.setY(g.height));
  }

  // falas: [[quemFala, texto], ...]; atores: { chaz: sprite, ... }
  iniciar(falas, atores, aoTerminar) {
    // fala chegando com outra aberta: entra na fila (antes, a nova tomava o lugar e a antiga nunca "terminava")
    if (this.ativo) {
      this.fila = this.fila || [];
      this.fila.push([falas, atores, aoTerminar]);
      return;
    }
    this.ativo = true;
    this.falas = falas.slice(); // cópia: a escolha insere as falas do caminho escolhido
    this.atores = atores;
    this.i = -1;
    this.aoTerminar = aoTerminar;
    const cena = this.cena;
    cena.tweens.add({ targets: [this.faixaCima, this.faixaBaixo], scaleY: 1, duration: 450, ease: "Sine.easeOut" });
    this.proxima();
  }

  // toque/tecla: se a fala ainda está aparecendo, mostra tudo; senão, vai pra próxima
  avancar() {
    if (!this.ativo || this.escolhendo) return;
    if (this.revelando) {
      this.revelando = false;
      this.mostrarTudo();
      return;
    }
    this.proxima();
  }

  proxima() {
    const cena = this.cena;
    if (this.bilhete) {
      const velho = this.bilhete;
      cena.tweens.add({ targets: velho, alpha: 0, y: velho.y - 20, duration: 160, onComplete: () => velho.destroy() });
      this.bilhete = null;
    }
    this.i++;
    if (this.i >= this.falas.length) return this.fechar();
    if (!Array.isArray(this.falas[this.i])) return this.mostrarEscolha(this.falas[this.i]);
    const [quem, texto] = this.falas[this.i];
    const f = FALANTES[quem];
    const ator = this.atores[quem];

    const txt = cena.add.text(0, 0, texto, {
      fontFamily: `"${f.fonte}", "Trebuchet MS", sans-serif`,
      fontSize: `${f.tam}px`,
      color: f.cor,
      align: "center",
      wordWrap: { width: 560 },
      lineSpacing: 2,
    }).setOrigin(0.5);
    this.linhas = txt.getWrappedText(texto);
    const w = Math.max(220, txt.width + 70);
    const h = txt.height + 44;
    const g = cena.add.graphics();
    desenharPapel(g, w, h, this.rnd);
    g.setPosition(-w / 2, -h / 2);
    txt.setText("");
    const c = cena.add.container(ator.x, ator.y - 250, [g, txt]);
    c.setDepth(8e6).setAngle(this.rnd.realInRange(-2.5, 2.5)).setScale(0.85).setAlpha(0);
    c.dono = ator;
    this.txt = txt;
    this.bilhete = c;
    cena.tweens.add({ targets: c, scale: 1, alpha: 1, duration: 180, ease: "Back.easeOut" });

    this.tocar(`papel_${this.rnd.between(1, 3)}`, 0.35, this.rnd.realInRange(0.95, 1.1));
    this.falar(f);
    const total = this.linhas.join("").length;
    if (total > 28) cena.time.delayedCall(((total * 0.5) / LETRAS_POR_SEG) * 1000, () => this.ativo && this.falar(f));

    this.revelando = true;
    this.mostradas = 0;
    this.t0 = cena.time.now;
  }

  falar(f) {
    this.tocar(this.rnd.pick(f.vozes), f.vol, this.rnd.realInRange(f.tom[0], f.tom[1]));
  }

  tocar(chave, vol, rate) {
    if (this.cena.cache.audio.exists(chave)) this.cena.sound.play(chave, { volume: vol, rate });
  }

  mostrarTudo() {
    this.txt.setText(this.linhas.join("\n"));
  }

  update() {
    if (!this.ativo || !this.bilhete) return;
    // bilhete acompanha quem fala (acima da cabeça)
    const dono = this.bilhete.dono;
    this.bilhete.x += (dono.x - this.bilhete.x) * 0.2;
    if (!this.revelando) return;
    const n = Math.floor(((this.cena.time.now - this.t0) / 1000) * LETRAS_POR_SEG);
    if (n === this.mostradas) return;
    this.mostradas = n;
    let resto = n;
    const out = [];
    for (const l of this.linhas) {
      if (resto <= 0) break;
      out.push(l.slice(0, resto));
      resto -= l.length;
    }
    this.txt.setText(out.join("\n"));
    if (n >= this.linhas.join("").length) this.revelando = false;
  }

  // ---------------------------------------------------------------- escolha (com tempo: o silêncio também é escolha)
  // item: { id, quem, opcoes: [{ texto, depois: [[quem, fala]...], flag }], tempo: segundos, silencio: [...], flagSilencio }
  mostrarEscolha(item) {
    const cena = this.cena;
    const f = FALANTES[item.quem];
    this.escolhendo = item;
    const W = cena.scale.width;
    const H = cena.scale.height;
    const cards = [];
    const larg = Math.min(560, (W - 160) / item.opcoes.length - 30);
    item.opcoes.forEach((op, i) => {
      const txt = cena.add.text(0, 0, op.texto, {
        fontFamily: `"${f.fonte}", "Trebuchet MS", sans-serif`, fontSize: `${Math.round(f.tam * 0.8)}px`,
        color: f.cor, align: "center", wordWrap: { width: larg - 80 }, padding: { left: 6, right: 10 },
      }).setOrigin(0.5);
      const num = cena.add.text(0, 0, String(i + 1), { fontFamily: "Trebuchet MS, sans-serif", fontSize: "26px", color: "#8a8a8a" })
        .setOrigin(0.5);
      const w = Math.max(larg, txt.width + 70);
      const h = Math.max(110, txt.height + 50);
      const g = cena.add.graphics();
      desenharPapel(g, w, h, this.rnd);
      g.setPosition(-w / 2, -h / 2);
      num.setPosition(-w / 2 + 22, -h / 2 + 20);
      const x = W / 2 + (i - (item.opcoes.length - 1) / 2) * (larg + 30);
      const c = cena.add.container(x, H - 230, [g, txt, num]).setScrollFactor(0).setDepth(9.5e6)
        .setAngle(this.rnd.realInRange(-2, 2)).setAlpha(0).setSize(w, h).setInteractive({ useHandCursor: true });
      c.on("pointerdown", () => this.escolher(i));
      cena.tweens.add({ targets: c, alpha: 1, y: H - 250, duration: 220, delay: i * 70, ease: "Back.easeOut" });
      cards.push(c);
    });
    this.cards = cards;
    // tempo: barra que encolhe na cor de quem escolhe
    if (item.tempo) {
      this.barra = cena.add.rectangle(W / 2, H - 120, W * 0.6, 8, Phaser.Display.Color.HexStringToColor(f.cor).color)
        .setScrollFactor(0).setDepth(9.5e6);
      this.barraTween = cena.tweens.add({ targets: this.barra, scaleX: 0, duration: item.tempo * 1000, onComplete: () => this.escolher(-1) });
    }
    this.tocar(`papel_${this.rnd.between(1, 3)}`, 0.3, 0.9);
  }

  escolher(i) {
    const item = this.escolhendo;
    if (!item) return;
    this.escolhendo = null;
    if (this.barraTween) this.barraTween.stop();
    if (this.barra) this.barra.destroy();
    this.barra = this.barraTween = null;
    this.cards.forEach((c, k) => {
      this.cena.tweens.add({ targets: c, alpha: 0, y: c.y + (k === i ? -30 : 30), duration: 200, onComplete: () => c.destroy() });
    });
    const op = i >= 0 ? item.opcoes[i] : null;
    registrarEscolha(item.id, op ? i : "silencio");
    if (op && op.flag) marcar(op.flag);
    if (!op && item.flagSilencio) marcar(item.flagSilencio);
    const depois = op ? op.depois || [] : item.silencio || [];
    this.falas.splice(this.i + 1, 0, ...depois);
    this.cena.time.delayedCall(220, () => this.proxima());
  }

  // teclas 1/2/3 durante a escolha
  tecla(n) {
    if (this.escolhendo && n < this.escolhendo.opcoes.length) this.escolher(n);
  }

  fechar() {
    const cena = this.cena;
    cena.tweens.add({ targets: [this.faixaCima, this.faixaBaixo], scaleY: 0, duration: 350, ease: "Sine.easeIn" });
    this.ativo = false;
    const fim = this.aoTerminar;
    this.aoTerminar = null;
    if (fim) fim();
    if (!this.ativo && this.fila && this.fila.length) {
      const [f, a, t] = this.fila.shift();
      cena.time.delayedCall(250, () => this.iniciar(f, a, t));
    }
  }
}
