import { CenaJogo, tocarAmbiente, tocarMusica } from "../base.js";
import { Cinema } from "../cinema.js";
import { estado } from "../estado.js";

// Prólogo, cena 2: saindo de casa e indo buscar o Névoa. Por enquanto só cutscene (fundos provisórios
// desfocados); a caminhada pela rua com os moradores entra quando chegar a arte da rua e dos moradores.

export default class Rua extends CenaJogo {
  constructor() {
    super("Rua");
  }

  config() {
    // ninguém anda aqui ainda: o Chaz existe (a base precisa de alguém) mas fica fora de quadro
    return { personagens: [{ nome: "chaz", x: -400, y: 900 }], controla: ["chaz"], esconder: false, cameraFixa: { x: 960, y: 540 } };
  }

  aoEntrar() {
    this.chars[0].s.setVisible(false);
    this.travado = true;
    this.cine = new Cinema(this);
    tocarMusica(this, "musica_entardecer", 0.22, 1500);
    tocarAmbiente(this, "vento_loop", 0.14, 1500);
    this.time.delayedCall(300, () => this.roteiro());
  }

  async roteiro() {
    const c = this.cine;
    const f = estado.flags;

    // ---------------------------------------------------------------- 1. na frente de casa
    c.planos = {};
    c.expAtual = { chaz: "empolgacao", riley: "tedio" };
    await c.abrir(() => {
      c.fundo("cine_rua_tarde");
      c.poeira(18);
      c.entrar("chaz", null, { x: 0.3, escala: 1.08 });
      c.entrar("riley", null, { x: 0.7, escala: 1.08 });
      c.camera({ z: 1.0, fx: 0.5, fy: 0.55 });
      c.camera({ z: 1.06, ms: 14000 });
    });
    await c.esperar(400);
    await c.falar([
      ["chaz", "TÔ AQUI! TÔ AQUI. RESPIRANDO E TUDO.", "empolgacao"],
      ...(f.tom_silencio
        ? [["riley", "AH. AGORA VOCÊ FALA.", "irritacao"]]
        : [["riley", "QUARENTA MINUTOS, CHAZ.", "tedio"]]),
      ["chaz", "QUALIDADE LEVA TEMPO.", "explicando"],
    ]);
    // a carta no bolso aparece (o jogador decidiu levar)
    if (f.carta_no_bolso) {
      await c.falar([
        ["riley", "QUE QUE TEM NO SEU BOLSO?", "irritacao", { chaz: "susto" }],
        {
          id: "bolso", quem: "chaz", tempo: 7,
          opcoes: [
            { texto: "NADA. PALHETA.", flag: "mentiu_bolso", exp: { chaz: "olhar_de_lado" }, depois: [["riley", "...TÁ.", "suspiro"]] },
            { texto: "DEPOIS EU TE MOSTRO.", flag: "chaz_quase_contou", exp: { chaz: "olhar_de_lado" },
              depois: [["riley", "VOCÊ VIVE DIZENDO 'DEPOIS'.", "tedio"], ["chaz", "E SEMPRE CUMPRO! ÀS VEZES.", "alegria"]] },
          ],
          silencio: [["riley", "TÁ BOM. GUARDA SEU SEGREDINHO.", "defensiva"]],
          flagSilencio: "calou_bolso",
        },
      ]);
    }
    await c.falar([
      ["chaz", "BORA PEGAR O NÉVOA NO CAMINHO.", "alegria"],
      ["riley", "ELE NUNCA OLHA PRA GENTE QUANDO FALA.", "irritacao"],
      ["chaz", "ELE É TÍMIDO. VOCÊ TAMBÉM É.", "olhar_de_lado"],
      ["riley", "NÃO SOU.", "irritacao"],
      ["chaz", "CLARO QUE NÃO.", "alegria_olhos_fechados"],
    ]);
    await c.fechar({ fade: 700 });

    // ---------------------------------------------------------------- 2. varanda do Vô Tobias
    c.expAtual = { chaz: "curiosidade", riley: "tedio", nevoa: "dormindo" };
    await c.abrir(() => {
      c.fundo("cine_varanda");
      c.poeira(12);
      c.entrar("chaz", null, { x: 0.34, escala: 1.0 });
      c.entrar("nevoa", null, { x: 0.6, y: 0.86, escala: 1.0 });
      c.entrar("riley", null, { x: 0.86, escala: 1.0 });
      c.camera({ z: 1.0, fx: 0.5, fy: 0.55 });
      c.camera({ z: 1.05, ms: 16000 });
    }, { fade: 700 });
    await c.esperar(700);
    // o Vô Tobias fala de dentro da casa, da porta de tela (fora do quadro, à esquerda)
    const fora = { fora: { tobias: "esquerda" } };
    await c.falar([
      ["chaz", "ELE TÁ... DORMINDO?", "curiosidade"],
      ["tobias", "TÁ. FINALMENTE.", null, { chaz: "susto", riley: "irritacao" }],
      ["tobias", "TRÊS DIAS.", null, { chaz: "tristeza" }],
      ["chaz", "TRÊS DIAS SEM DORMIR, VÔ TOBIAS?", "tristeza"],
      ["tobias", "ACORDA ELE DEVAGAR, MENINO. ELE ACORDA ASSUSTADO."],
      {
        id: "acordar_nevoa", quem: "chaz", tempo: 8,
        opcoes: [
          { texto: "CHAMAR BAIXINHO", flag: "acordou_devagar", exp: { chaz: "tristeza" }, depois: [["chaz", "NÉVOA... Ô, NÉVOA. O PÔR DO SOL.", "tristeza"]] },
          { texto: "MEXER NA ORELHA DELE", flag: "acordou_orelha", exp: { chaz: "empolgacao" }, depois: [["chaz", "SÓ UMA ORELHADINHA...", "empolgacao"]] },
        ],
        silencio: [["riley", "NÉVOA. ACORDA.", "tedio"]],
        flagSilencio: "riley_acordou_nevoa",
      },
    ], fora);
    // acorda assustado
    c.expressao("nevoa", "susto");
    c.tremer(0.004, 260);
    await c.esperar(500);
    await c.falar([
      ["nevoa", "...!", "susto", { chaz: "susto" }],
      ["nevoa", "EU... TAVA... ONDE...?", "nervoso"],
      ["chaz", "NA SUA VARANDA. TUDO BEM?", "curiosidade"],
      ["nevoa", "...TUDO. SÓ... SONHO RUIM.", "encolhido"],
      ["tobias", "TÁ COM CHEIRO DE PALHA DE NOVO, MENINO.", null, { nevoa: "nervoso" }],
      ["nevoa", "...DEVE SER DO MORRO.", "nervoso", { chaz: "curiosidade" }],
      ["riley", "A GENTE NEM FOI PRO MORRO AINDA.", "irritacao"],
      // o Névoa fala sem encarar ninguém (olhar pra baixo), como a Riley reclamou lá atrás
      ["nevoa", "...EU FUI ONTEM.", "sono", { riley: "irritacao" }],
      ["chaz", "BORA! O SOL NÃO ESPERA NINGUÉM.", "aceno", { nevoa: "sono" }],
      ["riley", "ESSA FALA É MINHA.", "tedio"],
    ], fora);
    await c.esperar(400);
    await c.fechar({ fade: 900 });
    this.fim();
  }

  fim() {
    this.scene.start("Morro");
  }
}
