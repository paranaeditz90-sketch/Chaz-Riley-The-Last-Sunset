import { CenaJogo, tocarAmbiente, tocarMusica } from "../base.js";
import { Cinema } from "../cinema.js";
import { estado } from "../estado.js";

// Capítulo 1, beat 5: troca -> POV Névoa. Ele acorda no chão da cozinha da casa do seu Amos, com palha nas mãos,
// sem lembrar de ter chegado. A porta da frente aberta. No quarto, o seu Amos (silhueta, mancha, reação; sem gore).
// Escolha E: trancar a porta (com os outros lá fora) ou ligar o gerador (a luz da varanda; barulhento).

const LUAR_COZINHA = 0x8890c0;

export default class Cozinha extends CenaJogo {
  constructor() {
    super("Cozinha");
  }

  config() {
    return { personagens: [{ nome: "nevoa", x: -400, y: 900 }], controla: ["nevoa"], esconder: false, cameraFixa: { x: 960, y: 540 } };
  }

  aoEntrar() {
    this.chars[0].s.setVisible(false);
    this.travado = true;
    this.cine = new Cinema(this);
    tocarMusica(this, null, 0, 800);
    tocarAmbiente(this, "vento_loop", 0.1, 1500);
    this.time.delayedCall(200, () => this.roteiro());
  }

  // cartela da troca de perspectiva: o nome na tinta de quem você agora é
  async cartela(nome, cor) {
    const t = this.add.text(this.scale.width / 2, 540, nome, { fontFamily: '"Caveat Brush", sans-serif', fontSize: "120px", color: cor, stroke: "#000", strokeThickness: 10 })
      .setOrigin(0.5).setScrollFactor(0).setDepth(1e7).setAlpha(0);
    await new Promise((ok) => this.tweens.add({ targets: t, alpha: 1, duration: 500, hold: 1300, yoyo: true, onComplete: () => ok(t.destroy()) }));
  }

  async roteiro() {
    const c = this.cine;
    await this.cartela("NÉVOA", "#8d6f82");
    c.expAtual = { nevoa: "deitado" };

    // ---------------------------------------------------------------- acorda no chão
    await c.abrir(() => {
      c.fundo("cine_cozinha");
      c.entrar("nevoa", null, { x: 0.5, y: 0.99, escala: 1.15 });
      c.tingir(LUAR_COZINHA, 0xa8b4f0);
      c.camera({ z: 1.2, fx: 0.5, fy: 0.75 });
      c.camera({ z: 1.08, fy: 0.62, ms: 6000 });
    }, { fade: 1400 });
    await c.esperar(1600);
    c.expressao("nevoa", "susto");
    c.tremer(0.003, 240);
    await c.falar([
      ["nevoa", "...!", "susto"],
      ["nevoa", "...COZINHA. DE QUEM É ESSA COZINHA.", "nervoso"],
      ["nevoa", "(palha. Nas mãos.)", "susto"],
      ["nevoa", "(de novo não. De novo não.)", "encolhido"],
      ["nevoa", "...EU TAVA NO TRIGO. EU TAVA INDO PRO GERADOR.", "duvida"],
    ]);
    // o vento bate a porta aberta
    this.som("porta_abre", 0.25, 0.7);
    await c.falar([
      ["nevoa", "...A PORTA TÁ ABERTA.", "nervoso"],
      ["nevoa", "SEU AMOS?", "nervoso"],
    ]);
    await c.esperar(1500);

    // ---------------------------------------------------------------- o quarto
    c.corte(() => {
      c.fundo("cine_quarto_amos");
      c.entrar("nevoa", "costas", { x: 0.16, y: 1.08, escala: 1.3 });
      c.tingir(LUAR_COZINHA, 0xa8b4f0);
      c.camera({ z: 1.0, fx: 0.5, fy: 0.55 });
      c.camera({ z: 1.18, fx: 0.42, fy: 0.6, ms: 9000, ease: "Sine.easeIn" });
    });
    tocarAmbiente(this, null, 0, 600);
    await c.esperar(3200); // silêncio. Só a imagem.
    await c.falar([["nevoa", "...SEU AMOS?"]]);
    await c.esperar(1800);
    c.corte(() => {
      c.fundo("cine_cozinha");
      c.entrar("nevoa", "susto", { x: 0.5, escala: 1.25 });
      c.tingir(LUAR_COZINHA, 0xa8b4f0);
      c.camera({ z: 1.1, fx: 0.5, fy: 0.45 });
    });
    await c.falar([
      ["nevoa", "NÃO. NÃO, NÃO, NÃO.", "susto"],
      ["nevoa", "EU NÃO FIZ ISSO.", "choro"],
      ["nevoa", "...EU NÃO... LEMBRO.", "choro"],
    ]);
    await c.esperar(900);

    // ---------------------------------------------------------------- lá fora tem alguma coisa (escolha E)
    this.som("folhas", 0.45, 0.5);
    await c.esperar(600);
    this.som("folhas", 0.5, 0.45);
    c.expressao("nevoa", "nervoso");
    await c.falar([
      ["nevoa", "(tem alguma coisa no terreiro.)", "nervoso"],
      ["nevoa", "(...os outros ainda tão lá fora.)", "nervoso"],
      {
        id: "porta_luz", quem: "nevoa", tempo: 10,
        opcoes: [
          { texto: "TRANCAR A PORTA", flag: "nevoa_trancou", exp: { nevoa: "choro" }, depois: [["nevoa", "...DESCULPA. DESCULPA."]] },
          { texto: "LIGAR O GERADOR (LUZ DA VARANDA)", flag: "luz_varanda", exp: { nevoa: "irritacao" },
            depois: [["nevoa", "SE TIVER LUZ, ELES ACHAM A CASA."], ["nevoa", "...E O QUE MAIS TIVER LÁ FORA TAMBÉM."]] },
        ],
        silencio: [["nevoa", "(...as pernas não mexem.)", "encolhido"]],
        flagSilencio: "nevoa_paralisou",
      },
    ]);
    if (estado.flags.nevoa_trancou) {
      this.som("porta_abre", 0.5, 1.4);
      c.tremer(0.004, 200);
    } else if (estado.flags.luz_varanda) {
      // gerador: barulho, tranco, luz
      c.tremer(0.006, 900);
      this.som("batida_vidro_0", 0.4, 0.5);
      await c.esperar(400);
      c.tingir(0xd8b48a);
    }
    await c.esperar(1200);
    await c.fechar({ fade: 900 });
    this.scene.start("Final");
  }
}
