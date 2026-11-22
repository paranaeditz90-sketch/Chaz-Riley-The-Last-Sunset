import Phaser from "phaser";
import { CenaJogo, tocarAmbiente, tocarMusica } from "../base.js";
import { Cinema } from "../cinema.js";
import { estado, marcar } from "../estado.js";

// Prólogo, cena 1: o quarto do Chaz, fim de tarde. Cenário: imagem gerada pelo diretor (ChatGPT).
// As medidas abaixo estão em pixels da IMAGEM (1672x941); S converte pro jogo (altura 1080).
// Momentos importantes viram cutscene de cinema (arte em alta, planos, câmera): o caderno, a carta e a janela.

const S = 1080 / 941;
const P = (x, y) => ({ x: x * S, y: y * S });
const R = (x0, y0, x1, y1) => ({ x: x0 * S, y: y0 * S, w: (x1 - x0) * S, h: (y1 - y0) * S });

export default class Quarto extends CenaJogo {
  constructor() {
    super("Quarto");
  }

  config() {
    const ini = P(820, 660);
    return {
      personagens: [{ nome: "chaz", x: ini.x, y: ini.y, facing: "frente" }],
      controla: ["chaz"],
      mundo: { w: 1672 * S, h: 1080 },
      area: { x0: 160 * S, y0: 455 * S, x1: 1525 * S, y1: 835 * S },
      obstaculos: [
        R(130, 290, 450, 650), // cama
        R(470, 330, 640, 492), // criado-mudo
        R(815, 300, 1230, 532), // escrivaninha
        R(885, 400, 1020, 566), // cadeira
        R(1275, 300, 1500, 532), // amplificador e guitarra
        R(105, 610, 318, 860), // planta e estante
        R(1332, 572, 1555, 860), // toca-discos
      ],
      piso: "madeira",
      esconder: false,
      cameraFixa: P(836, 470),
    };
  }

  criarCenario() {
    this.add.image(0, 0, "cenario_quarto").setOrigin(0).setScale(S).setDepth(-1e6);
  }

  // planos de cinema do quarto: o Chaz (câmera do lado da janela, quarto desfocado atrás) e quem está do lado
  // de fora da janela (câmera dentro do quarto, céu atrás do vidro)
  planos() {
    return {
      chaz: {
        quem: ["chaz"],
        montar: (c) => {
          c.fundo("cine_quarto");
          c.poeira();
          c.entrar("chaz", null, { x: 0.42, escala: 1.22 });
          c.camera({ z: 1.03, fx: 0.44, fy: 0.56 });
          c.camera({ z: 1.09, ms: 9000 });
        },
      },
      riley: {
        quem: ["riley"],
        montar: (c) => {
          c.fundo("cine_ceu_tarde");
          c.entrar("riley", null, { x: 0.5, y: 0.98, escala: 1.35 });
          c.janela();
          c.camera({ z: 1.02, fx: 0.5, fy: 0.5 });
          c.camera({ z: 1.07, ms: 9000 });
        },
      },
    };
  }

  aoEntrar() {
    this.cine = new Cinema(this);
    this.lidos = 0;
    this.visitaFeita = false;
    this.emVisita = false;
    this.saindo = false;
    tocarMusica(this, "musica_entardecer", 0.16, 2000);
    tocarAmbiente(this, null, 0, 800);

    const toque = this.sys.game.device.input.touch;
    const dica = this.add.text(48, this.scale.height - 60, toque ? "Chegue perto das coisas e toque em AÇÃO" : "Chegue perto das coisas e aperte E",
      { fontFamily: "Trebuchet MS, sans-serif", fontSize: "34px", color: "#fff3d6", stroke: "#000", strokeThickness: 6 })
      .setOrigin(0, 1).setScrollFactor(0).setDepth(1e7).setAlpha(0);
    this.tweens.add({ targets: dica, alpha: 1, duration: 600, delay: 2600, hold: 6000, yoyo: true });
    this.hud = [dica];

    const pensa = (...linhas) => linhas.map((l) => ["chaz", l]);
    const contar = () => {
      this.lidos++;
      if (this.lidos >= 3) this.time.delayedCall(1500, () => this.visita());
    };
    // primeira vez: momento (pode ser cutscene); depois: só um pensamento curto
    const umaVez = (id, primeira, depois) => async () => {
      if (!estado.flags[`quarto_${id}`]) {
        marcar(`quarto_${id}`);
        await primeira();
        contar();
      } else {
        await this.dizer(depois);
      }
    };

    this.interativo({
      id: "caderno", ...P(930, 470), raio: 190,
      acao: umaVez("caderno", async () => {
        marcar("leu_letra");
        const c = this.cine;
        c.planos = {}; // no close do objeto, o pensamento vira legenda embaixo (sem corte automático pro rosto)
        await c.abrir(() => {
          c.fundo("cine_quarto");
          c.objeto("caderno");
          c.camera({ z: 1 });
          c.camera({ z: 1.06, ms: 9000 });
        });
        await c.esperar(1800); // tempo de ler a página
        await c.falar(pensa("(A MÚSICA.)", "(FALTA O ÚLTIMO VERSO. SEMPRE FALTA.)"));
        c.expAtual.chaz = "olhar_de_lado";
        c.corte(this.planos().chaz.montar);
        await c.esperar(350);
        await c.falar(pensa("(...RIMA COM 'MORRO'. 'SOCORRO'. NÃO.)"));
        await c.fechar();
      }, pensa("(DEPOIS EU TERMINO. DEPOIS.)")),
    });
    this.interativo({
      id: "guitarra", ...P(1390, 485), raio: 180,
      acao: umaVez("guitarra", () => this.dizer(pensa("(A GUITARRA NEM É MINHA.)", "(TÁ COMIGO FAZ UMA SEMANA. EM MINHA DEFESA, ELA GOSTA MAIS DE MIM.)")),
        pensa("(UM DIA EU DEVOLVO. UM DIA.)")),
    });
    this.interativo({
      id: "cama", ...P(455, 560), raio: 180,
      acao: umaVez("cama", async () => {
        await this.dizer(pensa("(EMBAIXO DO COLCHÃO.)"));
        const c = this.cine;
        c.planos = {};
        await c.abrir(() => {
          c.fundo("cine_quarto");
          c.objeto("carta");
          c.camera({ z: 1 });
          c.camera({ z: 1.07, ms: 10000 });
        });
        await c.esperar(2800); // tempo de ler a carta
        await c.falar(pensa("(TRÊS SEMANAS. E EU AINDA NÃO CONTEI PRA NINGUÉM.)"));
        c.expAtual.chaz = "tristeza";
        c.corte(this.planos().chaz.montar);
        await c.esperar(400);
        await c.falar([
          {
            id: "carta", quem: "chaz",
            opcoes: [
              { texto: "GUARDAR DE VOLTA", flag: "carta_escondida", exp: { chaz: "olhar_de_lado" }, depois: pensa("(DEPOIS. DEPOIS EU VEJO ISSO.)") },
              { texto: "LEVAR NO BOLSO", flag: "carta_no_bolso", exp: { chaz: "empolgacao" }, depois: pensa("(VAI QUE HOJE EU TENHO CORAGEM.)") },
            ],
          },
        ]);
        await c.fechar();
      }, pensa("(AINDA TÁ LÁ. EMBAIXO DO COLCHÃO.)")),
    });
    this.interativo({
      id: "janela", ...P(730, 470), raio: 170,
      acao: umaVez("janela", () => this.dizer(pensa("(O CÉU TÁ BONITO DEMAIS HOJE.)", "(PARECE CENÁRIO.)")), pensa("(LARANJA DEMAIS. ESQUISITO.)")),
    });
    this.interativo({
      id: "discos", ...P(1300, 645), raio: 170,
      acao: umaVez("discos", () => this.dizer(pensa("(SE EU COLOCAR UM DISCO AGORA, NÃO SAIO MAIS DAQUI.)")), pensa("(NÃO. FOCO.)")),
    });
    this.interativo({
      id: "porta", ...P(830, 815), raio: 150,
      acao: async () => {
        if (!this.visitaFeita) {
          await this.dizer(pensa("(BELEZA. AGORA VAI.)"));
          return this.visita();
        }
        this.sairPelaPorta();
      },
    });

    // pensamento de abertura: só se o jogador ainda não estiver no meio de outra coisa (cutscene, fala)
    this.time.delayedCall(1200, () => {
      if (!this.travado && !this.dialogo.ativo && !this.cine.aberto) this.dizer(pensa("(SÓ MAIS UM MINUTO. DOIS. NO MÁXIMO TRÊS.)"));
    });
    // se ninguém mexer em nada, a visita chega mesmo assim
    this.time.delayedCall(50000, () => this.visita());
  }

  async bater(n, vol) {
    for (let i = 0; i < n; i++) {
      this.som(`batida_vidro_${i % 3}`, vol, Phaser.Math.FloatBetween(0.95, 1.05));
      if (this.cine.aberto) this.cine.tremer(0.003, 120);
      await this.esperar(260);
    }
  }

  // ---------------------------------------------------------------- batem na janela (cutscene)
  async visita() {
    if (this.visitaFeita || this.emVisita) return;
    if (this.dialogo.ativo || this.travado) {
      this.time.delayedCall(800, () => this.visita());
      return;
    }
    this.emVisita = true;
    this.travado = true;
    const chaz = this.chars[0];
    await this.bater(3, 0.6);
    await this.esperar(400);
    // vai até a janela (entre o criado-mudo e a escrivaninha)
    const frente = P(728, 545);
    await this.andarAte(chaz, chaz.s.x, Math.max(chaz.s.y, 600 * S));
    await this.andarAte(chaz, frente.x, frente.y);
    this.virar(chaz, "costas");
    await this.esperar(300);

    const c = this.cine;
    c.planos = this.planos();
    c.expAtual.chaz = "curiosidade";
    await c.abrir("chaz");
    await c.esperar(500);
    // quem bateu primeiro fica do lado de fora, fora do quadro: só o bilhete dela entra pela borda
    const fora = { cavalier: "direita" };
    await c.falar([
      ["cavalier", "ESPERANDO OUTRA PESSOA?", null, { chaz: "susto" }],
      ["cavalier", "QUE PENA."],
      ["cavalier", "CADÊ MINHA GUITARRA, BARKLEY?", null, { chaz: "tristeza" }],
      {
        id: "guitarra", quem: "chaz", tempo: 8,
        opcoes: [
          { texto: "AMANHÃ. JURO.", flag: "prometeu_guitarra", exp: { chaz: "explicando" },
            depois: [["cavalier", "VOCÊ DISSE ISSO SEMANA PASSADA."], ["cavalier", "AMANHÃ, BARKLEY. A-MA-NHÃ.", null, { chaz: "alegria" }]] },
          { texto: "TÁ BEM CUIDADA, PROMETO.", flag: "guitarra_cuidada", exp: { chaz: "empolgacao" },
            depois: [["cavalier", "BEM CUIDADA NO SEU QUARTO, NÉ.", null, { chaz: "olhar_de_lado" }], ["cavalier", "O ENSAIO É AMANHÃ. NÃO ATRASA."]] },
        ],
        silencio: [["cavalier", "TÁ. FINGE QUE NÃO TÁ EM CASA.", null, { chaz: "susto" }], ["cavalier", "FALOU, BARKLEY."]],
        flagSilencio: "ignorou_cavalier",
      },
    ], { fora });

    // silêncio... e outra batida, mais leve
    c.expressao("chaz", "curiosidade");
    await c.esperar(1300);
    await this.bater(2, 0.35);
    c.expAtual.riley = "tedio";
    await c.esperar(300);
    await c.falar([
      ["riley", "ATRASADO.", "tedio"],
      ["riley", "DE NOVO."],
      {
        id: "tom", quem: "chaz", tempo: 7,
        opcoes: [
          { texto: "ATRASADO NÃO. ADIANTADO PRA AMANHÃ.", flag: "tom_piada", exp: { chaz: "alegria" }, depois: [["riley", "...NÃO.", "suspiro"]] },
          { texto: "TÔ COM A CABEÇA CHEIA, RILEY.", flag: "chaz_meia_verdade", exp: { chaz: "tristeza" },
            depois: [["riley", "CHEIA DE QUÊ?", "irritacao"], ["chaz", "DEPOIS EU TE CONTO.", "olhar_de_lado"], ["riley", "...TÁ.", "suspiro"]] },
          { texto: "(ESCONDER O CADERNO)", flag: "escondeu_caderno", exp: { chaz: "susto" },
            depois: [["chaz", "NADA! NÃO TEM NADA AQUI!", "susto"], ["riley", "EU NÃO PERGUNTEI NADA, CHAZ.", "mao_na_cara"]] },
        ],
        silencio: [["riley", "OI PRA VOCÊ TAMBÉM.", "irritacao"]],
        flagSilencio: "tom_silencio",
      },
    ]);
    // o caderno fica aberto na escrivaninha, do lado da janela: se o Chaz não escondeu, Riley lê um pedaço
    if (!estado.flags.escondeu_caderno) {
      marcar("riley_viu_letra");
      await c.falar([["riley", "...'ANTES DO SOL VOLTAR'?", "irritacao"], ["chaz", "LETRA NOVA. NÃO TÁ PRONTA.", "olhar_de_lado"], ["riley", "HM.", "tedio"]]);
    }
    await c.falar([["riley", "VEM. O SOL NÃO ESPERA NINGUÉM.", "tedio"]]);
    await c.sair("riley", { para: "direita" });
    await c.esperar(500);
    c.expAtual.chaz = "alegria_olhos_fechados";
    c.corte("chaz");
    await c.esperar(400);
    await c.falar([["chaz", "(TÁ, TÁ. TÔ INDO.)", "alegria"]]);
    await c.fechar();

    this.visitaFeita = true;
    this.emVisita = false;
    this.travado = false;
    this.agendarVida(chaz, this.time.now);
  }

  sairPelaPorta() {
    if (this.saindo) return;
    this.saindo = true;
    this.travado = true;
    this.som("porta_abre", 0.5);
    marcar("prologo_quarto_feito");
    tocarMusica(this, null, 0, 900);
    this.cameras.main.fadeOut(900, 0, 0, 0);
    this.cameras.main.once("camerafadeoutcomplete", () => this.scene.start("Cartela", {
      textos: [
        { texto: "Continua...", fonte: "Patrick Hand", tam: 72, ms: 2400 },
        { texto: "A cidade ainda está sendo construída.", fonte: "Patrick Hand", tam: 44, ms: 2600, cor: "#b9ad9c" },
      ],
      depois: "Titulo",
    }));
  }
}
