import Phaser from "phaser";
import { CenaJogo, tocarAmbiente, tocarMusica } from "../base.js";
import { estado, marcar } from "../estado.js";

// Prólogo, cena 1: o quarto do Chaz, fim de tarde. Cenário: imagem gerada pelo diretor (ChatGPT).
// As medidas abaixo estão em pixels da IMAGEM (1672x941); S converte pro jogo (altura 1080).

const S = 1080 / 941;
const P = (x, y) => ({ x: x * S, y: y * S });
const R = (x0, y0, x1, y1) => ({ x: x0 * S, y: y0 * S, w: (x1 - x0) * S, h: (y1 - y0) * S });
const VIDRO = R(712, 58, 1005, 268); // vidro da janela
const NA_JANELA = { x: (VIDRO.x + VIDRO.w / 2), y: 520 }; // âncora dos bilhetes de quem fala lá de fora

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
        R(1275, 300, 1500, 532), // amplificador e violão
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

  aoEntrar() {
    this.lidos = 0;
    this.visitaFeita = false;
    tocarMusica(this, "musica_entardecer", 0.16, 2000);
    tocarAmbiente(this, null, 0, 800);

    const toque = this.sys.game.device.input.touch;
    const dica = this.add.text(48, this.scale.height - 60, toque ? "Chegue perto das coisas e toque em AÇÃO" : "Chegue perto das coisas e aperte E",
      { fontFamily: "Trebuchet MS, sans-serif", fontSize: "34px", color: "#fff3d6", stroke: "#000", strokeThickness: 6 })
      .setOrigin(0, 1).setScrollFactor(0).setDepth(1e7).setAlpha(0);
    this.tweens.add({ targets: dica, alpha: 1, duration: 600, delay: 2600, hold: 6000, yoyo: true });

    const pensa = (...linhas) => linhas.map((l) => ["chaz", l]);
    const contar = () => {
      this.lidos++;
      if (this.lidos >= 3) this.time.delayedCall(1500, () => this.visita());
    };
    const umaVez = (id, primeira, depois) => async () => {
      if (!estado.flags[`quarto_${id}`]) {
        marcar(`quarto_${id}`);
        await this.dizer(primeira());
        contar();
      } else {
        await this.dizer(depois);
      }
    };

    this.interativo({
      id: "caderno", ...P(930, 470), raio: 190,
      acao: umaVez("caderno", () => {
        marcar("leu_letra");
        return pensa("(A MÚSICA.)", "'SE EU FOR ANTES DO SOL VOLTAR, / NÃO ME PROCURA NO MORRO.'", "(FALTA O ÚLTIMO VERSO. SEMPRE FALTA.)",
          "(...RIMA COM 'MORRO'. 'SOCORRO'. NÃO.)");
      }, pensa("(DEPOIS EU TERMINO. DEPOIS.)")),
    });
    this.interativo({
      id: "violao", ...P(1390, 485), raio: 180,
      acao: umaVez("violao", () => pensa("(O VIOLÃO NEM É MEU.)", "(TÁ COMIGO HÁ TRÊS MESES. EM MINHA DEFESA, ELE GOSTA MAIS DE MIM.)"),
        pensa("(UM DIA EU DEVOLVO. UM DIA.)")),
    });
    this.interativo({
      id: "cama", ...P(455, 560), raio: 180,
      acao: async () => {
        if (estado.flags.quarto_cama) return this.dizer(pensa("(AINDA TÁ LÁ. EMBAIXO DO COLCHÃO.)"));
        marcar("quarto_cama");
        await this.dizer([
          ...pensa("(EMBAIXO DO COLCHÃO.)", "'...TEMOS A ALEGRIA DE INFORMAR QUE VOCÊ FOI ACEITO NO CONSERVATÓRIO...'",
            "(TRÊS SEMANAS. E EU AINDA NÃO CONTEI PRA NINGUÉM.)"),
          {
            id: "carta", quem: "chaz",
            opcoes: [
              { texto: "GUARDAR DE VOLTA", flag: "carta_escondida", depois: pensa("(DEPOIS. DEPOIS EU VEJO ISSO.)") },
              { texto: "LEVAR NO BOLSO", flag: "carta_no_bolso", depois: pensa("(VAI QUE HOJE EU TENHO CORAGEM.)") },
            ],
          },
        ]);
        contar();
      },
    });
    this.interativo({
      id: "janela", ...P(730, 470), raio: 170,
      acao: umaVez("janela", () => pensa("(O CÉU TÁ BONITO DEMAIS HOJE.)", "(PARECE CENÁRIO.)"), pensa("(LARANJA DEMAIS. ESQUISITO.)")),
    });
    this.interativo({
      id: "discos", ...P(1300, 645), raio: 170,
      acao: umaVez("discos", () => pensa("(SE EU COLOCAR UM DISCO AGORA, NÃO SAIO MAIS DAQUI.)"), pensa("(NÃO. FOCO.)")),
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

    this.time.delayedCall(1200, () => this.dizer(pensa("(SÓ MAIS UM MINUTO. DOIS. NO MÁXIMO TRÊS.)")));
    // se ninguém mexer em nada, a visita chega mesmo assim
    this.time.delayedCall(50000, () => this.visita());
  }

  // ---------------------------------------------------------------- batem na janela
  async visita() {
    if (this.visitaFeita || this.emVisita) return;
    if (this.dialogo.ativo || this.travado) {
      this.time.delayedCall(800, () => this.visita());
      return;
    }
    this.emVisita = true;
    this.travado = true;
    const chaz = this.chars[0];
    const bater = async (n, vol) => {
      for (let i = 0; i < n; i++) {
        this.som(`batida_vidro_${i % 3}`, vol, Phaser.Math.FloatBetween(0.95, 1.05));
        await this.esperar(260);
      }
    };
    await bater(3, 0.6);
    await this.esperar(400);
    // vai até a janela (entre o criado-mudo e a escrivaninha)
    const frente = P(728, 545);
    await this.andarAte(chaz, chaz.s.x, Math.max(chaz.s.y, 600 * S));
    await this.andarAte(chaz, frente.x, frente.y);
    this.virar(chaz, "costas");
    await this.esperar(400);

    const fora = { cavalier: NA_JANELA };
    await this.dizer([
      ["cavalier", "ESPERANDO OUTRA PESSOA?"],
      ["cavalier", "QUE PENA."],
      ["cavalier", "CADÊ MEU VIOLÃO, BARKLEY?"],
      {
        id: "violao", quem: "chaz", tempo: 8,
        opcoes: [
          { texto: "AMANHÃ. JURO.", flag: "prometeu_violao", depois: [["cavalier", "VOCÊ DISSE ISSO SEMANA PASSADA."], ["cavalier", "ANOTA AÍ, BARKLEY: AMANHÃ."]] },
          { texto: "TÁ BEM CUIDADO, PROMETO.", flag: "violao_cuidado", depois: [["cavalier", "TÁ BEM CUIDADO NO SEU QUARTO, NÉ."], ["cavalier", "O ENSAIO É AMANHÃ. NÃO ATRASA."]] },
        ],
        silencio: [["cavalier", "TÁ. FINGE QUE NÃO TÁ EM CASA."], ["cavalier", "ANOTA AÍ, BARKLEY."]],
        flagSilencio: "ignorou_cavalier",
      },
    ], fora);

    await this.esperar(1400);
    await bater(2, 0.35);
    // Riley aparece na janela (só o que o vidro deixa ver)
    const riley = this.add.sprite(NA_JANELA.x, VIDRO.y + VIDRO.h + 75, "riley", this.anim({ nome: "riley" }, "frente_parado").frames[0])
      .setOrigin(0.5, this.meta.originY).setScale(0.85).setAlpha(0).setDepth(-5e5);
    const masc = this.make.graphics({ x: 0, y: 0 }, false);
    masc.fillRect(VIDRO.x, VIDRO.y, VIDRO.w, VIDRO.h);
    riley.setMask(masc.createGeometryMask());
    this.tweens.add({ targets: riley, alpha: 1, y: riley.y - 12, duration: 500 });
    await this.esperar(600);

    const falaRiley = { riley: NA_JANELA };
    await this.dizer([
      ["riley", "ATRASADO."],
      ["riley", "DE NOVO."],
      {
        id: "tom", quem: "chaz", tempo: 7,
        opcoes: [
          { texto: "ATRASADO NÃO. ADIANTADO PRA AMANHÃ.", flag: "tom_piada", depois: [["riley", "...NÃO."]] },
          { texto: "TÔ COM A CABEÇA CHEIA, RILEY.", flag: "chaz_meia_verdade", depois: [["riley", "CHEIA DE QUÊ?"], ["chaz", "DEPOIS EU TE CONTO."], ["riley", "...TÁ."]] },
          { texto: "(ESCONDER O CADERNO)", flag: "escondeu_caderno", depois: [["chaz", "NADA! NÃO TEM NADA AQUI!"], ["riley", "EU NÃO PERGUNTEI NADA, CHAZ."]] },
        ],
        silencio: [["riley", "OI PRA VOCÊ TAMBÉM."]],
        flagSilencio: "tom_silencio",
      },
    ], falaRiley);
    if (estado.flags.leu_letra && !estado.flags.escondeu_caderno) {
      marcar("riley_viu_letra");
      await this.dizer([["riley", "...'ANTES DO SOL VOLTAR'?"], ["chaz", "LETRA NOVA. NÃO TÁ PRONTA."], ["riley", "HM."]], falaRiley);
    }
    await this.dizer([["riley", "VEM. O SOL NÃO ESPERA NINGUÉM."]], falaRiley);
    this.tweens.add({ targets: riley, alpha: 0, y: riley.y + 20, duration: 500, onComplete: () => riley.destroy() });
    await this.esperar(500);
    await this.dizer([["chaz", "(TÁ, TÁ. TÔ INDO.)"]]);

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

