import Phaser from "phaser";

// Falas no estilo dos vídeos do Bruce: bilhete de papel rasgado, letra de mão na cor de quem fala.
// A "voz" é o som do bicho (decisão do diretor): cachorro late, gato mia. Nada de fala gravada.

export const FALANTES = {
  chaz: { nome: "Chaz", cor: "#1f3fd8", fonte: "Patrick Hand", tam: 50, vozes: ["voz_chaz_1", "voz_chaz_2", "voz_chaz_3"], tom: [1.0, 1.12], vol: 0.55 },
  riley: { nome: "Riley", cor: "#7a1426", fonte: "Permanent Marker", tam: 42, vozes: ["voz_riley_1", "voz_riley_2", "voz_riley_3"], tom: [0.95, 1.06], vol: 0.5 },
  nevoa: { nome: "Névoa", cor: "#6a5a80", fonte: "Shadows Into Light", tam: 50, vozes: ["voz_nevoa_1", "voz_nevoa_2"], tom: [0.78, 0.88], vol: 0.45 },
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
    ["riley", "...NÃO."],
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
    this.ativo = true;
    this.falas = falas;
    this.atores = atores;
    this.i = -1;
    this.aoTerminar = aoTerminar;
    const cena = this.cena;
    cena.tweens.add({ targets: [this.faixaCima, this.faixaBaixo], scaleY: 1, duration: 450, ease: "Sine.easeOut" });
    this.proxima();
  }

  // toque/tecla: se a fala ainda está aparecendo, mostra tudo; senão, vai pra próxima
  avancar() {
    if (!this.ativo) return;
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

  fechar() {
    const cena = this.cena;
    cena.tweens.add({ targets: [this.faixaCima, this.faixaBaixo], scaleY: 0, duration: 350, ease: "Sine.easeIn" });
    this.ativo = false;
    const fim = this.aoTerminar;
    this.aoTerminar = null;
    if (fim) fim();
  }
}
