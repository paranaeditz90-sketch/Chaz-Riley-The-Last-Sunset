import Phaser from "phaser";
import { CenaJogo, tocarAmbiente, tocarMusica } from "../base.js";
import { Cinema } from "../cinema.js";
import { estado } from "../estado.js";

// Capítulo 1, beat 1-2: o morro sobre o trigal. Feliz, a única vez que a música soa inteira.
// Na última nota o sol não desce: APAGA. Linhas de transmissão faíscam até o horizonte, a cidade apaga.
// Tudo em cutscene (o morro ainda não tem cenário jogável).

const NOITE_MORRO = 0x4c5478; // tinta de quem está no breu (só a lanterna do celular)

export default class Morro extends CenaJogo {
  constructor() {
    super("Morro");
  }

  config() {
    return { personagens: [{ nome: "chaz", x: -400, y: 900 }], controla: ["chaz"], esconder: false, cameraFixa: { x: 960, y: 540 } };
  }

  aoEntrar() {
    this.chars[0].s.setVisible(false);
    this.travado = true;
    this.cine = new Cinema(this);
    tocarMusica(this, "musica_entardecer", 0.2, 2000);
    tocarAmbiente(this, "vento_loop", 0.16, 2000);
    this.time.delayedCall(300, () => this.roteiro());
  }

  // ---------------------------------------------------------------- cenário (por cima do fundo pintado)
  // torres de transmissão: silhuetas de treliça, cada vez menores até o horizonte; os fios entre elas
  torres(c, noite) {
    const g = this.add.graphics().setScrollFactor(0);
    const H = c.H;
    const torres = [
      { x: c.px(0.06), y: H * 0.8, h: 560 }, { x: c.px(0.5), y: H * 0.7, h: 280 }, { x: c.px(0.8), y: H * 0.665, h: 150 },
      { x: c.px(0.97), y: H * 0.65, h: 80 },
    ];
    const cor = noite ? 0x07060c : 0x3a2440;
    g.lineStyle(4, cor);
    for (const t of torres) {
      const topo = t.y - t.h;
      const base = t.h * 0.22;
      g.lineBetween(t.x - base, t.y, t.x - base * 0.18, topo);
      g.lineBetween(t.x + base, t.y, t.x + base * 0.18, topo);
      for (let k = 1; k < 6; k++) { // treliça em X
        const y0 = t.y - (t.h * (k - 1)) / 5;
        const y1 = t.y - (t.h * k) / 5;
        const w0 = base * (1 - ((k - 1) / 5) * 0.82);
        const w1 = base * (1 - (k / 5) * 0.82);
        g.lineBetween(t.x - w0, y0, t.x + w1, y1);
        g.lineBetween(t.x + w0, y0, t.x - w1, y1);
      }
      g.lineBetween(t.x - t.h * 0.34, topo + t.h * 0.12, t.x + t.h * 0.34, topo + t.h * 0.12); // braço dos fios
      t.fios = [-0.32, 0, 0.32].map((f) => ({ x: t.x + f * t.h, y: topo + t.h * 0.12 }));
    }
    // fios: curva caída entre uma torre e a próxima; guarda pontos pra faísca andar por eles
    const pontos = [];
    g.lineStyle(2, cor, 0.9);
    for (let i = 0; i < torres.length - 1; i++) {
      for (let f = 0; f < 3; f++) {
        const a = torres[i].fios[f];
        const b = torres[i + 1].fios[f];
        const curva = new Phaser.Curves.QuadraticBezier(new Phaser.Math.Vector2(a.x, a.y), new Phaser.Math.Vector2((a.x + b.x) / 2, Math.max(a.y, b.y) + 40 * (1 - i * 0.3)), new Phaser.Math.Vector2(b.x, b.y));
        curva.draw(g, 32);
        if (f === 1) pontos.push(curva.getPoint(0.5));
      }
      pontos.push(new Phaser.Math.Vector2(torres[i + 1].x, torres[i + 1].y - torres[i + 1].h * 0.88));
    }
    c.camFundo.add(g);
    return pontos;
  }

  // luzinhas da cidade lá embaixo, entre os morros
  cidade(c) {
    const rnd = new Phaser.Math.RandomDataGenerator(["harrow"]);
    const luzes = [];
    for (let i = 0; i < 46; i++) {
      const x = c.px(0.1 + rnd.frac() * 0.42);
      const y = c.H * (0.685 + rnd.frac() * 0.035);
      const l = this.add.circle(x, y, rnd.between(3, 6), 0xffd99a, 0.95).setScrollFactor(0);
      c.camFundo.add(l);
      luzes.push(l);
    }
    // apagam em sequência da direita (perto) pra esquerda (longe): ordem por x
    return luzes.sort((a, b) => b.x - a.x);
  }

  sol(c) {
    const x = c.px(0.7);
    const y = c.H * 0.43;
    const brilho = this.add.image(x, y, "cine_brilho").setScrollFactor(0).setScale(26).setTint(0xffb070).setAlpha(0.55).setBlendMode(Phaser.BlendModes.ADD);
    const disco = this.add.circle(x, y, 118, 0xffd27a).setScrollFactor(0);
    c.camFundo.add([brilho, disco]);
    this.tweens.add({ targets: brilho, scale: 28, alpha: 0.62, duration: 2600, yoyo: true, repeat: -1, ease: "Sine.easeInOut" });
    return [brilho, disco];
  }

  plano(c, noite) {
    c.fundo(noite ? "cine_morro_noite" : "cine_morro_tarde");
    this.solPartes = noite ? [] : this.sol(c);
    this.pontosFio = this.torres(c, noite);
    this.luzes = this.cidade(c);
    if (!noite) c.poeira(14);
    c.entrar("chaz", null, { x: 0.3, escala: 0.98 });
    c.entrar("riley", null, { x: 0.52, escala: 0.98 });
    c.entrar("nevoa", null, { x: 0.76, escala: 0.98 });
    if (noite) c.tingir(NOITE_MORRO);
  }

  // faísca: estalo de luz branca-azulada num ponto do fio
  faisca(c, p) {
    const f = this.add.image(p.x, p.y, "cine_brilho").setScrollFactor(0).setScale(5).setTint(0xcfe0ff).setBlendMode(Phaser.BlendModes.ADD);
    c.camFundo.add(f);
    c.tremer(0.0015, 90);
    this.som("batida_vidro_1", 0.12, 2.4);
    this.tweens.add({ targets: f, scale: 0.5, alpha: 0, duration: 380, ease: "Cubic.easeOut", onComplete: () => f.destroy() });
  }

  async roteiro() {
    const c = this.cine;
    const f = estado.flags;
    c.expAtual = { chaz: "empolgacao", riley: "tedio", nevoa: "sono" };

    // ---------------------------------------------------------------- 1. chegada
    await c.abrir(() => {
      this.plano(c, false);
      c.camera({ z: 1.0, fx: 0.5, fy: 0.55 });
      c.camera({ z: 1.06, ms: 20000 });
    }, { fade: 900 });
    await c.esperar(700);
    await c.falar([
      ["chaz", "CHEGAMOS! E ELE AINDA TÁ AÍ.", "empolgacao"],
      ["riley", "POR POUCO.", "tedio"],
      ["nevoa", "...TÁ FRIO AQUI EM CIMA.", "nervoso"],
      ["riley", "TÁ VINTE E SEIS GRAUS, NÉVOA.", "irritacao"],
      ["nevoa", "...NÃO EM MIM.", "sono"],
    ]);
    // o Névoa treme de leve (frio que não é frio)
    const nevoa = c.atores.nevoa;
    if (nevoa) this.tweens.add({ targets: nevoa.cont, x: nevoa.cont.x + 3, duration: 60, yoyo: true, repeat: 30 });

    // ---------------------------------------------------------------- 2. o ombro (cânone)
    const chaz = c.atores.chaz;
    if (chaz) await c.tween({ targets: chaz.cont, x: c.px(0.4), angle: 5, duration: 700, ease: "Sine.easeInOut" });
    await c.falar([
      ["chaz", "...", "alegria_olhos_fechados"],
      ["riley", "NÃO SOU TRAVESSEIRO.", "irritacao"],
      ["chaz", "EU DISSE... SÓ UM POUQUINHO.", "alegria_olhos_fechados"],
      ["riley", "VOCÊ NÃO DISSE NADA.", "tedio"],
    ]);
    if (chaz) c.tween({ targets: chaz.cont, x: c.px(0.3), angle: 0, duration: 600, ease: "Sine.easeInOut" });

    // ---------------------------------------------------------------- 3. escolha A: a novidade
    await c.falar([
      ...(f.mentiu_bolso
        ? [["riley", "PRIMEIRO A 'PALHETA'. AGORA ESSA CARA.", "defensiva"]]
        : [["riley", "VOCÊ TÁ ESTRANHO HOJE.", "defensiva"]]),
      {
        id: "novidade", quem: "chaz", tempo: 8,
        opcoes: [
          { texto: "TENHO UMA NOVIDADE. MEIO GRANDE.", flag: "chaz_segredo_pista", exp: { chaz: "olhar_de_lado" },
            depois: [["riley", "...QUE NOVIDADE?", "tedio"], ["chaz", "DEPOIS DO PÔR DO SOL. PROMETO.", "tristeza"], ["riley", "VOCÊ E SEUS 'DEPOIS'.", "suspiro"]] },
          { texto: "ESTRANHO É ESSE SEU CABELO.", flag: "chaz_desconversou", exp: { chaz: "alegria" },
            depois: [["riley", "É PELO, CHAZ.", "mao_na_cara"], ["chaz", "ESTRANHO É ESSE SEU PELO.", "alegria_olhos_fechados"]] },
        ],
        silencio: [["riley", "...TÁ BOM. FICA COM ISSO AÍ.", "tedio"]],
        flagSilencio: "chaz_calou_novidade",
      },
    ]);

    // ---------------------------------------------------------------- 4. escolha B: um cachecol só (cânone)
    await c.falar([
      ["chaz", "TÁ VENTANDO MESMO. E EU SÓ TROUXE UM CACHECOL.", "explicando"],
      {
        id: "cachecol", quem: "chaz", tempo: 8,
        opcoes: [
          { texto: "PRA RILEY", flag: "cachecol_riley", exp: { chaz: "alegria" },
            depois: [["riley", "...VALEU.", "constrangimento"], ["nevoa", "...", "sono"]] },
          { texto: "PRO NÉVOA", flag: "cachecol_nevoa", exp: { chaz: "alegria" },
            depois: [["nevoa", "...OBRIGADO.", "calma"], ["riley", "EU TAMBÉM TÔ COM FRIO, SABIA.", "defensiva"], ["chaz", "VOCÊ DISSE QUE TAVA VINTE E SEIS GRAUS.", "olhar_de_lado"]] },
        ],
        silencio: [["chaz", "...VOU FICAR COM ELE. SOU FRIORENTO.", "olhar_de_lado"]],
        flagSilencio: "cachecol_chaz",
      },
    ]);

    // ---------------------------------------------------------------- 5. a música (a única vez inteira)
    tocarMusica(this, "musica_entardecer", 0.42, 1800);
    c.camera({ z: 1.12, fx: 0.52, fy: 0.5, ms: 14000 });
    await c.falar([
      ["chaz", "SABE QUAL É A MELHOR PARTE DO PÔR DO SOL?", "curiosidade"],
      ["riley", "QUANDO ACABA E A GENTE VAI EMBORA.", "tedio"],
      ["chaz", "♪ HM-HM-HMM... HM-HMM... ♪", "alegria_olhos_fechados"],
      ["riley", "...NÃO SEI ESSA.", "defensiva"],
      ["chaz", "SABE SIM.", "alegria"],
      ["riley", "♪ ...HM-HMM. HMM-HM... ♪", "suspiro"],
      ["nevoa", "♪ hmm... ♪", "calma"],
      ["chaz", "♪ HM-HM-HMMM... ♪", "alegria_olhos_fechados"],
    ]);

    // ---------------------------------------------------------------- 6. o sol APAGA (na última nota)
    const [brilho, disco] = this.solPartes;
    this.tweens.killTweensOf(brilho);
    tocarMusica(this, null, 0, 1);
    tocarAmbiente(this, null, 0, 1);
    for (const a of [0.15, 1, 0.05, 0.7]) { // pisca como lâmpada ruim
      brilho.setAlpha(0.55 * a);
      disco.setAlpha(a);
      await c.esperar(70);
    }
    c.corte(() => {
      this.plano(c, true);
      c.camera({ z: 1.12, fx: 0.52, fy: 0.5 });
    });
    for (const n of ["chaz", "riley", "nevoa"]) c.expressao(n, n === "chaz" ? "susto" : n === "riley" ? "tristeza" : "susto");
    await c.esperar(3000); // silêncio total

    // linhas de transmissão faíscam uma a uma até o horizonte, como um pavio; a cidade apaga em sequência
    for (const [i, p] of this.pontosFio.entries()) {
      this.faisca(c, p);
      const fatia = Math.ceil(this.luzes.length / this.pontosFio.length);
      this.luzes.slice(i * fatia, (i + 1) * fatia).forEach((l, k) => this.time.delayedCall(k * 40, () => l.setAlpha(0)));
      await c.esperar(260 + i * 40);
    }
    await c.esperar(1200);
    tocarAmbiente(this, "grilos_loop", 0.0, 1);

    // o celular vibra
    c.tremer(0.002, 400);
    await c.esperar(500);
    await c.falar([["chaz", "...", "susto"]]);
    c.corte(() => {
      c.fundo("cine_morro_noite");
      c.objeto("celular", { aviso: "Novo vídeo salvo — 0:47" });
      c.camera({ z: 1.0 });
      c.camera({ z: 1.05, ms: 6000 });
    });
    await c.esperar(1800);
    await c.falar([["chaz", "EU NÃO GRAVEI NADA."]], { fora: { chaz: "esquerda" } });
    c.corte(() => {
      c.fundo("cine_morro_noite");
      c.objeto("celular", { tela: "video", audio: "♪ hm... hm-hm... hmm... ♪", ms: 7000, ate: 0.14 });
      c.camera({ z: 1.0 });
      c.camera({ z: 1.08, ms: 7000 });
    });
    await c.esperar(4200);
    await c.falar([["riley", "...QUEM TÁ CANTANDO?"]], { fora: { riley: "direita" } });
    await c.esperar(1500);

    // ---------------------------------------------------------------- 7. "isso não é um pôr do sol"
    c.corte(() => {
      this.plano(c, true);
      c.camera({ z: 1.08, fx: 0.5, fy: 0.55 });
    });
    c.expressao("chaz", "susto");
    c.expressao("riley", "tristeza");
    c.expressao("nevoa", "nervoso");
    await c.falar([
      ["riley", "ISSO NÃO É UM PÔR DO SOL.", "tristeza"],
      ["chaz", "...A LANTERNA. A LANTERNA DO CELULAR FUNCIONA.", "susto"],
      ["nevoa", "...A RUA INTEIRA APAGOU.", "nervoso"],
    ]);
    // a lanterna acende: quem está em cena volta a ter cor (um pouco)
    c.tingir(0x8a90b4);
    await c.esperar(600);
    // lá embaixo, no trigal: um espantalho que não estava lá
    c.corte(() => {
      c.fundo("cine_morro_noite");
      const e = this.add.image(c.px(0.62), c.H * 0.86, "espantalho").setOrigin(0.5, 1).setScale(0.6).setTint(0x6a6e88).setScrollFactor(0);
      c.camFundo.add(e);
      const luz = this.add.image(c.px(0.62), c.H * 0.8, "cine_brilho").setScale(9).setTint(0xdfe6ff).setAlpha(0.16).setBlendMode(Phaser.BlendModes.ADD).setScrollFactor(0);
      c.camFundo.add(luz);
      c.camera({ z: 1.0, fx: 0.6, fy: 0.75 });
      c.camera({ z: 1.35, ms: 5000, ease: "Cubic.easeIn" });
    });
    await c.esperar(2600);
    await c.falar([
      ["nevoa", "...AQUILO TAVA ALI?"],
      ["riley", "NÃO."],
    ], { fora: { nevoa: "direita", riley: "esquerda" } });
    c.corte(() => {
      this.plano(c, true);
      c.tingir(0x8a90b4);
      c.camera({ z: 1.05, fx: 0.5, fy: 0.55 });
    });
    await c.falar([
      ["chaz", "A CASA DO SEU AMOS É LÁ EMBAIXO. ELE TEM TELEFONE.", "tristeza"],
      ["riley", "...TEM QUE ATRAVESSAR O TRIGAL.", "defensiva"],
      ["chaz", "ENTÃO A GENTE ATRAVESSA. JUNTOS.", "explicando"],
    ]);
    await c.fechar({ fade: 900 });
    this.scene.start("Trigal");
  }
}
